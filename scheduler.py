"""
scheduler.py - Greedy study-task scheduling (pure Python, no Streamlit).

Problem (short): choose and order study tasks so that
  1. the total hours used never exceed the available hours (budget),
  2. every chosen task finishes on or before its deadline,
  3. the total priority (importance) points of the chosen tasks is as high as possible.

Greedy rule used here (documented in README.md and REPORT.md):
  SELECTION: look at tasks in decreasing order of  priority / duration
             ("importance points per hour").  Accept a task only if
             (a) it still fits in the remaining hours, and
             (b) the accepted set can still meet every deadline.
  ORDERING : run the accepted tasks in Earliest Deadline First (EDF) order.
"""

import math
from dataclasses import dataclass

EPS = 1e-9            # tolerance for floating point comparisons
MAX_DURATION = 100.0  # longest single task we accept (hours)
MAX_NAME_LEN = 60
MAX_BRUTE_FORCE_TASKS = 12  # 2^12 = 4096 subsets: still instant


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Task:
    name: str
    duration: float    # estimated hours
    deadline_day: int  # days from today (0 = today, 1 = tomorrow, ...)
    priority: int      # 1 (low) .. 5 (very high)


@dataclass(frozen=True)
class ScheduledItem:
    task: Task
    start: float       # hour on the study timeline when the task starts
    end: float         # hour on the study timeline when the task ends
    finish_day: int    # day offset (0 = today) on which the task ends
    on_time: bool      # True if it ends on/before its deadline


@dataclass
class ScheduleResult:
    strategy: str
    items: list        # list[ScheduledItem] in the order they are studied
    deferred: list     # list[(Task, reason_text)]
    total_hours: float
    hours_per_day: float

    @property
    def used_hours(self):
        return sum(i.task.duration for i in self.items)

    @property
    def remaining_hours(self):
        return self.total_hours - self.used_hours

    @property
    def total_priority(self):
        return sum(i.task.priority for i in self.items)

    @property
    def on_time_priority(self):
        return sum(i.task.priority for i in self.items if i.on_time)

    @property
    def late_count(self):
        return sum(1 for i in self.items if not i.on_time)


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------
def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def validate_task(name, duration, deadline_day, priority, existing_names=()):
    """Return a list of error messages (empty list = the task is valid)."""
    errors = []

    if not isinstance(name, str) or not name.strip():
        errors.append("Task name cannot be empty.")
    elif len(name.strip()) > MAX_NAME_LEN:
        errors.append(f"Task name must be at most {MAX_NAME_LEN} characters.")
    elif name.strip().lower() in {n.strip().lower() for n in existing_names}:
        errors.append(f"A task named '{name.strip()}' already exists.")

    if not _is_number(duration):
        errors.append("Duration must be a number of hours.")
    elif duration <= 0:
        errors.append("Duration must be greater than 0 hours.")
    elif duration > MAX_DURATION:
        errors.append(f"Duration cannot be more than {MAX_DURATION:g} hours.")

    if not isinstance(priority, int) or isinstance(priority, bool) or not 1 <= priority <= 5:
        errors.append("Priority must be a whole number from 1 to 5.")

    if not isinstance(deadline_day, int) or isinstance(deadline_day, bool):
        errors.append("Deadline must be a valid date.")
    elif deadline_day < 0:
        errors.append("Deadline cannot be before today.")

    return errors


def validate_budget(total_hours, hours_per_day):
    """Validate the sidebar settings. Return a list of error messages."""
    errors = []
    if not _is_number(total_hours) or total_hours <= 0:
        errors.append("Total available study hours must be greater than 0.")
    if not _is_number(hours_per_day) or not 0 < hours_per_day <= 24:
        errors.append("Study hours per day must be greater than 0 and at most 24.")
    return errors


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def deadline_hours(task, hours_per_day):
    """Deadline converted to 'hours on the study timeline'.
    A task due on day d must be finished by the end of day d, i.e. before
    (d + 1) * hours_per_day study hours have been used."""
    return (task.deadline_day + 1) * hours_per_day


def edf_order(tasks):
    """Earliest Deadline First order (ties: higher priority, shorter, name)."""
    return sorted(tasks, key=lambda t: (t.deadline_day, -t.priority, t.duration, t.name))


def is_feasible(ordered_tasks, hours_per_day):
    """Run the tasks back-to-back in the given order; True if none is late."""
    clock = 0.0
    for t in ordered_tasks:
        clock += t.duration
        if clock > deadline_hours(t, hours_per_day) + EPS:
            return False
    return True


def _build_items(ordered_tasks, hours_per_day):
    items = []
    clock = 0.0
    for t in ordered_tasks:
        start = clock
        clock += t.duration
        finish_day = max(math.ceil(clock / hours_per_day - EPS) - 1, 0)
        on_time = clock <= deadline_hours(t, hours_per_day) + EPS
        items.append(ScheduledItem(t, start, clock, finish_day, on_time))
    return items


