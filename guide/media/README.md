# Screenshots for the guide

Drop PNG files in this folder using the exact filenames below. The guide already has a slot
waiting for each one.

**You don't have to do all of them.** A slot with no image is removed from the page
automatically, so attendees never see a gap. Capture the **P1** shots first — those are the
points where a beginner genuinely cannot tell what to click. P2 shots are reassurance.

## How the slots behave

| Where you're viewing | A missing image shows as |
|---|---|
| The deployed guide | nothing — the figure is removed |
| `localhost`, or any URL with `?shots=debug` | a dashed "Screenshot needed" box naming the file |

So to see what's still outstanding, open the deployed guide with `?shots=debug` on the end of
the URL, for example `…azurestaticapps.net/02-codespace.html?shots=debug`.

## Before you capture

- **Browser zoom 100%**, window about **1400px** wide. Narrower and the Azure portal collapses
  its layout, which won't match what attendees see.
- **Light theme** in both the Azure portal and VS Code. The guide is light by default and a dark
  screenshot in a light page looks like a mistake.
- **Crop to the panel that matters**, not the whole 4K desktop. A full-screen capture scaled into
  the content column makes the labels unreadable.
- **Draw a red box** (2–3px, `#d13438`) around the control to click. Windows Snip & Sketch or
  ShareX both do this. One box per shot; number them only if a shot needs two.
- **PNG**, under about 400 KB each. If one is heavier, scale the long edge to 1600px.

## Redact before saving

You're working in the **Infoseer – Prod** subscription, so this matters:

- Subscription IDs and tenant GUIDs
- Your email address and profile photo in the portal's top-right corner
- Any real resource name you don't want public — the guide uses `fdy-callqa-ab1234` and
  `swa-call-qa-ab1234` as examples, so matching those keeps it consistent
- **Never** capture a deployment token, a client secret, or the output of
  `az ad sp create-for-rbac` with real values. For shot 17, retype the values as obvious
  placeholders first.

The guide is a public site. Assume every screenshot will be read closely by someone.

## The shots

### Step 1 — Create the project

| File | P | What to capture |
|---|---|---|
| `01-resource-group.png` | P2 | The **Create a resource group** form, filled in with `rg-call-qa-workshop`, before you press Review + create. |
| `02-foundry-create-advanced.png` | **P1** | The Foundry **Create project** dialog with **Advanced options expanded**, showing the resource group field set to `rg-call-qa-workshop`. Box the "Advanced options" toggle. This is the step people miss, and it's why their resources scatter. Get the **New Foundry** toggle in frame too if it fits. |
| `03-deploy-model.png` | **P1** | **Discover** → **Models** → the model picker with `gpt-4.1-mini` found and selected. Box the **Deploy** button. |
| `04-project-endpoint.png` | **P1** | The project **Home** page showing the endpoint containing `/api/projects/`, with the copy button boxed. Blur the rest of the page if it shows anything identifying. The single most-mistyped value in the workshop. |
| `05-role-assignment.png` | **P1** | **Access control (IAM)** → Add role assignment, with **Foundry User** selected in the role list — may still read **Azure AI User** while the rename rolls out. Box the role. |

### Step 2 — Open your Codespace

| File | P | What to capture |
|---|---|---|
| `06-fork.png` | **P1** | GitHub's **Create a new fork** page for the repo, with the **Create fork** button boxed. |
| `07-codespace-create.png` | **P1** | The green **Code** button open, on the **Codespaces** tab, with **Create codespace on main** boxed. Make sure the URL bar shows a fork under *your* username — that's the mistake this shot prevents. |
| `08-codespace-ready.png` | **P1** | The whole Codespace once the build finishes: file explorer on the left, terminal at the bottom showing the "Your environment is ready" message. Orients people who've never seen VS Code in a browser. |
| `09-env-file.png` | P2 | `.env` open in the editor with the placeholder values still in it. Shows them which file and which lines. |
| `10-az-login-device-code.png` | **P1** | The terminal right after `az login --use-device-code`, showing the code and the URL. **Redact the actual code.** |
| `11-check-setup.png` | P2 | `python scripts/check_setup.py` with all four checks passing. |

### Step 6 — Run the web app

| File | P | What to capture |
|---|---|---|
| `12-port-forward.png` | **P1** | The Codespaces notification for port 4280 with **Open in Browser**, or the **Ports** tab with the globe icon boxed. People get stuck here with the app running and no idea how to see it. |
| `13-app-running.png` | P2 | The app after one review, with **What the agent did** populated on the right — include a visible `transcribe_call` entry and an audio player under a call in the list. Good "this is what success looks like" shot. |

### Step 7 — Deploy from your Codespace

| File | P | What to capture |
|---|---|---|
| `14-swa-deploy-output.png` | **P1** | The terminal after `swa deploy` finishes, with the live site URL on screen. Box the URL. **Check no part of the deployment token is visible** — scroll so the token command is off screen before you capture. |

Step 7 used to walk through the portal wizard, so shots 15 (Build Details) and 16 (Actions run)
no longer have a slot. Don't capture them.

### Step 8 — Make the live app work

| File | P | What to capture |
|---|---|---|
| `17-swa-env-vars.png` | P2 | **Settings → Environment variables** on the Static Web App, showing the five names on the **Production** tab. Values must be placeholders or hidden — this screen holds a client secret. |

### Step 10 — Delete everything

| File | P | What to capture |
|---|---|---|
| `18-delete-rg.png` | **P1** | The **Delete resource group** confirmation blade, with the resource list visible above and the name-confirmation box boxed. |

## Adding a shot that isn't listed

Put the file here, then add a slot to the relevant page:

```html
<figure class="shot" data-shot="my-new-shot">
  <img src="media/my-new-shot.png" alt="What the reader should look at" loading="lazy">
  <figcaption>One sentence on what is happening.</figcaption>
</figure>
```

The `alt` text is what shows in the "Screenshot needed" placeholder, and it's what screen-reader
users get, so describe the action rather than writing "screenshot of the portal".
