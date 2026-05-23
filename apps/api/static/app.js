const API_BASE = "";
let samples = [];
let selectedSample = null;

async function init() {
  try {
    const res = await fetch(`${API_BASE}/api/demo/samples`);
    if (res.ok) {
      samples = await res.json();
      renderSampleButtons(samples);
    } else {
      useFallbackSamples();
    }
  } catch {
    useFallbackSamples();
  }
}

function useFallbackSamples() {
  samples = [
    { name: "good", label: "Good Asset", task_id: "freshbench_doc_good_001" },
    { name: "bad", label: "Bad Asset", task_id: "freshbench_doc_bad_001" },
    { name: "near_duplicate", label: "Near Duplicate", task_id: "freshbench_doc_dup_001" },
  ];
  renderSampleButtons(samples);
}

function renderSampleButtons(items) {
  const container = document.getElementById("sample-buttons");
  container.innerHTML = "";

  items.forEach((sample) => {
    const btn = document.createElement("button");
    btn.className = "sample-btn";
    btn.textContent = sample.label || sample.name;
    btn.dataset.name = sample.name;
    btn.addEventListener("click", () => selectSample(sample, btn));
    container.appendChild(btn);
  });
}

function selectSample(sample, btn) {
  document.querySelectorAll(".sample-btn").forEach((b) => b.classList.remove("selected"));
  btn.classList.add("selected");
  selectedSample = sample;
  document.getElementById("validate-btn").disabled = false;

  if (sample.submission) {
    showSubmission(sample.submission);
  } else {
    document.getElementById("submission-preview").classList.add("hidden");
  }
}

function showSubmission(submission) {
  const section = document.getElementById("submission-preview");
  section.classList.remove("hidden");
  document.getElementById("submission-json").textContent = JSON.stringify(submission, null, 2);
}

document.getElementById("validate-btn").addEventListener("click", async () => {
  if (!selectedSample) return;

  const btn = document.getElementById("validate-btn");
  btn.disabled = true;
  btn.classList.add("loading");
  btn.textContent = "Validating...";

  document.getElementById("results").classList.add("hidden");

  try {
    let report;
    if (selectedSample.submission) {
      const res = await fetch(`${API_BASE}/api/assets/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(selectedSample.submission),
      });
      report = await res.json();
    } else {
      const res = await fetch(`${API_BASE}/api/demo/validate/${selectedSample.name}`);
      report = await res.json();
    }
    renderReport(report);
  } catch (err) {
    alert("Validation failed: " + err.message);
  } finally {
    btn.disabled = false;
    btn.classList.remove("loading");
    btn.textContent = "Validate Asset";
  }
});

function renderReport(report) {
  const results = document.getElementById("results");
  results.classList.remove("hidden");

  const scoreEl = document.getElementById("final-score");
  const score = report.final_score;
  scoreEl.textContent = (score * 100).toFixed(1) + "%";
  scoreEl.style.color = score >= 0.5 ? "#00d4aa" : score > 0 ? "#d4aa00" : "#ff4d4d";

  const stateEl = document.getElementById("asset-state");
  stateEl.textContent = report.state;
  stateEl.className = "state-badge state-" + report.state;

  renderStages(report.stages);
  renderReward(report.reward_hint);

  document.getElementById("report-json").textContent = JSON.stringify(report, null, 2);
}

function renderStages(stages) {
  const container = document.getElementById("stages");
  container.innerHTML = "";

  stages.forEach((stage) => {
    const el = document.createElement("div");
    el.className = "stage";

    const icon = stage.passed ? "✅" : "❌";
    const costMs = stage.cost_ms != null ? stage.cost_ms.toFixed(2) + "ms" : "";

    el.innerHTML = `
      <div class="stage-header" onclick="this.nextElementSibling.classList.toggle('open')">
        <div class="stage-left">
          <span class="stage-icon">${icon}</span>
          <span class="stage-name">${formatStageName(stage.stage)}</span>
        </div>
        <div class="stage-right">
          <span class="stage-score">${(stage.score * 100).toFixed(1)}%</span>
          <span class="stage-time">${costMs}</span>
        </div>
      </div>
      <div class="stage-details">
        <div class="stage-reason">${stage.reason}</div>
        <div class="stage-evidence">${JSON.stringify(stage.evidence, null, 2)}</div>
      </div>
    `;

    container.appendChild(el);
  });
}

function formatStageName(name) {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function renderReward(hint) {
  const container = document.getElementById("reward-hint");
  container.innerHTML = `
    <div class="reward-grid">
      <div class="reward-item">
        <div class="reward-label">Submission Reward</div>
        <div class="reward-value">${hint.submission_reward.toFixed(2)}</div>
      </div>
      <div class="reward-item">
        <div class="reward-label">Usage Reward Weight</div>
        <div class="reward-value">${hint.usage_reward_weight.toFixed(4)}</div>
      </div>
    </div>
  `;
}

init();
