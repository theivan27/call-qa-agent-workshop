/* The single source of truth for the guide's navigation and chrome.
   Add a step to STEPS and every sidebar, breadcrumb, progress bar and pager picks it up. */

const MODULE_TITLE = "Build a call QA agent";
const MODULE_KICKER = "Workshop";

const STEPS = [
  { file: "index.html",              num: null, title: "Start here",             time: "5 min",  blurb: "What you'll build and how the day runs" },
  { file: "00-prerequisites.html",   num: "0",  title: "Prerequisites",          time: "20 min", blurb: "Azure subscription, GitHub account, costs" },
  { file: "01-foundry-project.html", num: "1",  title: "Create the project",     time: "15 min", blurb: "Resource group, Foundry project, model" },
  { file: "02-codespace.html",       num: "2",  title: "Open your Codespace",    time: "10 min", blurb: "Fork the repo and sign in to Azure" },
  { file: "03-first-agent.html",     num: "3",  title: "Your first agent",       time: "10 min", blurb: "A model plus instructions" },
  { file: "04-knowledge.html",       num: "4",  title: "Add knowledge",          time: "15 min", blurb: "Ground it in your scorecard" },
  { file: "05-tools.html",           num: "5",  title: "Add tools",              time: "20 min", blurb: "Let it read calls and save results" },
  { file: "06-run-app.html",         num: "6",  title: "Run the web app",        time: "15 min", blurb: "The front end in your Codespace" },
  { file: "07-deploy-portal.html",   num: "7",  title: "Deploy from the portal", time: "20 min", blurb: "Create a Static Web App from your fork" },
  { file: "08-configure-app.html",   num: "8",  title: "Make the live app work", time: "20 min", blurb: "Identity, settings, sign-in" },
  { file: "09-evaluate.html",        num: "9",  title: "Evaluate",               time: "15 min", blurb: "Test cases and traces" },
  { file: "10-clean-up.html",        num: "10", title: "Delete everything",      time: "10 min", blurb: "Stop the billing" },
];

/* Change this one line when you host the workshop from your own repository, and every
   link, fork button and clone command in the guide follows. */
const REPO = "theivan27/call-qa-agent-workshop";

const REPO_LINKS = {
  repo: `https://github.com/${REPO}`,
  fork: `https://github.com/${REPO}/fork`,
  codespace: `https://codespaces.new/${REPO}`,
};

const STORAGE_KEY = "callqa-guide-progress";

/* ---------- helpers ---------- */

function currentFile() {
  const name = location.pathname.split("/").pop();
  return name && name.endsWith(".html") ? name : "index.html";
}

function currentStep() {
  return STEPS.find((s) => s.file === currentFile()) || null;
}

function lastStepNumber() {
  const nums = STEPS.map((s) => Number(s.num)).filter((n) => !Number.isNaN(n));
  return nums.length ? Math.max(...nums) : 0;
}

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

/* Fills in <span data-repo></span> with the slug, and sets href on
   <a data-repo-url="repo|fork|codespace">. */
function applyRepoName() {
  document.querySelectorAll("[data-repo]").forEach((el) => {
    el.textContent = REPO;
  });
  document.querySelectorAll("[data-repo-url]").forEach((el) => {
    const href = REPO_LINKS[el.getAttribute("data-repo-url") || "repo"];
    if (href) el.setAttribute("href", href);
  });
}

/* ---------- left column ---------- */

function buildModuleCard() {
  const progress = document.querySelector("[data-guide-progress]");
  if (!progress) return;

  const card = document.createElement("div");
  card.className = "module-card";

  const kicker = document.createElement("p");
  kicker.className = "module-eyebrow";
  kicker.textContent = MODULE_KICKER;

  const title = document.createElement("p");
  title.className = "module-title";
  title.textContent = MODULE_TITLE;

  card.append(kicker, title);
  progress.parentNode.insertBefore(card, progress);
  card.append(progress);
}

function buildSidebar() {
  const nav = document.querySelector("[data-guide-nav]");
  if (!nav) return;

  const here = currentFile();
  const done = readProgress();

  const heading = document.createElement("p");
  heading.className = "toc-heading";
  heading.id = "toc-heading";
  heading.textContent = `${STEPS.length} units`;

  const list = document.createElement("ol");
  list.className = "step-nav";
  list.setAttribute("aria-labelledby", "toc-heading");

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

    const time = document.createElement("span");
    time.className = "step-time";
    time.textContent = step.time;
    label.append(time);

    if (done[step.file]) {
      const sr = document.createElement("span");
      sr.className = "visually-hidden";
      sr.textContent = " (completed)";
      label.append(sr);
    }

    link.append(marker, label);
    li.append(link);
    list.append(li);
  }

  nav.append(heading, list);
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
  label.textContent = `${finished} of ${total} complete`;

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

/* ---------- content chrome ---------- */

function buildBreadcrumb() {
  const main = document.querySelector(".guide-main");
  if (!main) return;

  const step = currentStep();
  const here = currentFile();

  const nav = document.createElement("nav");
  nav.className = "breadcrumb";
  nav.setAttribute("aria-label", "Breadcrumb");

  const list = document.createElement("ol");

  const crumbs = [{ text: MODULE_TITLE, href: here === "index.html" ? null : "index.html" }];
  if (step && here !== "index.html") crumbs.push({ text: step.title, href: null });

  for (const crumb of crumbs) {
    const li = document.createElement("li");
    if (crumb.href) {
      const a = document.createElement("a");
      a.href = crumb.href;
      a.textContent = crumb.text;
      li.append(a);
    } else {
      const span = document.createElement("span");
      span.setAttribute("aria-current", "page");
      span.textContent = crumb.text;
      li.append(span);
    }
    list.append(li);
  }

  nav.append(list);
  main.insertBefore(nav, main.firstChild);
}

