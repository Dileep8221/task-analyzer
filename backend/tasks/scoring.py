from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List, Optional


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected among tasks."""
    pass


STRATEGY_WEIGHTS = {
    "smart_balance": {
        "urgency": 0.35,
        "importance": 0.35,
        "effort": 0.15,
        "dependencies": 0.15,
    },
    "fastest_wins": {
        "urgency": 0.20,
        "importance": 0.20,
        "effort": 0.50,
        "dependencies": 0.10,
    },
    "high_impact": {
        "urgency": 0.20,
        "importance": 0.60,
        "effort": 0.10,
        "dependencies": 0.10,
    },
    "deadline_driven": {
        "urgency": 0.60,
        "importance": 0.20,
        "effort": 0.10,
        "dependencies": 0.10,
    },
}

DEFAULT_STRATEGY = "smart_balance"
MAX_EFFORT_HOURS = 8.0


@dataclass
class ScoredTask:
    data: Dict[str, Any]
    score: float
    explanation: str


def _adjust_for_weekend(due_date: date) -> date:
    """
    Date intelligence: if a task is due on weekend, we treat its effective
    due date as the following Monday for urgency purposes.
    (Holidays could be added as a future extension.)
    """
    weekday = due_date.weekday()  # 0=Mon ... 5=Sat, 6=Sun
    if weekday == 5:  # Saturday -> Monday
        return due_date + timedelta(days=2)
    if weekday == 6:  # Sunday -> Monday
        return due_date + timedelta(days=1)
    return due_date


def _normalize_urgency(due_date: date, today: Optional[date] = None) -> float:
    if today is None:
        today = date.today()

    # Use adjusted date for weekends when computing urgency
    effective_due = _adjust_for_weekend(due_date)
    days_diff = (effective_due - today).days

    if days_diff <= 0:
        # Due today or in the past (or Monday after a weekend due date)
        return 1.0
    if days_diff >= 14:
        return 0.0
    # Linearly scale between 0 and 14 days
    return (14 - days_diff) / 14.0


def _normalize_importance(importance: int) -> float:
    importance = max(1, min(importance, 10))
    return importance / 10.0


def _normalize_effort(estimated_hours: float) -> float:
    # We treat small tasks as better (higher score).
    h = max(0.0, min(estimated_hours, MAX_EFFORT_HOURS))
    return 1.0 - (h / MAX_EFFORT_HOURS)


def _build_dependency_maps(tasks: List[Dict[str, Any]]):
    """
    Build:
      - id_map: task_id -> task dict
      - deps: task_id -> list[dependency_id]
      - reverse_deps: task_id -> list[task_ids that depend on it]

    Also validates dependency references and 'dependencies' type.
    """
    ids: List[Any] = []
    for idx, t in enumerate(tasks):
        tid = t.get("id", str(idx))
        ids.append(tid)

    id_set = set(ids)

    deps: Dict[Any, List[Any]] = {tid: [] for tid in ids}
    reverse_deps: Dict[Any, List[Any]] = {tid: [] for tid in ids}
    id_map: Dict[Any, Dict[str, Any]] = {}

    for idx, t in enumerate(tasks):
        tid = t.get("id", str(idx))
        id_map[tid] = t
        dep_ids = t.get("dependencies") or []

        if not isinstance(dep_ids, list):
            raise ValueError(f"Task {tid!r} has invalid 'dependencies' (expected list).")

        for dep in dep_ids:
            if dep not in id_set:
                raise ValueError(f"Task {tid!r} depends on unknown task id {dep!r}.")
            deps[tid].append(dep)
            reverse_deps[dep].append(tid)

    return id_map, deps, reverse_deps


def _detect_cycles(deps: Dict[Any, List[Any]]):
    """
    Detect circular dependencies using DFS.
    Raises CircularDependencyError if a cycle is found.
    """
    visited = set()
    stack = set()

    def dfs(node: Any):
        visited.add(node)
        stack.add(node)
        for neighbor in deps.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in stack:
                # Found a cycle
                raise CircularDependencyError(
                    f"Circular dependency detected involving task {neighbor!r}."
                )
        stack.remove(node)

    for node in deps.keys():
        if node not in visited:
            dfs(node)


def _compute_dependency_score(reverse_deps: Dict[Any, List[Any]], task_id: Any) -> float:
    dependents_count = len(reverse_deps.get(task_id, []))
    if not reverse_deps:
        return 0.0
    max_dep = max((len(v) for v in reverse_deps.values()), default=0)
    if max_dep == 0:
        return 0.0
    return dependents_count / max_dep


def _build_explanation(
    *, days_diff: int, importance: int, estimated_hours: float, dependents_count: int
) -> str:
    # Urgency phrase (based on raw calendar days for clarity)
    if days_diff < 0:
        urgency_phrase = "overdue"
    elif days_diff == 0:
        urgency_phrase = "due today"
    elif days_diff == 1:
        urgency_phrase = "due in 1 day"
    elif days_diff <= 7:
        urgency_phrase = f"due in {days_diff} days"
    else:
        urgency_phrase = f"due in {days_diff} days (low urgency)"

    # Importance phrase
    if importance >= 8:
        importance_phrase = "high importance"
    elif importance >= 4:
        importance_phrase = "medium importance"
    else:
        importance_phrase = "low importance"

    # Effort phrase
    if estimated_hours <= 2:
        effort_phrase = "quick win"
    elif estimated_hours <= 5:
        effort_phrase = "moderate effort"
    else:
        effort_phrase = "long task"

    # Dependency phrase
    if dependents_count > 0:
        dep_phrase = f"unblocks {dependents_count} other task(s)"
    else:
        dep_phrase = "no dependent tasks"

    return (
        f"{urgency_phrase}, {importance_phrase} ({importance}/10), "
        f"{effort_phrase} ({estimated_hours}h), {dep_phrase}."
    )


def score_tasks(
    tasks: List[Dict[str, Any]],
    strategy: str = DEFAULT_STRATEGY,
    today: Optional[date] = None,
) -> List[ScoredTask]:
    """
    Given a list of task dicts, compute scores and explanations.
    Returns a list of ScoredTask objects sorted by score (descending).

    Expects each task dict to have:
      - id (optional, string)
      - title
      - due_date (datetime.date)
      - importance (int)
      - estimated_hours (float)
      - dependencies (list of ids, optional)
    """
    if today is None:
        today = date.today()

    if strategy not in STRATEGY_WEIGHTS:
        raise ValueError(f"Unknown strategy '{strategy}'.")

    weights = STRATEGY_WEIGHTS[strategy]

    # Build graphs, validate, and detect cycles
    id_map, deps, reverse_deps = _build_dependency_maps(tasks)
    _detect_cycles(deps)

    scored: List[ScoredTask] = []

    for task_id, task in id_map.items():
        due_date = task.get("due_date")
        importance = int(task.get("importance", 0))
        estimated_hours = float(task.get("estimated_hours", 0.0))

        if not isinstance(due_date, date):
            raise ValueError(f"Task {task_id!r} has invalid or missing 'due_date'.")

        u = _normalize_urgency(due_date, today)
        i = _normalize_importance(importance)
        e = _normalize_effort(estimated_hours)
        d = _compute_dependency_score(reverse_deps, task_id)

        score_raw = (
            weights["urgency"] * u
            + weights["importance"] * i
            + weights["effort"] * e
            + weights["dependencies"] * d
        )
        score = round(score_raw * 100, 2)

        days_diff = (due_date - today).days
        dependents_count = len(reverse_deps.get(task_id, []))
        explanation = _build_explanation(
            days_diff=days_diff,
            importance=importance,
            estimated_hours=estimated_hours,
            dependents_count=dependents_count,
        )

        task_with_meta = dict(task)
        task_with_meta["score"] = score
        task_with_meta["explanation"] = explanation

        scored.append(ScoredTask(data=task_with_meta, score=score, explanation=explanation))

    scored.sort(key=lambda st: st.score, reverse=True)
    return scored
