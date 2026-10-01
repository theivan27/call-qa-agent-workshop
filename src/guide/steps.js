/* The single source of truth for the guide's navigation.
   Add a step here and every page's sidebar, progress bar and prev/next links pick it up. */

const STEPS = [
  { file: "index.html",            num: null, title: "Start here",            time: "5 min",  blurb: "What you'll build and how the day runs" },
  { file: "00-prerequisites.html", num: "0",  title: "Prerequisites",         time: "20 min", blurb: "Azure subscription, GitHub account, costs" },
  { file: "01-foundry-project.html", num: "1", title: "Create the project",   time: "15 min", blurb: "Resource group, Foundry project, model" },
  { file: "02-codespace.html",     num: "2",  title: "Open your Codespace",   time: "10 min", blurb: "Fork the repo and sign in to Azure" },
  { file: "03-first-agent.html",   num: "3",  title: "Your first agent",      time: "10 min", blurb: "A model plus instructions" },
  { file: "04-knowledge.html",     num: "4",  title: "Add knowledge",         time: "15 min", blurb: "Ground it in your scorecard" },
  { file: "05-tools.html",         num: "5",  title: "Add tools",             time: "20 min", blurb: "Let it read calls and save results" },
  { file: "06-run-app.html",       num: "6",  title: "Run the web app",       time: "15 min", blurb: "The front end in your Codespace" },
  { file: "07-deploy-portal.html", num: "7",  title: "Deploy from the portal", time: "20 min", blurb: "Create a Static Web App from your fork" },
  { file: "08-configure-app.html", num: "8",  title: "Make the live app work", time: "20 min", blurb: "Identity, settings, sign-in" },
  { file: "09-evaluate.html",      num: "9",  title: "Evaluate",              time: "15 min", blurb: "Test cases and traces" },
  { file: "10-clean-up.html",      num: "10", title: "Delete everything",     time: "10 min", blurb: "Stop the billing" },
];

/* Change this one line when you host the workshop from your own repository, and every
   link, fork button and clone command in the guide follows. */
const REPO = "theivan27/call-qa-agent-workshop";

const REPO_LINKS = {
  repo: `https://github.com/${REPO}`,
  fork: `https://github.com/${REPO}/fork`,
  codespace: `https://codespaces.new/${REPO}`,
};

/* Fills in <span data-repo></span> with the slug, and sets href on
   <a data-repo-url="repo|fork|codespace">. */
function applyRepoName() {
  document.querySelectorAll("[data-repo]").forEach((el) => {
    el.textContent = REPO;
  });
  document.querySelectorAll("[data-repo-url]").forEach((el) => {
    const kind = el.getAttribute("data-repo-url") || "repo";
    const href = REPO_LINKS[kind];
    if (href) el.setAttribute("href", href);
  });
}

const STORAGE_KEY = "callqa-guide-progress";

/* localStorage can throw in private windows or with site data blocked, and it is
   per-browser only, so every read and write is guarded and the page works without it. */
function readProgress() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function writeProgress(done) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(done));
  } catch {
    /* Progress just won't persist. Not worth interrupting the reader. */
  }
}

function currentFile() {
  const name = location.pathname.split("/").pop();
  return name && name.endsWith(".html") ? name : "index.html";
}

function buildSidebar() {
  const nav = document.querySelector("[data-guide-nav]");
  if (!nav) return;

  const here = currentFile();
  const done = readProgress();

  const list = document.createElement("ol");
  list.className = "step-nav";

  for (const step of STEPS) {
    const li = document.createElement("li");
    li.className = "step-nav-item";
    if (step.file === here) li.classList.add("is-current");
    if (done[step.file]) li.classList.add("is-done");

    const link = document.createElement("a");
    link.href = step.file;
    if (step.file === here) link.setAttribute("aria-current", "page");

    const marker = document.createElement("span");
    marker.className = "step-marker";
    marker.setAttribute("aria-hidden", "true");
    marker.textContent = done[step.file] ? "✓" : (step.num ?? "·");

    const label = document.createElement("span");
    label.className = "step-label";
    label.textContent = step.title;

    link.append(marker, label);
    li.append(link);
    list.append(li);
  }

  nav.append(list);
}

