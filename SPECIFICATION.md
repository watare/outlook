# Spécification détaillée – Agent IA de Messagerie (Email AI Agent)

## 1. Contexte et Objectif

L'**Agent IA de messagerie** a pour objectif d'automatiser la gestion des emails entrants sur une boîte Outlook via Microsoft Graph. Il lit les nouveaux messages, analyse le contenu avec un modèle IA (par ex. GPT-4) et déclenche des actions : réponses automatiques, extractions de données, création de tickets, etc. L'agent tourne en continu dans un conteneur Docker exposé sur `agentmail.padaw.ovh` via un proxy nginx et Let's Encrypt.

## 2. Architecture Générale

- **Application Azure AD** : fournit les identifiants OAuth2 pour accéder à Microsoft Graph (permissions Mail.Read, Mail.Send...).
  - Le domaine `outlook.padaw.ovh` est autorisé pour l'authentification OAuth.
  - Les droits configurés incluent `Files.ReadWrite.AppFolder` et `User.Read` en mode délégué.
- **Service Python** : exécute le traitement des emails et expose un endpoint HTTP (webhook) pour recevoir les notifications Graph.
- **Infrastructure Docker/Nginx** : containerisé, rattaché au réseau `nginx-proxy` pour bénéficier du reverse-proxy automatique et du certificat TLS.

## 3. Fonctionnement

1. Obtention d'un jeton d'accès via MSAL avec le flux client credentials.
2. Création d'un abonnement Graph (`/subscriptions`) pour recevoir les notifications de nouveaux emails sur la boîte ciblée.
3. Réception d'une notification `POST` sur le webhook `https://agentmail.padaw.ovh/graph/notifications`. Vérification du `clientState`.
4. Récupération du message complet via `GET /users/{userId}/messages/{messageId}`.
5. Analyse du contenu via le module IA (classification, résumé, suggestions de réponse...).
6. Action adaptée : marquer le mail comme lu, déplacer dans un dossier, envoyer une réponse via Graph (`/sendMail`), créer un ticket interne, etc.
7. Renouvellement automatique de l'abonnement avant expiration (max 3 jours). Gestion des erreurs : logs, nouvelle tentative, re-création de l'abonnement.

## 4. Déploiement Docker

Exemple de `Dockerfile` :

```Dockerfile
FROM python:3.11-slim
RUN pip install msal requests fastapi uvicorn[standard] openai
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "agentmail:app", "--host", "0.0.0.0", "--port", "8000"]
```

Variables d'environnement clés : `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`, `MAILBOX_USER_ID`, `OPENAI_API_KEY`, `VIRTUAL_HOST=agentmail.padaw.ovh`, `LETSENCRYPT_HOST=agentmail.padaw.ovh`, `LETSENCRYPT_EMAIL`.

Le container rejoint le réseau `nginx-proxy` et expose le port 8000. Nginx se charge du TLS et du routage vers le webhook.

## 5. Sécurité

- Stockage des secrets via variables d'environnement ou service de secrets.
- Permissions minimales accordées à l'application Azure.
- Vérification du `clientState` pour chaque notification afin d'éviter les appels frauduleux.
- Journalisation soignée sans exposer de données sensibles.

## 6. Tests

- Vérifier l'obtention du jeton Graph et la création réussie de l'abonnement.
- Envoyer des emails de test et confirmer la réception des notifications, la récupération du message et le traitement IA.
- Tester le renouvellement de l'abonnement et la gestion des interruptions réseau ou erreurs d'authentification.

## 7. Améliorations potentielles

- Interface d'administration pour visualiser les emails traités.
- Intégration d'une base de connaissances pour affiner les réponses.
- Analyse des pièces jointes (PDF, images) via OCR ou autres outils.

Cette spécification servira de base pour développer l'agent IA de messagerie déployé sur `agentmail.padaw.ovh`.
