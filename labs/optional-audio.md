# Optional: generate AI call recordings

Turn the five fictional transcripts into audio with Azure AI Speech text to speech, so the web
app can play each call before the agent reviews it. Taglish calls use Filipino voices and English
calls use Philippine English voices.

## 1. Get a Speech key
In the Azure portal, open your Foundry resource (or any Azure AI Speech resource) and go to
**Keys and Endpoint**. Copy a key and the region, and add them to `.env`:
```
SPEECH_KEY=<your key>
SPEECH_REGION=<your region, for example southeastasia>
```

## 2. Generate the recordings
```bash
pip install azure-cognitiveservices-speech
python scripts/generate_audio.py            # all five calls
python scripts/generate_audio.py C-5533     # or just one
```
The files are saved to `src/audio/`. Restart `swa start` and each call in the list gets a player.

## 3. Use it in the demo
Play 15 to 20 seconds of a call before asking the agent to review it. C-5533 works well: the
audience hears the threat and the personal e-wallet request, then watches the agent flag both.

## Good practice
- Say that the voices are AI-generated and the call is fictional. The web app labels each player.
- Don't generate voices that imitate real people, and don't use this to create audio of real
  customer calls.
- To hear the voices before generating, try them in the Speech playground in the Foundry portal.
