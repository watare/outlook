# Outlook AI Agent

This project implements a simple email agent that interacts with Microsoft Graph and processes messages with OpenAI via the OpenRouter gateway.

## Requirements

- Python 3.11
- Dependencies listed in `requirements.txt`

## Quick start

Install dependencies and run tests (a Python 3.11 environment is assumed):

```bash
pip install -r requirements.txt
pytest
```

Run the application:

```bash
uvicorn agentmail:app --reload --host 0.0.0.0 --port 8000
```

The application loads configuration from a `.env` file. Copy `.env.example` to
`.env` and fill in your credentials. The required variables are:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_SECRET`
- `MAILBOX_USER_ID`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL` *(optional, defaults to `https://openrouter.ai/api/v1`)*
These values are used to authenticate to Microsoft Graph and the OpenRouter API.

### Using a proxy

If you run the agent behind an HTTP proxy, set the `HTTP_PROXY` and
`HTTPS_PROXY` environment variables before starting the application so that the
underlying libraries can route traffic correctly.

### Docker deployment

The repository includes a simple `Dockerfile` to run the service in a container.
Build the image and run it:

```bash
docker build -t agentmail .
docker run --env-file .env -p 8000:8000 agentmail
```

When run in Docker the container can join an existing network such as
`nginx-proxy` to be served behind a reverse proxy.
