"""Transcribe the call recordings with Azure AI Speech, ahead of time.

The agent can transcribe a call on demand through its transcribe_call tool, but doing it
once up front means the first review in the web app is instant, and it gives you something
to read before you trust the agent's scoring.

Transcripts are written to api/qa_agent/data/transcripts/<call_id>.json. Commit them and the
deployed app serves them straight from the cache instead of calling Speech again.

Usage:
  python scripts/transcribe_calls.py             # every call that has a recording
  python scripts/transcribe_calls.py C-5533      # just one
  python scripts/transcribe_calls.py --force     # re-transcribe, ignoring the cache
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from qa_agent import speech  # noqa: E402
from qa_agent.tools import _calls  # noqa: E402


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv

    wanted = [a.upper() for a in args]
    calls = [c for c in _calls() if not wanted or c["call_id"].upper() in wanted]
    if not calls:
        print("No matching calls. Ids are: " + ", ".join(c["call_id"] for c in _calls()))
        return 1

    print(f"Speech endpoint: {speech.speech_endpoint()}")
    auth = "SPEECH_KEY" if os.environ.get("SPEECH_KEY") else "your az login session"
    print(f"Signing in with: {auth}\n")

    failures = 0
    for call in calls:
        call_id = call["call_id"]
        audio = speech.LOCAL_AUDIO_DIR / f"{call_id}.mp3"
        if not audio.is_file():
            print(f"  {call_id}  no recording at {audio.relative_to(ROOT)}, skipped")
            continue
        if force:
            speech.transcribe.cache_clear()
            cached = speech._cache_path(call_id)
            if cached.is_file():
                cached.unlink()
        try:
            result = speech.transcribe(call_id)
        except speech.TranscriptionError as exc:
            print(f"  {call_id}  FAILED: {exc}")
            failures += 1
            continue
        where = "from cache" if result.get("cached") else "transcribed"
        turns = len(result["transcript"])
        print(f"  {call_id}  {where}, {result['duration_seconds']}s, {turns} turns")

    if failures:
        print(f"\n{failures} call(s) failed. Common causes:")
        print("  - You need the Cognitive Services Speech User role on the Foundry resource.")
        print("  - Run `az login` again if your session expired.")
        print("  - Or put a key in SPEECH_KEY in .env to skip Entra ID entirely.")
        return 1

    out = speech.CACHE_DIR.relative_to(ROOT)
    print(f"\nDone. Transcripts are in {out}/ - commit them so the deployed app uses them too.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
