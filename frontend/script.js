const API_BASE = "http://localhost:8000/api/tasks";

let tasks = [];
let nextId = 1;
let lastResults = [];

const taskForm = document.getElementById("task-form");
const taskListEl = document.getElementById("task-list");
const analyzeBtn = document.getElementById("analyze-btn");
const strategySelect = document.getElementById("strategy");
const bulkJsonTextarea = document.getElementById("bulk-json");
const loadJsonBtn = document.getElementById("load-json-btn");
const resultsEl = document.getElementById("results");
const errorEl = document.getElementById("error");
const loadingEl = document.getElementById("loading");
const summaryEl = document.getElementById("task-summary");
const depGraphEl = document.getElementById("dependency-graph");

function resetError() {
  errorEl.classList.add("hidden");
  errorEl.textContent = "";
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function renderTaskList() {
  taskListEl.innerHTML = "";
  tasks.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = `ID ${t.id}: ${t.title} (due ${t.due_date}, ${t.estimated_hours}h, importance ${t.importance}/10, deps: ${
      t.dependencies.join(", ") || "none"
    })`;
    taskListEl.appendChild(li);
  });
}

taskForm.addEventListener("submit", (e) => {
  e.preventDefault();
  resetError();

  const title = document.getElementById("title").value.trim();
  const dueDate = document.getElementById("due_date").value;
  const estimatedHours = document.getElementById("estimated_hours").value;
  const importance = document.getElementById("importance").value;
  const depsRaw = document.getElementById("dependencies").value.trim();

  if (!title || !dueDate || !estimatedHours || !importance) {
    showError("Please fill in all required fields.");
    return;
  }

  const est = parseFloat(estimatedHours);
  const imp = parseInt(importance, 10);
  if (isNaN(est) || est < 0) {
    showError("Estimated hours must be a non-negative number.");
    return;
  }
  if (isNaN(imp) || imp < 1 || imp > 10) {
    showError("Importance must be between 1 and 10.");
    return;
  }

  let deps = [];
  if (depsRaw) {
    deps = depsRaw
      .split(",")
      .map((d) => d.trim())
      .filter((d) => d.length > 0);
  }

  const task = {
    id: String(nextId),
    title,
    due_date: dueDate,
    estimated_hours: est,
    importance: imp,
    dependencies: deps,
  };
  nextId += 1;

  tasks.push(task);
  renderTaskList();
  taskForm.reset();
});

loadJsonBtn.addEventListener("click", () => {
  resetError();

  const text = bulkJsonTextarea.value.trim();
  if (!text) {
    showError("Please paste JSON before loading.");
    return;
  }

  try {
    const parsed = JSON.parse(text);
    if (!Array.isArray(parsed)) {
      showError("Bulk JSON must be an array of tasks.");
      return;
    }

    tasks = parsed.map((t, idx) => {
      const id = t.id ? String(t.id) : String(idx + 1);
      return {
        id,
        title: t.title || `Task ${id}`,
        due_date: t.due_date,
        estimated_hours: t.estimated_hours ?? 0,
        importance: t.importance ?? 5,
        dependencies: Array.isArray(t.dependencies)
          ? t.dependencies.map(String)
          : [],
      };
    });

    nextId = tasks.length + 1;
    renderTaskList();
  } catch (err) {
    console.error(err);
    showError("Invalid JSON. Please check the format.");
  }
});

function priorityBadge(score) {
  if (score >= 75) return { label: "High", className: "badge badge-high" };
  if (score >= 50) return { label: "Medium", className: "badge badge-medium" };
  return { label: "Low", className: "badge badge-low" };
}

function renderResults(items) {
  resultsEl.innerHTML = "";
  if (!items || items.length === 0) {
    const p = document.createElement("p");
    p.textContent = "No results to display.";
    resultsEl.appendChild(p);
    return;
  }

  items.forEach((t) => {
    const card = document.createElement("div");
    card.className = "result-card";

    const header = document.createElement("div");
    header.className = "result-header";

    const titleEl = document.createElement("div");
    titleEl.className = "result-title";
    titleEl.textContent = t.title;

    const scoreEl = document.createElement("div");
    const badgeInfo = priorityBadge(t.score);
    scoreEl.innerHTML = `<span>${t.score.toFixed(
      2
    )}</span> <span class="${badgeInfo.className}">${badgeInfo.label}</span>`;

    header.appendChild(titleEl);
    header.appendChild(scoreEl);

    const meta = document.createElement("div");
    meta.className = "result-meta";
    meta.textContent = `Due: ${t.due_date} | Hours: ${t.estimated_hours} | Importance: ${
      t.importance
    } | Dependencies: ${
      t.dependencies && t.dependencies.length ? t.dependencies.join(", ") : "none"
    }`;

    const explanation = document.createElement("div");
    explanation.className = "result-explanation";
    explanation.textContent = t.explanation;

    card.appendChild(header);
    card.appendChild(meta);
    card.appendChild(explanation);

    resultsEl.appendChild(card);
  });
}

