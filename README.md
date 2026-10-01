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

## Start here: the workshop guide

The step-by-step instructions live in a static site in [`src/guide/`](src/guide/), written for
attendees with no prior Azure experience. It deploys with the app, so the live site serves the app
at `/` and the guide at `/guide`.

To read it, open `/guide/` on the deployed site, or run `swa start src --api-location api` and open
`/guide/` on port 4280. The files in [`labs/`](labs/) are now pointers into it.

| Step | What you do | Time |
|------|-------------|------|
| [0. Prerequisites](src/guide/00-prerequisites.html) | Azure subscription, GitHub account, costs | 20 min |
| [1. Create the project](src/guide/01-foundry-project.html) | Resource group, Foundry project, model deployment | 15 min |
| [2. Open your Codespace](src/guide/02-codespace.html) | Fork, configure `.env`, sign in to Azure | 10 min |
| [3. Your first agent](src/guide/03-first-agent.html) | A prompt agent with instructions only | 10 min |
| [4. Add knowledge](src/guide/04-knowledge.html) | Ground it in the scorecard and checklist | 15 min |
| [5. Add tools](src/guide/05-tools.html) | Let it read calls and save results | 20 min |
| [6. Run the web app](src/guide/06-run-app.html) | The front end and API in your Codespace | 15 min |
| [7. Deploy from the portal](src/guide/07-deploy-portal.html) | Create a Static Web App from your fork | 20 min |
| [8. Make the live app work](src/guide/08-configure-app.html) | Identity, app settings, sign-in | 20 min |
| [9. Evaluate](src/guide/09-evaluate.html) | Test cases, guardrails and traces | 15 min |
| [10. Delete everything](src/guide/10-clean-up.html) | Clean-up, so nothing keeps billing you | 10 min |
| [Optional: AI call recordings](labs/optional-audio.md) | Generate audio of the sample calls with Azure AI Speech | 10 min |

### Running the workshop yourself

Two things to change when you host this for your own attendees:

1. Set `REPO` at the top of [`src/guide/steps.js`](src/guide/steps.js) to your own
   `owner/repo` slug. Every fork link, Codespaces link and clone command in the guide follows it.
2. Deploy this repo once (guide Step 7) and give attendees the resulting `/guide` URL, so they can
   read the instructions before they have an Azure subscription of their own.

## In GitHub Codespaces

Attendees don't install anything. [`.devcontainer/`](.devcontainer/) builds an environment with
Python 3.10, the Azure CLI, the Static Web Apps CLI and Azure Functions Core Tools, and creates
`.env` and `api/local.settings.json` from the samples.

On a fork, select **Code > Codespaces > Create codespace on main**. When it finishes:

```bash
# fill in .env and api/local.settings.json, then:
az login --use-device-code
python scripts/check_setup.py        # checks settings, sign-in and permissions
```

`check_setup.py` is the first thing to run when anything is misbehaving — it names the guide step
that fixes each failure.

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
.devcontainer/       Codespaces environment (Python 3.10, Azure CLI, SWA CLI, Functions tools)
api/                 Azure Functions (Python) used as the web app's API
  chat/              POST /api/chat
  calls/             GET  /api/calls
  qa_agent/          Shared agent code: clients, run loop, tools, instructions, sample calls
knowledge/           Documents the agent searches (scorecard, checklist, coaching guide)
scripts/             check_setup.py, create_agent.py, chat_cli.py, evaluate.py
evals/               Test cases for evaluate.py
src/                 Static front end (HTML, CSS, JavaScript) and staticwebapp.config.json
  guide/             The attendee workshop guide, served at /guide
labs/                Pointers into src/guide/ (the instructions used to live here)
.github/workflows/   Manual fallback deploy; Azure writes the real one when you deploy (Step 7)
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
