"""GET /api/calls  Returns the sample calls shown in the web app's call list."""
import json

import azure.functions as func

from ..qa_agent.tools import list_calls


def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(list_calls("all"), ensure_ascii=False), mimetype="application/json")
