"""Check that your environment is ready before you build the agent (guide Step 2).

Runs four checks in the order things usually break, and points at the guide step that
fixes each one:

  1. .env is filled in and the endpoint looks like a project endpoint
  2. the Python packages are installed
  3. you are signed in with `az login` and a credential can be obtained
  4. the Foundry project answers, which means your role assignment works

Usage:  python scripts/check_setup.py
"""
import os
import re
import sys

from _setup import ROOT  # noqa: F401  (sets up imports and .env)

# Plain ASCII markers: this script runs on Windows terminals too, where the default
# code page cannot encode tick and arrow characters.
OK = "  [ ok ]"
BAD = "  [FAIL]"
INFO = "        "

ENDPOINT_PATTERN = re.compile(
    r"^https://[a-z0-9-]+\.services\.ai\.azure\.com/api/projects/[A-Za-z0-9_-]+/?$"
)

failures: list[str] = []


def fail(message: str, fix: str) -> None:
    print(f"{BAD} {message}")
    print(f"{INFO}Fix: {fix}")
    failures.append(message)


def check_env() -> bool:
    print("\n1. Your settings in .env")

    if not (ROOT / ".env").exists():
        fail(
            ".env does not exist",
            "Run: cp .env.sample .env   then fill in your values (guide Step 2, section 3)",
        )
        return False

    endpoint = (os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or "").strip()
    if not endpoint:
        fail("FOUNDRY_PROJECT_ENDPOINT is empty", "Set it in .env (guide Step 2, section 3)")
        return False
    if "<" in endpoint or ">" in endpoint:
        fail(
            "FOUNDRY_PROJECT_ENDPOINT still holds the placeholder text",
            "Replace it with your own endpoint from the Foundry portal (guide Step 1, section 5)",
        )
        return False
    if not ENDPOINT_PATTERN.match(endpoint):
        fail(
            f"FOUNDRY_PROJECT_ENDPOINT does not look like a project endpoint:\n{INFO}   {endpoint}",
            "It should look like https://<resource>.services.ai.azure.com/api/projects/<project>. "
            "Copy it from your project's Overview page (guide Step 1, section 5)",
        )
        return False
    print(f"{OK} endpoint: {endpoint}")

    model = (os.environ.get("MODEL_DEPLOYMENT_NAME") or "").strip()
    if not model or "<" in model:
        fail(
            "MODEL_DEPLOYMENT_NAME is not set",
            "Set it to your model deployment name, for example gpt-4.1-mini (guide Step 1, section 4)",
        )
        return False
    print(f"{OK} model deployment: {model}")
    print(f"{OK} agent name: {os.environ.get('FOUNDRY_AGENT_NAME', 'call-qa-reviewer')}")
    return True


def check_packages() -> bool:
    print("\n2. Python packages")
    try:
        import azure.ai.projects  # noqa: F401
        import azure.identity  # noqa: F401
        import openai  # noqa: F401
    except ImportError as exc:
        fail(
            f"a package is missing ({exc.name})",
            "Run: pip install -r requirements.txt -r api/requirements.txt",
        )
        return False
    print(f"{OK} azure-ai-projects, azure-identity and openai are installed")
    return True


def check_sign_in() -> bool:
    print("\n3. Your Azure sign-in")
    from azure.core.exceptions import ClientAuthenticationError
    from azure.identity import DefaultAzureCredential

    try:
        credential = DefaultAzureCredential()
        credential.get_token("https://management.azure.com/.default")
    except ClientAuthenticationError:
        fail(
            "could not get an Azure token",
            "Run: az login --use-device-code   (guide Step 2, section 4)",
        )
        return False
    except Exception as exc:  # noqa: BLE001 - surface anything unexpected in plain words
        fail(f"sign-in check failed: {type(exc).__name__}: {exc}", "Try: az login --use-device-code")
        return False
    print(f"{OK} signed in, and a token was issued")
    return True


def check_project() -> bool:
    print("\n4. Access to your Foundry project")
    from qa_agent.client import get_openai_client

    try:
        # Listing vector stores is a cheap call that exercises the data plane, which is
        # what the Azure AI User role actually grants. create_agent.py uses the same call.
        for _ in get_openai_client().vector_stores.list():
            break
    except Exception as exc:  # noqa: BLE001 - the message is the useful part for a beginner
        text = f"{type(exc).__name__}: {exc}"
        lowered = text.lower()
        if "403" in text or "forbidden" in lowered or "permissiondenied" in lowered.replace(" ", ""):
            fail(
                "the project refused the request (403)",
                "You are missing the Azure AI User role on the Foundry resource. "
                "See guide Step 1, section 6. Role changes can take a minute to apply",
            )
        elif "401" in text or "unauthorized" in lowered:
            fail(
                "the project rejected your sign-in (401)",
                "Run az login --use-device-code with the same account you granted the role to",
            )
        elif "404" in text or "not found" in lowered:
            fail(
                "the project was not found (404)",
                "Check FOUNDRY_PROJECT_ENDPOINT in .env. The project name at the end must match "
                "the project in the Foundry portal (guide Step 1, section 5)",
            )
        else:
            fail(f"could not reach the project: {text}", "Check your endpoint and your sign-in")
        return False
    print(f"{OK} the project answered, so your role assignment works")
    return True


def main() -> int:
    print("Checking your workshop environment")
    print("=" * 38)

    if check_env() and check_packages() and check_sign_in():
        check_project()

    print("\n" + "=" * 38)
    if failures:
        print(f"{len(failures)} check(s) failed. Fix the first one and run this again:")
        print("  python scripts/check_setup.py")
        return 1

    print("Everything is ready. On to Step 3: create your first agent.")
    print("  python scripts/create_agent.py --stage 1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
