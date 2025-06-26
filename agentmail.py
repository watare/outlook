import logging
import os
from typing import Dict

import msal
import openai
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

app = FastAPI()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
MAILBOX_USER_ID = os.getenv("MAILBOX_USER_ID")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if OPENROUTER_API_KEY:
    openai.api_key = OPENROUTER_API_KEY
    openai.api_base = OPENROUTER_BASE_URL


def get_access_token() -> str:
    """Acquire a token from Microsoft identity platform."""
    client = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    result = client.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"Token acquisition failed: {result.get('error_description')}")
    return result["access_token"]


def analyze_message(content: str) -> str:
    """Analyze email content using OpenAI."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message["content"]


@app.post("/graph/notifications")
async def graph_notifications(request: Request) -> Dict[str, str]:
    payload = await request.json()
    if "value" not in payload:
        raise HTTPException(status_code=400, detail="Invalid notification payload")

    for note in payload["value"]:
        message_id = note.get("resourceData", {}).get("id")
        if not message_id:
            continue
        token = get_access_token()
        msg = requests.get(
            f"https://graph.microsoft.com/v1.0/users/{MAILBOX_USER_ID}/messages/{message_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        ).json()
        content = msg.get("body", {}).get("content", "")
        summary = analyze_message(content)
        logging.info("Message %s summary: %s", message_id, summary)

    return {"status": "ok"}
