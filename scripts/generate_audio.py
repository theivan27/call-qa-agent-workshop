"""Generate AI voice recordings of the sample calls with Azure AI Speech (text to speech).

Each call in api/qa_agent/data/calls.json becomes src/audio/<call_id>.mp3, with one voice for
the contact-center agent and another for the customer. The web app shows a player for every
call that has a recording. All calls are fictional; label the audio as AI-generated when you
play it to an audience.

Needs SPEECH_KEY and SPEECH_REGION in .env. You can use the key and region from your Foundry
resource (Azure portal > your Foundry resource > Keys and Endpoint) or from a Speech resource.

Usage:
  python scripts/generate_audio.py            # all calls
  python scripts/generate_audio.py C-5533     # one call
"""
import json
import os
import sys
from xml.sax.saxutils import escape

from _setup import ROOT

import azure.cognitiveservices.speech as speechsdk

CALLS_FILE = ROOT / "api" / "qa_agent" / "data" / "calls.json"
OUT_DIR = ROOT / "src" / "audio"

# Philippine voices: Filipino voices for Taglish calls, Philippine English voices for English calls.
VOICES = {
    ("Taglish", "female"): ("fil-PH", "fil-PH-BlessicaNeural"),
    ("Taglish", "male"): ("fil-PH", "fil-PH-AngeloNeural"),
    ("English", "female"): ("en-PH", "en-PH-RosaNeural"),
    ("English", "male"): ("en-PH", "en-PH-JamesNeural"),
}

# Who sounds like whom in each fictional call: (agent, customer).
SPEAKERS = {
    "C-5531": ("male", "female"),
    "C-5532": ("female", "male"),
    "C-5533": ("female", "male"),
    "C-5534": ("female", "female"),
    "C-5535": ("female", "female"),
}


def build_ssml(call: dict) -> str:
    language = call["language"] if call["language"] in ("Taglish", "English") else "Taglish"
    agent_gender, customer_gender = SPEAKERS.get(call["call_id"], ("female", "male"))
    lang, agent_voice = VOICES[(language, agent_gender)]
    _, customer_voice = VOICES[(language, customer_gender)]
    same_voice = agent_voice == customer_voice

    parts = []
    for turn in call["transcript"]:
        text = escape(turn["text"])
        if turn["speaker"] == "Agent":
            parts.append(f'<voice name="{agent_voice}">{text}<break time="450ms"/></voice>')
        else:
            # If both speakers share a voice, shift the customer's pitch and pace so they sound different.
            if same_voice:
                text = f'<prosody pitch="-12%" rate="-6%">{text}</prosody>'
            parts.append(f'<voice name="{customer_voice}">{text}<break time="450ms"/></voice>')

    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">'
            + "".join(parts) + "</speak>")


def main() -> None:
    key, region = os.environ.get("SPEECH_KEY"), os.environ.get("SPEECH_REGION")
    if not key or not region:
        sys.exit("Set SPEECH_KEY and SPEECH_REGION in .env first (see the docstring at the top of this script).")

    calls = json.loads(CALLS_FILE.read_text(encoding="utf-8"))["calls"]
    wanted = {a.upper() for a in sys.argv[1:]}
    if wanted:
        calls = [c for c in calls if c["call_id"].upper() in wanted]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3)

    for call in calls:
        path = OUT_DIR / f"{call['call_id']}.mp3"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(path))
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_ssml_async(build_ssml(call)).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Saved {path.relative_to(ROOT)}")
        else:
            details = result.cancellation_details
            print(f"Failed {call['call_id']}: {details.reason} {details.error_details}")


if __name__ == "__main__":
    main()
