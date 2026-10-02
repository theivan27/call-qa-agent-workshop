"""Function tools the agent can call, backed by fictional sample data.

In a real deployment these would call your contact-center platform, QA system and
case-management tools. Here they read calls from data/calls.json and keep anything
the agent writes (scores, flags, coaching tasks) in memory.
"""
import itertools
import json
import re
from pathlib import Path

from . import speech

DATA_FILE = Path(__file__).parent / "data" / "calls.json"

SCORE_MAX = {"opening": 15, "verification": 20, "empathy": 20, "resolution": 25, "compliance": 20}
RULE_IDS = ["CC-01", "CC-02", "CC-03", "CC-04", "CC-05", "CC-06", "CC-07"]

# In-memory "systems of record" for the workshop. They reset when the app restarts.
QA_SCORES: dict = {}
COMPLIANCE_FLAGS: list = []
COACHING_TASKS: list = []
_ids = itertools.count(1001)

_NUMBER = re.compile(r"\b(?:\d[ -]?){8,19}\b")


def _mask(text: str) -> str:
    """Guardrail in code: never hand full account or card numbers to the model."""
    def repl(match: re.Match) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        return f"[number ending {digits[-4:]}]"
    return _NUMBER.sub(repl, text)


def _calls() -> list:
    with open(DATA_FILE, encoding="utf-8") as fh:
        return json.load(fh)["calls"]


def _find(call_id: str):
    return next((c for c in _calls() if c["call_id"].lower() == call_id.strip().lower()), None)


# ---------- Tool implementations ----------

def list_calls(campaign: str = "all") -> dict:
    calls = [c for c in _calls() if campaign == "all" or c["campaign"] == campaign]
    return {"calls": [
        {k: c[k] for k in ("call_id", "date", "campaign", "agent_id", "agent_name", "language", "duration_min")}
        for c in calls
    ]}


def get_transcript(call_id: str) -> dict:
    call = _find(call_id)
    if not call:
        return {"error": f"No call found with id {call_id}. Use list_calls to see valid ids."}
    return {
        "call_id": call["call_id"],
        "agent_id": call["agent_id"],
        "agent_name": call["agent_name"],
        "campaign": call["campaign"],
        "date": call["date"],
        "language": call["language"],
        "transcript": [{"speaker": t["speaker"], "text": _mask(t["text"])} for t in call["transcript"]],
    }


def transcribe_call(call_id: str) -> dict:
    """Transcribe the recording with Azure AI Speech. This is where a review starts."""
    call = _find(call_id)
    if not call:
        return {"error": f"No call found with id {call_id}. Use list_calls to see valid ids."}
    try:
        result = speech.transcribe(call["call_id"])
    except speech.TranscriptionError as exc:
        # Hand the reason back to the agent so it can say what went wrong and fall back.
        return {
            "error": str(exc),
            "call_id": call["call_id"],
            "fallback": "Call get_transcript for the stored reference transcript instead, "
                        "and say in your report that you reviewed text rather than audio.",
        }
    return {
        "call_id": result["call_id"],
        "agent_id": call["agent_id"],
        "agent_name": call["agent_name"],
        "campaign": call["campaign"],
        "date": call["date"],
        "source": result["source"],
        "duration_seconds": result["duration_seconds"],
        "speaker_mapping": result["speaker_mapping"],
        "transcript": [
            {"speaker": t["speaker"], "at": t["at"], "text": _mask(t["text"])}
            for t in result["transcript"]
        ],
    }


def log_qa_score(call_id: str, scores: dict, total: int, summary: str) -> dict:
    if not _find(call_id):
        return {"error": f"No call found with id {call_id}."}
    for key, maximum in SCORE_MAX.items():
        value = scores.get(key)
        if not isinstance(value, int) or not 0 <= value <= maximum:
            return {"error": f"Score '{key}' must be a whole number from 0 to {maximum}."}
    if total != sum(scores[k] for k in SCORE_MAX):
        return {"error": "Total must equal the sum of the five criteria. Recalculate and try again."}
    record_id = f"QA-{next(_ids)}"
    QA_SCORES[call_id.upper()] = {"record_id": record_id, "scores": scores, "total": total, "summary": summary}
    return {"status": "logged", "record_id": record_id, "call_id": call_id.upper(), "total": total,
            "result": "pass" if total >= 80 else "below target"}


def flag_compliance_issue(call_id: str, rule_id: str, excerpt: str, severity: str) -> dict:
    if not _find(call_id):
        return {"error": f"No call found with id {call_id}."}
    if rule_id not in RULE_IDS:
        return {"error": f"Unknown rule {rule_id}. Valid rules: {', '.join(RULE_IDS)}."}
    ticket_id = f"CMP-{next(_ids)}"
    COMPLIANCE_FLAGS.append({"ticket_id": ticket_id, "call_id": call_id.upper(), "rule_id": rule_id,
                             "excerpt": _mask(excerpt), "severity": severity})
    routed_to = "compliance officer (same day)" if severity == "high" else "team supervisor"
    return {"status": "flagged", "ticket_id": ticket_id, "routed_to": routed_to}


