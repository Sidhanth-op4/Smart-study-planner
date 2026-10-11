"""
app.py - Smart Study Planner (Streamlit web interface).
Run with:  streamlit run app.py
All scheduling logic lives in scheduler.py; this file only handles the screen.
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

import scheduler as sch

st.set_page_config(page_title="Smart Study Planner", page_icon="📚", layout="wide")


# ----------------------------------------------------------------------
# State helpers
# ----------------------------------------------------------------------
def init_state():
    st.session_state.setdefault("tasks", [])           # list of dicts
    st.session_state.setdefault("total_hours", 14.0)
    st.session_state.setdefault("hours_per_day", 4.0)


def load_sample(key):
    """Button callback: replace all tasks with a demo data set."""
    sample = sch.SAMPLES[key]
    today = date.today()
    st.session_state["tasks"] = [
        {"name": n, "duration": d, "deadline": today + timedelta(days=off), "priority": p}
        for (n, d, off, p) in sample["tasks"]
    ]
    st.session_state["total_hours"] = sample["total_hours"]
    st.session_state["hours_per_day"] = sample["hours_per_day"]


def reset_all():
    """Button callback: clear every task and restore default settings."""
    st.session_state["tasks"] = []
    st.session_state["total_hours"] = 14.0
    st.session_state["hours_per_day"] = 4.0


def remove_task():
    name = st.session_state.get("remove_choice")
    st.session_state["tasks"] = [t for t in st.session_state["tasks"] if t["name"] != name]


def to_core_tasks(task_dicts, today):
    """Convert UI dictionaries to Task objects (deadline date -> day number)."""
    return [
        sch.Task(t["name"], t["duration"], (t["deadline"] - today).days, t["priority"])
        for t in task_dicts
    ]


def day_label(day_index, today):
    d = today + timedelta(days=day_index)
    return f"Day {day_index + 1} ({d.strftime('%a %d %b')})"


init_state()
today = date.today()

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown(
    """
    <div style="padding:1.1rem 1.4rem;border-radius:12px;
                background:linear-gradient(90deg,#4f46e5,#7c3aed);color:white;">
      <h1 style="margin:0;color:white;">📚 Smart Study Planner</h1>
      <div style="opacity:.9;">Greedy-Based Task Scheduling System &nbsp;|&nbsp; DAA Lab Mini Project</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# ----------------------------------------------------------------------
# Sidebar: settings and demo controls
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.number_input("Total available study hours", step=0.5, key="total_hours",
                    help="The overall time budget. Tasks that do not fit are deferred.")
    st.number_input("Study hours per day", step=0.5, key="hours_per_day",
                    help="Used to turn deadlines (dates) into a time limit on the study timeline.")
    st.divider()
    st.header("🧪 Demo")
    st.button("Load sample tasks", on_click=load_sample, args=("standard",), key="btn_sample")
    st.button("Load 'greedy is not optimal' demo", on_click=load_sample, args=("limitation",),
              key="btn_limit")
    st.button("Reset (clear everything)", on_click=reset_all, key="btn_reset")

# ----------------------------------------------------------------------
# Step 1: add a task
# ----------------------------------------------------------------------
st.subheader("1. Add a study task")
with st.form("add_task_form"):
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    name = c1.text_input("Task name", placeholder="e.g. DAA Assignment", key="f_name")
    duration = c2.number_input("Estimated duration (hours)", value=1.0, step=0.25, key="f_duration")
    deadline = c3.date_input("Deadline", value=today + timedelta(days=3), key="f_deadline")
    priority = c4.slider("Importance (1 = low, 5 = high)", 1, 5, 3, key="f_priority")
    submitted = st.form_submit_button("➕ Add task")

if submitted:
    existing = [t["name"] for t in st.session_state["tasks"]]
    errors = sch.validate_task(name, duration, (deadline - today).days, priority, existing)
    if errors:
        for e in errors:
            st.error(e)
    else:
        st.session_state["tasks"].append(
            {"name": name.strip(), "duration": float(duration),
             "deadline": deadline, "priority": int(priority)}
        )
        st.success(f"Added '{name.strip()}'.")

# ----------------------------------------------------------------------
# Step 2: task list
# ----------------------------------------------------------------------
st.subheader("2. Your tasks")
tasks_ui = st.session_state["tasks"]
if not tasks_ui:
    st.info("No tasks yet. Add a task above or click **Load sample tasks** in the sidebar.")
    st.stop()

table = pd.DataFrame(
    [{"Task": t["name"], "Duration (h)": t["duration"], "Deadline": t["deadline"],
      "Importance": t["priority"],
      "Priority per hour": round(t["priority"] / t["duration"], 2)} for t in tasks_ui]
)
st.dataframe(table, hide_index=True)

rc1, rc2 = st.columns([3, 1])
rc1.selectbox("Remove a task", [t["name"] for t in tasks_ui], key="remove_choice")
rc2.write("")
rc2.write("")
rc2.button("🗑️ Remove", on_click=remove_task, key="btn_remove")

# ----------------------------------------------------------------------
# Step 3: run the scheduler
# ----------------------------------------------------------------------
st.subheader("3. Your study plan")
total_hours = st.session_state["total_hours"]
hours_per_day = st.session_state["hours_per_day"]

budget_errors = sch.validate_budget(total_hours, hours_per_day)
if budget_errors:
    for e in budget_errors:
        st.error(e)
    st.stop()

core_tasks = to_core_tasks(tasks_ui, today)
greedy = sch.greedy_schedule(core_tasks, total_hours, hours_per_day)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Selected tasks", len(greedy.items))
m2.metric("Deferred tasks", len(greedy.deferred))
m3.metric("Scheduled hours", f"{greedy.used_hours:g}")
m4.metric("Remaining hours", f"{greedy.remaining_hours:g}")
st.progress(min(greedy.used_hours / total_hours, 1.0),
            text=f"{greedy.used_hours:g} of {total_hours:g} hours used")

if not greedy.items:
    st.warning("No task could be scheduled. Increase the available hours, "
               "shorten the tasks, or move the deadlines further away.")
elif greedy.deferred:
    st.warning(f"{len(greedy.deferred)} task(s) were deferred. See the 'Deferred tasks' tab for the reasons.")
else:
    st.success("All tasks fit in your available time and meet their deadlines.")

tab_plan, tab_sel, tab_def, tab_cmp, tab_algo = st.tabs(
    ["📅 Study schedule", "✅ Selected tasks", "⏳ Deferred tasks",
     "⚖️ Greedy vs baseline", "📖 Algorithm & limitations"]
)

with tab_plan:
    if greedy.items:
        plan = sch.daily_plan(greedy.items, hours_per_day)
        st.dataframe(
            pd.DataFrame([{"Day": day_label(d, today), "Task": n, "Hours": round(h, 2)}
                          for d, n, h in plan]),
            hide_index=True)
        st.caption("Tasks are studied in Earliest-Deadline-First order. "
                   "A long task may continue on the next day.")
    else:
        st.info("Nothing to schedule.")

with tab_sel:
    if greedy.items:
        st.dataframe(
            pd.DataFrame([{
                "Order": k + 1, "Task": i.task.name, "Hours": i.task.duration,
                "Importance": i.task.priority,
                "Deadline": today + timedelta(days=i.task.deadline_day),
                "Finishes on": today + timedelta(days=i.finish_day),
                "On time?": "Yes" if i.on_time else "No",
            } for k, i in enumerate(greedy.items)]),
            hide_index=True)
    else:
        st.info("No tasks selected.")

with tab_def:
    if greedy.deferred:
        st.dataframe(
            pd.DataFrame([{"Task": t.name, "Hours": t.duration, "Importance": t.priority,
                           "Deadline": today + timedelta(days=t.deadline_day), "Reason": why}
                          for t, why in greedy.deferred]),
            hide_index=True)
    else:
        st.success("No deferred tasks.")

with tab_cmp:
    st.write("The baseline takes tasks **in the order you entered them** while they fit "
             "in the hours, ignoring importance and deadlines.")
    results = [greedy, sch.baseline_fcfs(core_tasks, total_hours, hours_per_day)]
    if len(core_tasks) <= sch.MAX_BRUTE_FORCE_TASKS:
        results.append(sch.brute_force_optimal(core_tasks, total_hours, hours_per_day))
    else:
        st.caption(f"Exact optimum is only computed for {sch.MAX_BRUTE_FORCE_TASKS} tasks or fewer.")
    st.dataframe(
        pd.DataFrame([{
            "Strategy": r.strategy, "Tasks scheduled": len(r.items),
            "Hours used": r.used_hours, "Importance points": r.total_priority,
            "Tasks missing deadline": r.late_count,
            "On-time importance points": r.on_time_priority,
        } for r in results]),
        hide_index=True)
    st.caption("Optimal = best subset found by trying all 2^n subsets (small inputs only). "
               "If Greedy scores lower than Optimal, that is the heuristic's limitation.")
    if len(results) == 3 and greedy.on_time_priority < results[2].on_time_priority:
        st.warning("For this input the greedy plan is NOT optimal: a better subset exists.")

with tab_algo:
    st.markdown(
        """
**Greedy rule**
1. Rank tasks by **importance ÷ duration** (importance points per hour), highest first.
   Ties: earlier deadline, then shorter task.
2. Go through the ranked list once. **Accept** a task only if it fits in the remaining hours
   *and* every accepted task can still meet its deadline. Otherwise **defer** it.
3. Study the accepted tasks in **Earliest Deadline First** order.

**Limitations (please read)**
- Greedy scheduling is a **heuristic**. It does **not** guarantee the globally optimal schedule
  for every combination of deadlines and priorities.
- It never reconsiders a choice, so one early pick can block a better combination
  (try the *'greedy is not optimal' demo*).
- The underlying problem contains the 0/1 knapsack problem, which is NP-hard,
  so no simple greedy rule can be optimal for all inputs.
- Durations are estimates; the plan is only as good as the numbers you enter.
        """
    )
