"""Create (or update) the Call QA Reviewer agent in AI Foundry.

Each run creates a new version of the same agent. Use --stage to follow the labs:
  --stage 1   instructions only                     (Lab 1)
  --stage 2   + knowledge files via file search     (Lab 2)
  --stage 3   + function tools                      (Lab 3, default)
"""
import argparse

from _setup import ROOT  # noqa: F401  (sets up imports and .env)
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition

from qa_agent.client import agent_name, get_openai_client, get_project_client, model_deployment
from qa_agent.tools import function_tools

VECTOR_STORE_NAME = "call-qa-knowledge"


def ensure_vector_store(refresh: bool) -> str:
    """Upload the files in knowledge/ to a vector store, reusing it if it already exists."""
    openai = get_openai_client()
    for store in openai.vector_stores.list():
        if store.name == VECTOR_STORE_NAME:
            if not refresh:
                print(f"Reusing vector store {store.id}")
                return store.id
            openai.vector_stores.delete(vector_store_id=store.id)
            print(f"Deleted old vector store {store.id}")
            break

    store = openai.vector_stores.create(name=VECTOR_STORE_NAME)
    for path in sorted((ROOT / "knowledge").glob("*.md")):
        with open(path, "rb") as fh:
            openai.vector_stores.files.upload_and_poll(vector_store_id=store.id, file=fh)
        print(f"  uploaded {path.name}")
    print(f"Created vector store {store.id}")
    return store.id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", type=int, choices=[1, 2, 3], default=3)
    parser.add_argument("--refresh-knowledge", action="store_true",
                        help="Re-upload the knowledge files after you edit them.")
    args = parser.parse_args()

    instructions = (ROOT / "api" / "qa_agent" / "instructions.md").read_text(encoding="utf-8")
    tools = []
    if args.stage >= 2:
        tools.append(FileSearchTool(vector_store_ids=[ensure_vector_store(args.refresh_knowledge)]))
    if args.stage >= 3:
        tools.extend(function_tools())

    definition = PromptAgentDefinition(model=model_deployment(), instructions=instructions, tools=tools or None)
    agent = get_project_client().agents.create_version(
        agent_name=agent_name(),
        definition=definition,
        description="Reviews recorded contact-center calls for QA and compliance (workshop sample).",
    )
    print(f"Agent ready: name={agent.name} version={agent.version} stage={args.stage} tools={len(tools)}")


if __name__ == "__main__":
    main()
