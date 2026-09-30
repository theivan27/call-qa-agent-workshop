# Lab 5: Deploy to Azure Static Web Apps

## 1. Push the code to your GitHub repository
Create an empty repository on GitHub, then push this project's `main` branch to it.

## 2. Create the static web app
1. In the Azure portal, create a **Static Web App** on the **Free** plan.
2. For **Deployment details**, choose **Other**. (This repo already has a GitHub Actions workflow.)
3. When it's created, select **Manage deployment token** and copy the token.
4. In GitHub, go to **Settings > Secrets and variables > Actions** and add a secret named
   `AZURE_STATIC_WEB_APPS_API_TOKEN` with the token.
5. Push any change to `main` (or run the workflow manually from the **Actions** tab). The workflow
   deploys `src/` as the site and `api/` as the API.

## 3. Give the API an identity
The built-in API of Static Web Apps doesn't support managed identity, so this workshop uses a
service principal:
```bash
az ad sp create-for-rbac --name call-qa-reviewer-web
```
Note the `appId`, `password` and `tenant`. Then grant it access to your Foundry project:
```bash
az role assignment create --assignee <appId> --role "Azure AI User" \
  --scope <your Foundry project resource ID>
```
You'll find the project's resource ID in the Azure portal, on the project's **Properties** page.

## 4. Add the app settings
In your static web app, open **Settings > Environment variables** and add:

| Name | Value |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | Your project endpoint |
| `FOUNDRY_AGENT_NAME` | `call-qa-reviewer` |
| `AZURE_CLIENT_ID` | The service principal's `appId` |
| `AZURE_TENANT_ID` | The `tenant` value |
| `AZURE_CLIENT_SECRET` | The `password` value |

Open the site's URL and run a review.

## 5. Require sign-in
Right now anyone with the URL can use your agent. Replace `src/staticwebapp.config.json` with:
```json
{
  "platform": { "apiRuntime": "python:3.10" },
  "routes": [{ "route": "/*", "allowedRoles": ["authenticated"] }],
  "responseOverrides": { "401": { "redirect": "/.auth/login/aad", "statusCode": 302 } },
  "navigationFallback": { "rewrite": "/index.html", "exclude": ["/api/*", "*.{css,js,svg,png,ico}"] }
}
```
Push the change. Visitors now sign in with Microsoft Entra ID first.

## Good to know
- API requests in Static Web Apps time out after about 45 seconds. Reviewing one or two calls per
  request is fine; large batch requests may time out.
- For production, link your own Azure Functions app so the API can use a managed identity instead
  of a client secret, and keep secrets in Key Vault.

**Next:** [Lab 6: Evaluate](06-evaluate.md)