def _make_result(strategy, ordered_tasks, deferred, total_hours, hours_per_day):
    return ScheduleResult(strategy, _build_items(ordered_tasks, hours_per_day),
                          deferred, total_hours, hours_per_day)


# ----------------------------------------------------------------------
# The greedy algorithm
# ----------------------------------------------------------------------
def greedy_rank_key(task):
    """Sort key: highest priority-per-hour first.
    Ties: earlier deadline, then shorter task, then name (so output is repeatable)."""
    return (-task.priority / task.duration, task.deadline_day, task.duration, task.name)


def greedy_schedule(tasks, total_hours, hours_per_day):
    """Greedy selection by priority/duration + EDF ordering. See module docstring."""
    ranked = sorted(tasks, key=greedy_rank_key)          # Step 1: rank
    chosen, deferred, used = [], [], 0.0

    for t in ranked:                                      # Step 2: scan once
        if not is_feasible([t], hours_per_day):
            deferred.append((t, "Deadline too close: it cannot finish in time even if started first"))
        elif used + t.duration > total_hours + EPS:
            deferred.append((t, "Not enough remaining study hours"))
        elif not is_feasible(edf_order(chosen + [t]), hours_per_day):
            deferred.append((t, "Adding it would make another task miss its deadline"))
        else:
            chosen.append(t)
            used += t.duration

    ordered = edf_order(chosen)                           # Step 3: order by deadline
    return _make_result("Greedy (priority/hour + EDF)", ordered, deferred,
                        total_hours, hours_per_day)


# ----------------------------------------------------------------------
# Baseline and exact comparison
# ----------------------------------------------------------------------
def baseline_fcfs(tasks, total_hours, hours_per_day):
    """Baseline: First-Come-First-Served. Take tasks in the order they were
    entered while they fit in the hours. It ignores priority and deadlines."""
    chosen, deferred, used = [], [], 0.0
    for t in tasks:
        if used + t.duration <= total_hours + EPS:
            chosen.append(t)
            used += t.duration
        else:
            deferred.append((t, "Not enough remaining study hours"))
    return _make_result("Baseline (first-come-first-served)", chosen, deferred,
                        total_hours, hours_per_day)


def brute_force_optimal(tasks, total_hours, hours_per_day):
    """Try every subset (2^n) and keep the best one. Only for small n.
    'Best' = most priority points; ties -> fewer hours used."""
    n = len(tasks)
    if n > MAX_BRUTE_FORCE_TASKS:
        raise ValueError(f"Brute force is limited to {MAX_BRUTE_FORCE_TASKS} tasks.")

    best_subset, best_score = [], (0, 0.0)
    for mask in range(1 << n):
        subset = [tasks[i] for i in range(n) if mask >> i & 1]
        hours = sum(t.duration for t in subset)
        if hours > total_hours + EPS:
            continue
        ordered = edf_order(subset)
        if not is_feasible(ordered, hours_per_day):
            continue
        score = (sum(t.priority for t in subset), -hours)
        if score > best_score:
            best_score, best_subset = score, ordered

    chosen_names = {t.name for t in best_subset}
    deferred = [(t, "Not part of the best possible subset")
                for t in tasks if t.name not in chosen_names]
    return _make_result("Optimal (brute force)", best_subset, deferred,
                        total_hours, hours_per_day)


# ----------------------------------------------------------------------
# Day-by-day plan
# ----------------------------------------------------------------------
def daily_plan(items, hours_per_day):
    """Split the scheduled tasks over days.
    Returns a list of (day_index, task_name, hours); day_index 0 = today."""
    plan = []
    day, free = 0, hours_per_day
    for item in items:
        left = item.task.duration
        while left > EPS:
            chunk = min(left, free)
            plan.append((day, item.task.name, chunk))
            left -= chunk
            free -= chunk
            if free <= EPS:
                day += 1
                free = hours_per_day
    return plan


# ----------------------------------------------------------------------
# Demo data  (name, duration hours, deadline in days from today, priority)
# ----------------------------------------------------------------------
SAMPLES = {
    "standard": {
        "label": "Standard demo",
        "total_hours": 14.0,
        "hours_per_day": 4.0,
        "tasks": [
            ("Resume Update", 1.0, 7, 1),
            ("Python Practice", 2.0, 6, 2),
            ("Mock Test Revision", 5.0, 0, 3),
            ("Computer Networks Notes", 4.0, 4, 3),
            ("Blockchain Mini Project", 5.0, 5, 5),
            ("Maths Problem Set", 3.0, 3, 4),
            ("DBMS Normalization Revision", 2.0, 2, 4),
            ("DAA Assignment", 3.0, 1, 5),
        ],
    },
    "limitation": {
        "label": "Greedy-is-not-optimal demo",
        "total_hours": 10.0,
        "hours_per_day": 4.0,
        "tasks": [
            ("Unit 1 Long Revision", 6.0, 5, 4),
            ("Unit 2 Revision", 5.0, 5, 3),
            ("Unit 3 Revision", 5.0, 5, 3),
        ],
    },
}
