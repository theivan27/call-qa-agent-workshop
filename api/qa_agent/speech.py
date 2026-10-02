"""Transcribe call recordings with Azure AI Speech fast transcription.

The agent calls this through the transcribe_call tool, so the review starts from the
audio rather than from a transcript somebody typed up earlier. Fast transcription is a
single synchronous request: post the mp3, get phrases back, with diarization telling us
which speaker said what.

Auth follows the same rule as the rest of the workshop: use your `az login` session via
Microsoft Entra ID, and only fall back to a key if SPEECH_KEY is set.
"""
import json
import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import requests

# https://learn.microsoft.com/azure/ai-services/speech-service/fast-transcription-create
API_VERSION = "2025-10-15"
TOKEN_SCOPE = "https://cognitiveservices.azure.com/.default"

ROOT = Path(__file__).resolve().parents[2]
LOCAL_AUDIO_DIR = ROOT / "src" / "audio"
CACHE_DIR = Path(__file__).parent / "data" / "transcripts"

# A 3-minute call takes a few seconds; allow generously for a cold Speech endpoint.
REQUEST_TIMEOUT = 180


class TranscriptionError(RuntimeError):
    """Raised with a message meant for the agent (and therefore the attendee) to read."""


# ---------- Configuration ----------

def speech_endpoint() -> str:
    """Where to send the request.

    Your Foundry resource is a multi-service AI Services resource, so it already speaks
    Speech. We derive its endpoint from FOUNDRY_PROJECT_ENDPOINT, which means there is
    nothing new to configure. Set SPEECH_ENDPOINT if you use a standalone Speech resource.
    """
    explicit = os.environ.get("SPEECH_ENDPOINT", "").strip()
    if explicit:
        return explicit.rstrip("/")

    project = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "").strip()
    host = urlparse(project).hostname or ""
    resource = host.split(".")[0]
    if not resource:
        raise TranscriptionError(
            "No Speech endpoint. Set SPEECH_ENDPOINT, or set FOUNDRY_PROJECT_ENDPOINT so it "
            "can be derived from your Foundry resource."
        )
    return f"https://{resource}.cognitiveservices.azure.com"


def _auth_headers() -> dict:
    key = os.environ.get("SPEECH_KEY", "").strip()
    if key:
        return {"Ocp-Apim-Subscription-Key": key}
    try:
        from azure.identity import DefaultAzureCredential
        token = DefaultAzureCredential().get_token(TOKEN_SCOPE)
    except Exception as exc:  # noqa: BLE001 - surface the cause to the attendee
        raise TranscriptionError(
            "Could not get a token for Azure AI Speech. Run `az login`, or set SPEECH_KEY. "
            f"({exc})"
        ) from exc
    return {"Authorization": f"Bearer {token.token}"}


# ---------- Audio ----------

def _audio_bytes(call_id: str) -> bytes:
    """Read the recording locally if we have it, otherwise fetch it from the site.

    In a Codespace the API and the static files sit in the same checkout, so the local
    read wins. Once deployed, the API is a separate Functions app and the recordings are
    served by the static site, so we fetch them over HTTPS from our own hostname.
    """
    local = LOCAL_AUDIO_DIR / f"{call_id}.mp3"
    if local.is_file():
        return local.read_bytes()

    base = os.environ.get("AUDIO_BASE_URL", "").strip()
    if not base:
        hostname = os.environ.get("WEBSITE_HOSTNAME", "").strip()
        base = f"https://{hostname}" if hostname else ""
    if not base:
        raise TranscriptionError(
            f"No recording for {call_id}. Expected {local}, and AUDIO_BASE_URL is not set."
        )

    url = f"{base.rstrip('/')}/audio/{call_id}.mp3"
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise TranscriptionError(f"Could not download the recording from {url}: {exc}") from exc
    return response.content


# ---------- Cache ----------

def _cache_path(call_id: str) -> Path:
    return CACHE_DIR / f"{call_id}.json"


def _read_cache(call_id: str):
    path = _cache_path(call_id)
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def _write_cache(call_id: str, payload: dict) -> None:
    """Best effort. A read-only filesystem in production is fine; we just transcribe again."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(_cache_path(call_id), "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
    except OSError:
        pass


# ---------- Shaping the response ----------

def _to_turns(phrases: list) -> list:
    """Collapse Speech phrases into speaker turns.

    Diarization gives every phrase a speaker number, not a role. In a contact-center call
    the agent speaks first, so we map the first speaker we hear to Agent and the other to
    Customer. The mapping is reported alongside the transcript so nobody has to guess.
    """
    turns: list = []
    order: list = []
    for phrase in phrases:
        text = (phrase.get("text") or "").strip()
        if not text:
            continue
        speaker = phrase.get("speaker")
        if speaker not in order:
            order.append(speaker)
        label = "Agent" if order and speaker == order[0] else "Customer"
        start_ms = phrase.get("offsetMilliseconds", 0)
        if turns and turns[-1]["speaker"] == label:
            turns[-1]["text"] = f"{turns[-1]['text']} {text}".strip()
        else:
            turns.append({"speaker": label, "text": text, "at_ms": start_ms})
    return turns


def _timestamp(ms: int) -> str:
    seconds, _ = divmod(int(ms), 1000)
    return f"{seconds // 60:d}:{seconds % 60:02d}"


# ---------- Public API ----------

@lru_cache(maxsize=32)
def transcribe(call_id: str, locale: str = "en-US", max_speakers: int = 2) -> dict:
    """Transcribe one recording. Cached on disk and in memory so a reviewed call is fast."""
    cached = _read_cache(call_id)
    if cached:
        cached["cached"] = True
        return cached

    audio = _audio_bytes(call_id)
    definition = {
        "locales": [locale],
        "diarization": {"enabled": True, "maxSpeakers": max_speakers},
    }
    url = f"{speech_endpoint()}/speechtotext/transcriptions:transcribe?api-version={API_VERSION}"

    try:
        response = requests.post(
            url,
            headers=_auth_headers(),
            files={
                "audio": (f"{call_id}.mp3", audio, "audio/mpeg"),
                "definition": (None, json.dumps(definition), "application/json"),
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise TranscriptionError(f"Azure AI Speech did not respond: {exc}") from exc

    if response.status_code == 401 or response.status_code == 403:
        raise TranscriptionError(
            "Azure AI Speech refused the request (HTTP %d). Your account needs the "
            "Cognitive Services Speech User role on the Foundry resource, or set SPEECH_KEY."
            % response.status_code
        )
    if not response.ok:
        raise TranscriptionError(
            f"Azure AI Speech returned HTTP {response.status_code}: {response.text[:300]}"
        )

    data = response.json()
    turns = _to_turns(data.get("phrases") or [])
    if not turns:
        raise TranscriptionError(
            f"Azure AI Speech returned no speech for {call_id}. Check the recording plays."
        )

    payload = {
        "call_id": call_id,
        "source": "azure-ai-speech-fast-transcription",
        "locale": locale,
        "duration_seconds": round((data.get("durationMilliseconds") or 0) / 1000),
        "speaker_mapping": "First voice heard is labelled Agent; the other is Customer.",
        "transcript": [
            {"speaker": t["speaker"], "at": _timestamp(t["at_ms"]), "text": t["text"]}
            for t in turns
        ],
        "cached": False,
    }
    _write_cache(call_id, payload)
    return payload