/* Learn shows "Unit 4 of 12" above the title. The pages carry "Step 3"; add the total. */
function annotateUnitNumber() {
  const step = currentStep();
  const eyebrow = document.querySelector(".guide-main .eyebrow");
  if (!step || !eyebrow || step.num === null) return;
  eyebrow.textContent = `Step ${step.num} of ${lastStepNumber()}`;
}

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .slice(0, 60);
}

/* Gives every h2/h3 a stable id and a hover anchor, then builds the right rail from them. */
function buildUnitRail() {
  const main = document.querySelector(".guide-main");
  const shell = document.querySelector(".guide-shell");
  if (!main || !shell) return;

  const headings = [...main.querySelectorAll("h2, h3")];
  const used = new Set();

  for (const h of headings) {
    if (!h.id) {
      let base = slugify(h.textContent) || "section";
      let id = base;
      let n = 2;
      while (used.has(id) || document.getElementById(id)) id = `${base}-${n++}`;
      h.id = id;
    }
    used.add(h.id);

    const anchor = document.createElement("a");
    anchor.className = "heading-anchor";
    anchor.href = `#${h.id}`;
    anchor.textContent = "#";
    anchor.setAttribute("aria-label", `Link to ${h.textContent}`);
    h.append(anchor);
  }

  const tops = headings.filter((h) => h.tagName === "H2");
  if (tops.length < 2) return;

  const rail = document.createElement("aside");
  rail.className = "rail";
  rail.setAttribute("aria-labelledby", "rail-title");

  const title = document.createElement("p");
  title.className = "rail-title";
  title.id = "rail-title";
  title.textContent = "In this unit";

  const list = document.createElement("ul");
  list.className = "rail-list";

  const links = new Map();
  for (const h of tops) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = `#${h.id}`;
    // Strip the trailing "#" from the anchor we just appended.
    a.textContent = [...h.childNodes]
      .filter((n) => !(n.nodeType === 1 && n.classList.contains("heading-anchor")))
      .map((n) => n.textContent)
      .join("")
      .trim();
    li.append(a);
    list.append(li);
    links.set(h.id, a);
  }

  rail.append(title, list);
  shell.append(rail);

  wireScrollSpy(tops, links);
}

/* Highlights the rail entry for whichever section you're reading. */
function wireScrollSpy(headings, links) {
  if (!("IntersectionObserver" in window)) return;

  const seen = new Map();

  const setActive = () => {
    let active = null;
    for (const h of headings) {
      if (seen.get(h.id)) { active = h.id; break; }
    }
    if (!active) {
      // Nothing on screen: fall back to the last heading scrolled past.
      for (const h of headings) {
        if (h.getBoundingClientRect().top < 120) active = h.id;
      }
    }
    links.forEach((a, id) => a.classList.toggle("is-active", id === active));
  };

  const observer = new IntersectionObserver(
    (entries) => {
      for (const e of entries) seen.set(e.target.id, e.isIntersecting);
      setActive();
    },
    { rootMargin: "-80px 0px -65% 0px", threshold: 0 }
  );

  headings.forEach((h) => observer.observe(h));
  addEventListener("scroll", setActive, { passive: true });
  setActive();
}

/* ---------- footer ---------- */

function refreshNavMarkers(done) {
  document.querySelectorAll(".step-nav-item").forEach((li, i) => {
    const step = STEPS[i];
    if (!step) return;
    const isDone = Boolean(done[step.file]);
    li.classList.toggle("is-done", isDone);
    const marker = li.querySelector(".step-marker");
    if (marker) marker.textContent = isDone ? "✓" : (step.num ?? "·");
  });
}

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
  text.textContent = "Mark this step complete";

  box.addEventListener("change", () => {
    const next = readProgress();
    if (box.checked) next[here] = true;
    else delete next[here];
    writeProgress(next);
    buildProgressBar();
    refreshNavMarkers(next);
  });

  wrap.append(box, text);
  host.append(wrap);
}

function buildPrevNext() {
  const host = document.querySelector("[data-guide-pager]");
  if (!host) return;

  const i = STEPS.findIndex((s) => s.file === currentFile());
  if (i === -1) return;

  const make = (step, dir, label) => {
    const a = document.createElement("a");
    a.className = `pager-link pager-${dir}`;
    a.href = step.file;

    const d = document.createElement("span");
    d.className = "pager-dir";
    d.textContent = label;

    const t = document.createElement("span");
    t.className = "pager-title";
    t.textContent = step.title;

    a.append(d, t);
    return a;
  };

  const prev = STEPS[i - 1];
  const next = STEPS[i + 1];
  if (prev) host.append(make(prev, "prev", "← Previous"));
  if (next) host.append(make(next, "next", "Next →"));
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
  buildModuleCard();
  buildBreadcrumb();
  annotateUnitNumber();
  buildUnitRail();
  buildDoneToggle();
  buildPrevNext();
  addCopyButtons();
  wireSidebarToggle();
});