function renderSummary(items) {
  if (!items || items.length === 0) {
    summaryEl.textContent = "";
    return;
  }

  const today = new Date();
  let overdue = 0;
  let dueToday = 0;
  let upcoming = 0;

  items.forEach((t) => {
    const d = new Date(t.due_date);
    const diffDays = Math.floor((d - today) / (1000 * 60 * 60 * 24));
    if (diffDays < 0) overdue++;
    else if (diffDays === 0) dueToday++;
    else upcoming++;
  });

  summaryEl.innerHTML = `Summary: Overdue: <strong>${overdue}</strong>, Due Today: <strong>${dueToday}</strong>, Upcoming: <strong>${upcoming}</strong>`;
}

function renderDependencyGraph(items) {
  depGraphEl.innerHTML = "";
  if (!items || items.length === 0) return;

  const idToTitle = {};
  const dependents = {};

  items.forEach((t) => {
    idToTitle[t.id] = t.title;
    dependents[t.id] = [];
  });

  items.forEach((t) => {
    (t.dependencies || []).forEach((depId) => {
      if (!dependents[depId]) dependents[depId] = [];
      dependents[depId].push(t.id);
    });
  });

  const depsTitle = document.createElement("div");
  depsTitle.className = "dep-section-title";
  depsTitle.textContent = "Direct Dependencies:";
  depGraphEl.appendChild(depsTitle);

  const depsList = document.createElement("ul");
  depsList.className = "dep-list";

  items.forEach((t) => {
    const li = document.createElement("li");
    const deps = (t.dependencies || []).map((id) => idToTitle[id] || id);
    li.textContent = `${t.title} → depends on: ${
      deps.length ? deps.join(", ") : "none"
    }`;
    depsList.appendChild(li);
  });

  depGraphEl.appendChild(depsList);

  const unlockTitle = document.createElement("div");
  unlockTitle.className = "dep-section-title";
  unlockTitle.textContent = "Tasks Unblocked:";
  depGraphEl.appendChild(unlockTitle);

  const unlockList = document.createElement("ul");
  unlockList.className = "dep-list";

  Object.keys(dependents).forEach((id) => {
    const li = document.createElement("li");
    const title = idToTitle[id] || id;
    const deps = dependents[id].map((x) => idToTitle[x] || x);
    li.textContent = `${title} → unblocks: ${
      deps.length ? deps.join(", ") : "none"
    }`;
    unlockList.appendChild(li);
  });

  depGraphEl.appendChild(unlockList);
}

function renderEisenhowerMatrix(items) {
  const q1 = document
    .getElementById("matrix-urgent-important")
    .querySelector(".matrix-list");
  const q2 = document
    .getElementById("matrix-urgent-not-important")
    .querySelector(".matrix-list");
  const q3 = document
    .getElementById("matrix-not-urgent-important")
    .querySelector(".matrix-list");
  const q4 = document
    .getElementById("matrix-not-urgent-not-important")
    .querySelector(".matrix-list");

  [q1, q2, q3, q4].forEach((ul) => (ul.innerHTML = ""));

  if (!items || items.length === 0) return;

  const today = new Date();

  items.forEach((t) => {
    const d = new Date(t.due_date);
    const diffDays = Math.floor((d - today) / (1000 * 60 * 60 * 24));
    const urgent = diffDays <= 2; // overdue or due very soon
    const important = t.importance >= 7;

    const li = document.createElement("li");
    li.textContent = `${t.title} (score ${t.score.toFixed(1)})`;

    if (urgent && important) q1.appendChild(li);
    else if (urgent && !important) q2.appendChild(li);
    else if (!urgent && important) q3.appendChild(li);
    else q4.appendChild(li);
  });
}

analyzeBtn.addEventListener("click", async () => {
  resetError();
  resultsEl.innerHTML = "";
  summaryEl.textContent = "";
  depGraphEl.innerHTML = "";
  lastResults = [];

  if (tasks.length === 0) {
    showError("Please add at least one task before analyzing.");
    return;
  }

  const invalidTask = tasks.find(
    (t) =>
      !t.title ||
      !t.due_date ||
      t.estimated_hours == null ||
      t.importance == null
  );
  if (invalidTask) {
    showError("All tasks must have title, due date, estimated hours, and importance.");
    return;
  }

  const strategy = strategySelect.value;

  const body = {
    strategy,
    tasks: tasks.map((t) => ({
      id: t.id,
      title: t.title,
      due_date: t.due_date,
      estimated_hours: t.estimated_hours,
      importance: t.importance,
      dependencies: t.dependencies,
    })),
  };

  analyzeBtn.disabled = true;
  loadingEl.classList.remove("hidden");

  try {
    const resp = await fetch(`${API_BASE}/analyze/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      const msg = errData.detail || "API error while analyzing tasks.";
      showError(msg);
      return;
    }

    const data = await resp.json();
    lastResults = data;

    renderResults(data);
    renderSummary(data);          // bonus summary
    renderDependencyGraph(data);  // bonus dep graph
    renderEisenhowerMatrix(data); // bonus matrix
  } catch (err) {
    console.error(err);
    showError("Failed to reach backend API. Is the server running?");
  } finally {
    analyzeBtn.disabled = false;
    loadingEl.classList.add("hidden");
  }
});
