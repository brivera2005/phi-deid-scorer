const noteInput = document.getElementById("noteInput");
const btnAnalyze = document.getElementById("btnAnalyze");
const sampleBtns = document.getElementById("sampleBtns");
const resultsSection = document.getElementById("resultsSection");
const emptyState = document.getElementById("emptyState");
const riskGauge = document.getElementById("riskGauge");
const gaugeFill = document.getElementById("gaugeFill");
const gaugeScore = document.getElementById("gaugeScore");
const riskBadge = document.getElementById("riskBadge");
const riskSummary = document.getElementById("riskSummary");
const redactCount = document.getElementById("redactCount");
const originalView = document.getElementById("originalView");
const redactedView = document.getElementById("redactedView");
const factorsGrid = document.getElementById("factorsGrid");
const redactionLog = document.getElementById("redactionLog");
const logCount = document.getElementById("logCount");
const toast = document.getElementById("toast");

const CIRC = 327;

function showToast(msg) {
  toast.textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

function highlightRedactions(text, redactions) {
  let html = text;
  const sorted = [...redactions].sort((a, b) => b.start - a.start);
  for (const r of sorted) {
    const before = html.slice(0, r.start);
    const orig = html.slice(r.start, r.end);
    const after = html.slice(r.end);
    html = `${before}<mark class="phi" title="${r.category}">${orig}</mark>${after}`;
  }
  return html;
}

async function loadSamples() {
  const samples = await fetch("/api/samples").then((r) => r.json());
  sampleBtns.innerHTML = samples
    .map((s) => `<button type="button" class="btn sample" data-id="${s.id}">${s.title}</button>`)
    .join("");
  sampleBtns.querySelectorAll(".btn.sample").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const data = await fetch(`/api/samples/${btn.dataset.id}`).then((r) => r.json());
      noteInput.value = data.content;
      showToast(`Loaded: ${data.meta?.title || btn.dataset.id}`);
    });
  });
}

function renderResults(data) {
  emptyState.classList.add("hidden");
  resultsSection.classList.remove("hidden");

  gaugeScore.textContent = data.risk_score;
  riskGauge.className = `risk-gauge ${data.risk_level}`;
  const offset = CIRC - (data.risk_score / 100) * CIRC;
  gaugeFill.style.strokeDashoffset = offset;

  riskBadge.textContent = `${data.risk_level} risk`;
  riskBadge.className = `risk-badge ${data.risk_level}`;
  riskSummary.textContent = data.summary;
  redactCount.textContent = data.redaction_count;

  originalView.textContent = data.original_text;
  redactedView.textContent = data.redacted_text;

  factorsGrid.innerHTML = data.risk_factors
    .map(
      (f) => `
    <div class="factor-card ${f.present ? "present" : "absent"}">
      <div class="factor-label">
        <span>${f.present ? "⚠ " : "✓ "}${f.label}</span>
        <span class="factor-weight">+${f.weight}</span>
      </div>
      <div class="factor-detail">${f.detail}</div>
    </div>`
    )
    .join("");

  logCount.textContent = data.redaction_count;
  redactionLog.innerHTML = data.redactions
    .map(
      (r) => `
    <div class="log-item">
      <span class="log-cat">${r.category}</span>
      <span>${r.original}</span>
      <span class="log-arrow">→ ${r.replacement}</span>
    </div>`
    )
    .join("");
}

btnAnalyze.addEventListener("click", async () => {
  const clinical_note = noteInput.value.trim();
  if (clinical_note.length < 10) {
    showToast("Enter at least 10 characters");
    return;
  }
  btnAnalyze.disabled = true;
  btnAnalyze.textContent = "Analyzing…";
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clinical_note }),
    });
    if (!res.ok) throw new Error("Analysis failed");
    renderResults(await res.json());
  } catch (e) {
    showToast(e.message);
  } finally {
    btnAnalyze.disabled = false;
    btnAnalyze.textContent = "Analyze & redact";
  }
});

loadSamples();
