"""POST /api/chat  {"message": "...", "conversationId": "optional"}
Returns {"conversationId", "reply", "trace"}."""
import json
import logging

import azure.functions as func

from ..qa_agent.runner import new_conversation, run_turn

MAX_MESSAGE_CHARS = 4000


def _json(body: dict, status: int = 200) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(body, ensure_ascii=False), status_code=status,
                             mimetype="application/json")


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return _json({"error": "Send a JSON body with a 'message' field."}, 400)

    message = str(body.get("message") or "").strip()
    if not message:
        return _json({"error": "The message is empty."}, 400)
    if len(message) > MAX_MESSAGE_CHARS:
        return _json({"error": f"Keep messages under {MAX_MESSAGE_CHARS} characters."}, 400)

    try:
        conversation_id = body.get("conversationId") or new_conversation()
        result = run_turn(conversation_id, message)
    except Exception as exc:  # Workshop-friendly error: show the cause so attendees can fix setup issues.
        logging.exception("Agent call failed")
        return _json({"error": f"{type(exc).__name__}: {str(exc)[:300]}"}, 502)

    return _json({"conversationId": conversation_id, **result})
