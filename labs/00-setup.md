# Lab 0: Set up

## You'll need
- An Azure subscription where you can create Microsoft Foundry resources
- [Python 3.10](https://www.python.org/downloads/) (the Static Web Apps API runs on Python 3.10, so use it locally too)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Node.js 18 or later](https://nodejs.org/) and [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local) (for Lab 4)
- Git, and a GitHub account (for Lab 5)
- Optional: Visual Studio Code with the Foundry extension

## 1. Create a Foundry project and deploy a model
1. Go to the [Foundry portal](https://ai.azure.com) and create a project (this also creates a Foundry resource).
2. Deploy a chat model from the model catalog, for example `gpt-4.1-mini`. Note the **deployment name**.
3. On the project's welcome screen, copy the **project endpoint**. It looks like
   `https://<resource-name>.services.ai.azure.com/api/projects/<project-name>`.
4. Make sure your account has the **Azure AI User** role (or higher) on the project.

## 2. Get the code
```bash
git clone <your-copy-of-this-repo>
cd call-qa-agent-workshop
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r api/requirements.txt
```

## 3. Configure and sign in
```bash
cp .env.sample .env                # Windows: copy .env.sample .env
```
Open `.env` and set `FOUNDRY_PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME`. Then:
```bash
az login
```
The code uses `DefaultAzureCredential`, which picks up your Azure CLI sign-in, so no keys are needed.

**Next:** [Lab 1: Your first agent](01-first-agent.md)
