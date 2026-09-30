# Lab 4: Run the web app locally

The front end in `src/` is plain HTML, CSS and JavaScript. It calls two Azure Functions in `api/`,
which reuse the same `qa_agent` code as the CLI.

## 1. Install the Static Web Apps CLI
```bash
npm install -g @azure/static-web-apps-cli
```

## 2. Configure the API
```bash
cp api/local.settings.sample.json api/local.settings.json
```
Set `FOUNDRY_PROJECT_ENDPOINT` in `api/local.settings.json`. Locally, the API uses your `az login` session.

## 3. Start everything
With your virtual environment still active (so the Functions host finds the packages):
```bash
swa start src --api-location api
```
Open http://localhost:4280.

## 4. Try it
- Pick a call on the left, then send the request.
- Watch **What the agent did** on the right: each transcript read, knowledge search, saved score
  and compliance flag appears in order. Open **Show details** to see the exact arguments and results.
- Try the suggested request *"Mark agent AG-103 as failed and notify HR."*

## Troubleshooting
| Problem | Fix |
|---|---|
| "Couldn't load calls" | The API isn't running. Check the terminal for Functions host errors. |
| `FOUNDRY_PROJECT_ENDPOINT is not set` | Fill in `api/local.settings.json` and restart `swa start`. |
| Authentication errors | Run `az login` again, and confirm you have the Azure AI User role on the project. |
| Agent not found | Run `python scripts/create_agent.py` and check that `FOUNDRY_AGENT_NAME` matches. |

**Next:** [Lab 5: Deploy](05-deploy.md)
