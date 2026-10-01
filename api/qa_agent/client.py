"""Creates the AI Foundry clients used by the scripts and the web API."""
import os
from functools import lru_cache

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def agent_name() -> str:
    return os.environ.get("FOUNDRY_AGENT_NAME", "call-qa-reviewer")


def model_deployment() -> str:
    return os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")


@lru_cache(maxsize=1)
def get_project_client() -> AIProjectClient:
    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
    if not endpoint:
        raise RuntimeError(
            "FOUNDRY_PROJECT_ENDPOINT is not set. For scripts, copy .env.sample to .env. "
            "For the web app, copy api/local.settings.sample.json to api/local.settings.json."
        )
    # Locally this uses your `az login` session. In Azure it uses the
    # service principal settings (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET).
    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())


@lru_cache(maxsize=1)
def get_openai_client():
    """An OpenAI-compatible client for conversations, responses and vector stores."""
    return get_project_client().get_openai_client()
