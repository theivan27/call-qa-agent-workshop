// Call QA Reviewer front end. Talks to /api/chat and /api/calls (Azure Functions).
const els = {
  messages: document.getElementById("messages"),
  form: document.getElementById("composer"),
  input: document.getElementById("input"),
  send: document.getElementById("send"),
  callList: document.getElementById("call-list"),
  activity: document.getElementById("activity-list"),
  newChat: document.getElementById("new-chat"),
};

let conversationId = null;
let turn = 0;

const CAMPAIGN_LABEL = { collections: "Collections", card_services: "Card services" };

// ---------- Calls list ----------
async function loadCalls() {
  try {
    const res = await fetch("/api/calls");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const { calls } = await res.json();
    els.callList.innerHTML = "";
    for (const c of calls) {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "call";
      btn.innerHTML = `
        <span class="call-id">${esc(c.call_id)}</span>
        <span class="call-campaign">${esc(CAMPAIGN_LABEL[c.campaign] || c.campaign)}</span>
        <span class="call-meta">${esc(c.agent_name)} (${esc(c.agent_id)}), ${esc(c.language)}, ${c.duration_min} min</span>`;
      btn.addEventListener("click", () => {
        els.input.value = `Review call ${c.call_id}.`;
        els.input.focus();
      });
      li.appendChild(btn);
      els.callList.appendChild(li);
    }
  } catch (err) {
    els.callList.innerHTML = `<li class="muted">Couldn't load calls (${esc(err.message)}). Is the API running?</li>`;
  }
}

// ---------- Chat ----------
function addMessage(who, html, kind = "") {
  const empty = els.messages.querySelector(".empty");
  if (empty) empty.remove();
  const wrap = document.createElement("div");
  wrap.className = `msg ${kind}`;
  wrap.innerHTML = `<div class="msg-who">${esc(who)}</div><div class="msg-body">${html}</div>`;
  els.messages.appendChild(wrap);
  els.messages.scrollTop = els.messages.scrollHeight;
  return wrap;
}

async function send(text) {
  text = text.trim();
  if (!text) return;
  addMessage("You", `<p>${esc(text)}</p>`, "you");
  els.input.value = "";
  setBusy(true);
  const pending = addMessage("QA agent", `<p class="thinking">Reviewing…</p>`);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, conversationId }),
    });
    const data = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
    conversationId = data.conversationId;
    pending.querySelector(".msg-body").innerHTML = renderMarkdown(data.reply || "(No reply text.)");
    renderTrace(data.trace || [], text);
  } catch (err) {
    pending.classList.add("error");
    pending.querySelector(".msg-body").innerHTML =
      `<p>The agent didn't respond: ${esc(err.message)}</p>` +
      `<p>Check that the API is running, FOUNDRY_PROJECT_ENDPOINT is set, and you ran scripts/create_agent.py.</p>`;
  } finally {
    setBusy(false);
    els.input.focus();
  }
}

function setBusy(busy) {
  els.send.disabled = busy;
  els.send.textContent = busy ? "Working…" : "Send";
}

// ---------- Activity ledger ----------
function describe(step) {
  const a = step.arguments || {};
  const r = step.result || {};
  if (r.error) return { kind: "error", label: "Error returned", title: `${step.name}: ${r.error}` };
  switch (step.name) {
    case "file_search":
      return { kind: "read", label: "Knowledge", title: "Searched the QA scorecard and checklists" };
    case "list_calls":
      return { kind: "read", label: "Read", title: `Listed ${a.campaign === "all" ? "all" : a.campaign.replace("_", " ")} calls` };
    case "get_transcript":
      return { kind: "read", label: "Read", title: `Read transcript ${a.call_id}` };
    case "log_qa_score":
      return { kind: "write", label: "Saved", title: `Logged score ${a.total}/100 for ${a.call_id} (${r.record_id})` };
    case "flag_compliance_issue":
      return { kind: "flag", label: "Compliance flag", title: `${a.rule_id}, ${a.severity} severity, on ${a.call_id} (${r.ticket_id})` };
    case "create_coaching_task":
      return { kind: "write", label: "Saved", title: `Coaching task for ${a.agent_id}: ${a.theme} (${r.task_id})` };
    default:
      return { kind: "read", label: "Tool", title: step.name };
  }
}

function renderTrace(trace, prompt) {
  const empty = els.activity.querySelector(".ledger-empty");
  if (empty) empty.remove();
  turn += 1;
  const divider = document.createElement("li");
  divider.className = "turn-divider";
  divider.textContent = `Request ${turn}: ${prompt.length > 60 ? prompt.slice(0, 57) + "…" : prompt}`;
  els.activity.appendChild(divider);

  if (!trace.length) {
    const li = document.createElement("li");
    li.className = "step read new";
    li.innerHTML = `<div class="step-title">Answered without using tools</div>`;
    els.activity.appendChild(li);
    return;
  }
  for (const step of trace) {
    const d = describe(step);
    const li = document.createElement("li");
    li.className = `step ${d.kind} new`;
    li.innerHTML = `
      <span class="step-kind">${esc(d.label)}</span>
      <div class="step-title">${esc(d.title)}</div>
      <details><summary>Show details</summary>
        <pre>${esc(JSON.stringify({ arguments: step.arguments, result: step.result }, null, 2))}</pre>
      </details>`;
    els.activity.appendChild(li);
  }
  els.activity.parentElement.scrollTop = els.activity.parentElement.scrollHeight;
}

// ---------- Minimal, safe Markdown (bold, lists, tables, headings) ----------
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function inline(s) {
  return esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
}
function renderMarkdown(md) {
  const lines = md.replace(/\r/g, "").split("\n");
  let html = "", list = null, table = [];
  const flushList = () => { if (list) { html += `<ul>${list.join("")}</ul>`; list = null; } };
  const flushTable = () => {
    if (!table.length) return;
    const rows = table.filter((r) => !/^\|?\s*:?-{2,}/.test(r.replace(/\|/g, "|").trim()));
    const cells = (r) => r.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
    html += "<table>" + rows.map((r, i) => {
      const tag = i === 0 ? "th" : "td";
      return "<tr>" + cells(r).map((c) => `<${tag}>${inline(c)}</${tag}>`).join("") + "</tr>";
    }).join("") + "</table>";
    table = [];
  };
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^\s*\|/.test(line)) { flushList(); table.push(line); continue; }
    flushTable();
    const item = line.match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
    if (item) { (list ||= []).push(`<li>${inline(item[1])}</li>`); continue; }
    flushList();
    const heading = line.match(/^#{1,6}\s+(.*)$/);
    if (heading) { html += `<p><strong>${inline(heading[1])}</strong></p>`; continue; }
    if (line.trim()) html += `<p>${inline(line)}</p>`;
  }
  flushList(); flushTable();
  return html;
}

// ---------- Wire up ----------
els.form.addEventListener("submit", (e) => { e.preventDefault(); send(els.input.value); });
els.input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(els.input.value); }
});
document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => send(chip.textContent))
);
els.newChat.addEventListener("click", () => {
  conversationId = null;
  turn = 0;
  els.messages.innerHTML = `<div class="empty"><p class="empty-title">New review started.</p><p>Pick a call or type a request.</p></div>`;
  els.activity.innerHTML = `<li class="muted ledger-empty">Nothing yet. Tool calls appear here as the agent works.</li>`;
});

loadCalls();
