"""Runs one conversation turn with the agent, executing any function calls it requests."""
import json

from . import tools
from .client import agent_name, get_openai_client

MAX_TOOL_ROUNDS = 10


def _agent_ref() -> dict:
    return {"agent_reference": {"name": agent_name(), "type": "agent_reference"}}


def new_conversation() -> str:
    return get_openai_client().conversations.create().id


def _record_builtin_tools(response, trace: list) -> None:
    """Built-in tools such as file search run inside Foundry; we only log that they happened."""
    for item in response.output:
        if item.type == "file_search_call":
            trace.append({
                "type": "file_search",
                "name": "file_search",
                "arguments": {"queries": list(getattr(item, "queries", None) or [])},
                "result": None,
            })


def run_turn(conversation_id: str, user_text: str) -> dict:
    """Send a message, run the tool loop, and return the reply plus a trace of what the agent did."""
    openai = get_openai_client()
    trace: list = []

    response = openai.responses.create(
        input=user_text,
        conversation=conversation_id,
        extra_body=_agent_ref(),
    )

    finished = False
    for _ in range(MAX_TOOL_ROUNDS):
        _record_builtin_tools(response, trace)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            finished = True
            break

        outputs = []
        for call in calls:
            try:
                args = json.loads(call.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = tools.dispatch(call.name, args)
            trace.append({"type": "function", "name": call.name, "arguments": args, "result": result})
            outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })

        # Return every function result in one request so the agent can continue.
        response = openai.responses.create(
            input=outputs,
            conversation=conversation_id,
            extra_body=_agent_ref(),
        )

    reply = response.output_text or ""
    if not finished:
        reply = (reply + "\n\n" if reply else "") + (
            f"(Stopped after {MAX_TOOL_ROUNDS} rounds of tool calls. Try a narrower request.)"
        )
    return {"reply": reply, "trace": trace}