function buildProgressBar() {
  const host = document.querySelector("[data-guide-progress]");
  if (!host) return;

  const done = readProgress();
  const total = STEPS.length;
  const finished = STEPS.filter((s) => done[s.file]).length;
  const pct = Math.round((finished / total) * 100);

  host.innerHTML = "";

  const label = document.createElement("p");
  label.className = "progress-label";
  label.textContent = `${finished} of ${total} done`;

  const track = document.createElement("div");
  track.className = "progress-track";
  track.setAttribute("role", "progressbar");
  track.setAttribute("aria-valuenow", String(pct));
  track.setAttribute("aria-valuemin", "0");
  track.setAttribute("aria-valuemax", "100");
  track.setAttribute("aria-label", "Workshop progress");

  const fill = document.createElement("div");
  fill.className = "progress-fill";
  fill.style.width = `${pct}%`;
  track.append(fill);

  host.append(label, track);
}

/* The "I've finished this step" control at the bottom of each step page. */
function buildDoneToggle() {
  const host = document.querySelector("[data-guide-done]");
  if (!host) return;

  const here = currentFile();
  const done = readProgress();

  const wrap = document.createElement("label");
  wrap.className = "done-toggle";

  const box = document.createElement("input");
  box.type = "checkbox";
  box.checked = Boolean(done[here]);

  const text = document.createElement("span");
  text.textContent = "I've finished this step";

  box.addEventListener("change", () => {
    const next = readProgress();
    if (box.checked) next[here] = true;
    else delete next[here];
    writeProgress(next);
    buildProgressBar();
    document.querySelectorAll(".step-nav-item").forEach((li, i) => {
      const step = STEPS[i];
      li.classList.toggle("is-done", Boolean(next[step.file]));
      const marker = li.querySelector(".step-marker");
      if (marker) marker.textContent = next[step.file] ? "✓" : (step.num ?? "·");
    });
  });

  wrap.append(box, text);
  host.append(wrap);
}

function buildPrevNext() {
  const host = document.querySelector("[data-guide-pager]");
  if (!host) return;

  const here = currentFile();
  const i = STEPS.findIndex((s) => s.file === here);
  if (i === -1) return;

  const prev = STEPS[i - 1];
  const next = STEPS[i + 1];

  if (prev) {
    const a = document.createElement("a");
    a.className = "pager-link pager-prev";
    a.href = prev.file;
    a.innerHTML = `<span class="pager-dir">← Back</span><span class="pager-title"></span>`;
    a.querySelector(".pager-title").textContent = prev.title;
    host.append(a);
  }
  if (next) {
    const a = document.createElement("a");
    a.className = "pager-link pager-next";
    a.href = next.file;
    a.innerHTML = `<span class="pager-dir">Next →</span><span class="pager-title"></span>`;
    a.querySelector(".pager-title").textContent = next.title;
    host.append(a);
  }
}

/* Copy buttons on every code block, so nobody loses a command to a bad selection. */
function addCopyButtons() {
  document.querySelectorAll("pre > code").forEach((code) => {
    const pre = code.parentElement;
    pre.classList.add("has-copy");

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "Copy";

    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(code.textContent);
        btn.textContent = "Copied";
      } catch {
        btn.textContent = "Press Ctrl+C";
        const range = document.createRange();
        range.selectNodeContents(code);
        const sel = getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      }
      setTimeout(() => { btn.textContent = "Copy"; }, 1800);
    });

    pre.append(btn);
  });
}

function wireSidebarToggle() {
  const btn = document.querySelector("[data-nav-toggle]");
  const panel = document.querySelector("[data-guide-sidebar]");
  if (!btn || !panel) return;

  btn.addEventListener("click", () => {
    const open = panel.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", String(open));
  });
}

document.addEventListener("DOMContentLoaded", () => {
  applyRepoName();
  buildSidebar();
  buildProgressBar();
  buildDoneToggle();
  buildPrevNext();
  addCopyButtons();
  wireSidebarToggle();
});
