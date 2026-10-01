# Call QA Reviewer: build an agent with Microsoft Foundry

A hands-on workshop project for **Building Agents with AI Foundry** (Infoseer Consulting).

You'll build an AI agent that reviews recorded contact-center calls for a bank: it reads the
transcript, scores it against a QA scorecard, checks a compliance checklist, and logs scores,
compliance flags and coaching tasks. Then you'll put it behind a simple web app and deploy it to
Azure Static Web Apps.

The scenario fits both **banks** (collections and servicing compliance) and **BPOs** (QA at scale
across client programs). All data is fictional: Northwind Bank and Contoso BPO are sample names.

![The web app: calls to review, a chat with the agent, and a live log of every tool call](docs/screenshot.png)

## What you'll build

```
 Browser (src/)                Azure Functions API (api/)              Microsoft Foundry
┌──────────────────┐  /api/*  ┌─────────────────────────────┐        ┌──────────────────────────┐
│ Calls list       │ ───────▶ │ chat: runs the tool loop    │ ─────▶ │ Prompt agent             │
│ Chat with agent  │          │ calls: lists sample calls   │ ◀───── │  - model + instructions  │
│ "What the agent  │ ◀─────── │ qa_agent/tools.py executes  │        │  - file search knowledge │
│  did" activity   │          │ function calls on mock data │        │  - function tools        │
└──────────────────┘          └─────────────────────────────┘        └──────────────────────────┘
```

- **Knowledge** (`knowledge/`): QA scorecard, compliance checklist (CC-01 to CC-07) and coaching
  guide, uploaded to a vector store and searched with the file search tool.
- **Tools** (`api/qa_agent/tools.py`): `list_calls`, `get_transcript`, `log_qa_score`,
  `flag_compliance_issue`, `create_coaching_task`. They run in your code, not in Foundry.
- **Guardrails**: the instructions keep HR decisions with people; the code masks card and account
  numbers before the model sees them and validates every score.

## Labs

| Lab | What you do | Time |
|-----|-------------|------|
| [0. Set up](labs/00-setup.md) | Foundry project, model deployment, local environment | 15 min |
| [1. Your first agent](labs/01-first-agent.md) | Create a prompt agent with instructions only | 10 min |
| [2. Add knowledge](labs/02-knowledge.md) | Ground it in the scorecard and checklist | 10 min |
| [3. Add tools](labs/03-tools.md) | Let it read calls and save results | 20 min |
| [4. Run the web app](labs/04-web-app.md) | Run the static web app and API locally | 15 min |
| [5. Deploy](labs/05-deploy.md) | Publish to Azure Static Web Apps | 20 min |
| [6. Evaluate](labs/06-evaluate.md) | Run test cases and check the guardrails | 10 min |
| [Optional: AI call recordings](labs/optional-audio.md) | Generate audio of the sample calls with Azure AI Speech | 10 min |

## Quick start (if you've done this before)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r api/requirements.txt
cp .env.sample .env                                     # fill in your project endpoint and model
az login
python scripts/create_agent.py                          # knowledge + tools (stage 3)
python scripts/chat_cli.py                              # try: Review call C-5531.
cp api/local.settings.sample.json api/local.settings.json
swa start src --api-location api                        # open http://localhost:4280
```

## Repository layout

```
api/                 Azure Functions (Python) used as the web app's API
  chat/              POST /api/chat
  calls/             GET  /api/calls
  qa_agent/          Shared agent code: clients, run loop, tools, instructions, sample calls
knowledge/           Documents the agent searches (scorecard, checklist, coaching guide)
scripts/             create_agent.py, chat_cli.py, evaluate.py
evals/               Test cases for evaluate.py
src/                 Static front end (HTML, CSS, JavaScript) and staticwebapp.config.json
labs/                Step-by-step instructions
.github/workflows/   GitHub Actions deployment to Azure Static Web Apps
```

## Costs and clean-up

Model calls and file search are billed to your Azure subscription; the Static Web Apps Free plan
has no charge. When you're done, delete the resource group that holds your Foundry project and
static web app.

## Security notes

This is a teaching sample. Before using the pattern with real data: require sign-in on the web
app (Lab 5 shows how), move the API to a separately deployed Functions app with managed identity,
keep secrets in Key Vault, and replace the mock tools with calls to your real systems using
least-privilege access.