def create_coaching_task(agent_id: str, theme: str, call_ids: list, recommendation: str) -> dict:
    task_id = f"COACH-{next(_ids)}"
    COACHING_TASKS.append({"task_id": task_id, "agent_id": agent_id, "theme": theme,
                           "call_ids": call_ids, "recommendation": recommendation})
    return {"status": "created", "task_id": task_id, "assigned_to": "team supervisor coaching queue"}


IMPLEMENTATIONS = {
    "list_calls": list_calls,
    "transcribe_call": transcribe_call,
    "get_transcript": get_transcript,
    "log_qa_score": log_qa_score,
    "flag_compliance_issue": flag_compliance_issue,
    "create_coaching_task": create_coaching_task,
}


def dispatch(name: str, args: dict) -> dict:
    """Run a tool by name. Errors go back to the agent so it can correct itself."""
    func = IMPLEMENTATIONS.get(name)
    if not func:
        return {"error": f"Unknown tool {name}."}
    try:
        return func(**args)
    except TypeError as exc:
        return {"error": f"Invalid arguments for {name}: {exc}"}


# ---------- Tool definitions sent to Foundry ----------

TOOL_SPECS = [
    {
        "name": "list_calls",
        "description": "List recorded calls available for QA review, optionally filtered by campaign.",
        "parameters": {
            "type": "object",
            "properties": {
                "campaign": {"type": "string", "enum": ["all", "collections", "card_services"],
                             "description": "Which campaign to list. Use 'all' for every call."},
            },
            "required": ["campaign"],
            "additionalProperties": False,
        },
    },
    {
        "name": "transcribe_call",
        "description": (
            "Transcribe the audio recording of a call with Azure AI Speech, with each turn "
            "labelled by speaker and timestamped. Use this first when reviewing a call. "
            "Account and card numbers are masked."
        ),
        "parameters": {
            "type": "object",
            "properties": {"call_id": {"type": "string", "description": "Call id, for example C-5531."}},
            "required": ["call_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_transcript",
        "description": (
            "Get the stored reference transcript of a call, typed up in advance. Use only if "
            "transcribe_call fails. Account and card numbers are masked."
        ),
        "parameters": {
            "type": "object",
            "properties": {"call_id": {"type": "string", "description": "Call id, for example C-5531."}},
            "required": ["call_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "log_qa_score",
        "description": "Save the QA scorecard result for a call. Each criterion has its own maximum; total is out of 100.",
        "parameters": {
            "type": "object",
            "properties": {
                "call_id": {"type": "string"},
                "scores": {
                    "type": "object",
                    "properties": {
                        "opening": {"type": "integer", "description": "0 to 15"},
                        "verification": {"type": "integer", "description": "0 to 20"},
                        "empathy": {"type": "integer", "description": "0 to 20"},
                        "resolution": {"type": "integer", "description": "0 to 25"},
                        "compliance": {"type": "integer", "description": "0 to 20"},
                    },
                    "required": ["opening", "verification", "empathy", "resolution", "compliance"],
                    "additionalProperties": False,
                },
                "total": {"type": "integer", "description": "Sum of the five criteria, 0 to 100."},
                "summary": {"type": "string", "description": "Two or three sentences explaining the score."},
            },
            "required": ["call_id", "scores", "total", "summary"],
            "additionalProperties": False,
        },
    },
    {
        "name": "flag_compliance_issue",
        "description": "Raise a compliance flag for one rule breach on a call. Call once per breached rule.",
        "parameters": {
            "type": "object",
            "properties": {
                "call_id": {"type": "string"},
                "rule_id": {"type": "string", "enum": RULE_IDS,
                            "description": "Rule id from the compliance checklist."},
                "excerpt": {"type": "string", "description": "The exact transcript line that shows the breach."},
                "severity": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": ["call_id", "rule_id", "excerpt", "severity"],
            "additionalProperties": False,
        },
    },
    {
        "name": "create_coaching_task",
        "description": "Create a coaching task for a contact-center agent in the supervisor's queue.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent id, for example AG-103."},
                "theme": {"type": "string", "description": "Short coaching theme, for example 'Empathy under pressure'."},
                "call_ids": {"type": "array", "items": {"type": "string"}},
                "recommendation": {"type": "string", "description": "What the supervisor should coach, in one or two sentences."},
            },
            "required": ["agent_id", "theme", "call_ids", "recommendation"],
            "additionalProperties": False,
        },
    },
]


def function_tools() -> list:
    """Tool definitions in the shape Foundry expects (used when creating the agent)."""
    from azure.ai.projects.models import FunctionTool
    return [FunctionTool(name=s["name"], description=s["description"], parameters=s["parameters"], strict=True)
            for s in TOOL_SPECS]
