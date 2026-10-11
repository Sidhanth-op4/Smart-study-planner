"""
test_scheduler.py - unit tests for the scheduling algorithm (no Streamlit needed).
Run:  python -m pytest -v
Test IDs (TC01...) match TEST_CASES.md.
"""
import math
import random

import pytest

import scheduler as sch
from scheduler import Task

HPD = 4.0  # study hours per day used in most tests


def names(result):
    return [i.task.name for i in result.items]


def deferred_reasons(result):
    return {t.name: why for t, why in result.deferred}


# ---------------------------- Greedy behaviour ----------------------------
def test_TC01_no_tasks():
    r = sch.greedy_schedule([], 10, HPD)
    assert r.items == [] and r.deferred == []
    assert r.used_hours == 0 and r.remaining_hours == 10


def test_TC02_single_task_fits():
    r = sch.greedy_schedule([Task("A", 2, 1, 3)], 5, HPD)
    assert names(r) == ["A"] and r.remaining_hours == 3 and r.late_count == 0


def test_TC03_single_task_longer_than_budget():
    r = sch.greedy_schedule([Task("A", 6, 5, 3)], 5, HPD)
    assert r.items == []
    assert deferred_reasons(r)["A"] == "Not enough remaining study hours"


def test_TC04_exact_fit_uses_whole_budget():
    r = sch.greedy_schedule([Task("A", 2, 3, 3), Task("B", 3, 3, 2)], 5, HPD)
    assert sorted(names(r)) == ["A", "B"]
    assert r.used_hours == 5 and r.remaining_hours == 0


def test_TC05_higher_priority_per_hour_wins_when_only_one_fits():
    # A: 5/4 = 1.25 per hour, B: 4/2 = 2.0 per hour. Budget allows only one of them.
    r = sch.greedy_schedule([Task("A", 4, 5, 5), Task("B", 2, 5, 4)], 4, HPD)
    assert names(r) == ["B"]


def test_TC06_tie_in_ratio_broken_by_earlier_deadline():
    # Both have ratio 1.0. Budget fits one. B has the earlier deadline.
    r = sch.greedy_schedule([Task("A", 2, 6, 2), Task("B", 2, 5, 2)], 2, HPD)
    assert names(r) == ["B"]


def test_TC07_selected_tasks_are_in_earliest_deadline_first_order():
    tasks = [Task("Late", 1, 6, 5), Task("Soon", 1, 1, 1), Task("Mid", 1, 3, 3)]
    r = sch.greedy_schedule(tasks, 10, HPD)
    assert names(r) == ["Soon", "Mid", "Late"]


def test_TC08_task_that_cannot_meet_own_deadline_is_deferred():
    # Due today (day 0) but needs 5 h and only 4 h per day exist today.
    r = sch.greedy_schedule([Task("Impossible", 5, 0, 5)], 20, HPD)
    assert r.items == []
    assert deferred_reasons(r)["Impossible"].startswith("Deadline too close")


def test_TC09_task_that_would_miss_its_deadline_is_deferred():
    # A (4h, due today, ratio 1.25) is accepted first and fills today's 4 hours.
    # B (1h, due today, ratio 1.0) could finish alone, but after A it would end at hour 5 > 4.
    r = sch.greedy_schedule([Task("A", 4, 0, 5), Task("B", 1, 0, 1)], 20, HPD)
    assert names(r) == ["A"]
    assert "miss its deadline" in deferred_reasons(r)["B"]


def test_TC10_order_is_by_deadline_not_by_acceptance_order():
    # X (ratio 1.67) is accepted first, Z (ratio 0.5) second, but Z is due earlier,
    # so the final plan is Z then X, and both finish on time.
    r = sch.greedy_schedule([Task("X", 3, 1, 5), Task("Z", 2, 0, 1)], 20, HPD)
    assert names(r) == ["Z", "X"] and r.late_count == 0


def test_TC11_random_inputs_always_give_valid_schedules():
    rng = random.Random(2026)
    for _ in range(300):
        n = rng.randint(0, 9)
        tasks = [Task(f"T{i}", rng.choice([0.5, 1, 1.5, 2, 3, 4, 6]),
                      rng.randint(0, 6), rng.randint(1, 5)) for i in range(n)]
        budget = rng.choice([1, 3, 5, 8, 12, 20])
        r = sch.greedy_schedule(tasks, budget, HPD)
        assert r.used_hours <= budget + 1e-9           # budget respected
        assert r.late_count == 0                       # every chosen task on time
        chosen = {i.task.name for i in r.items}
        dropped = {t.name for t, _ in r.deferred}
        assert chosen | dropped == {t.name for t in tasks}   # nobody lost
        assert not chosen & dropped                          # nobody twice


def test_TC12_greedy_never_beats_the_exact_optimum():
    rng = random.Random(7)
    for _ in range(300):
        n = rng.randint(1, 8)
        tasks = [Task(f"T{i}", rng.choice([1, 2, 3, 4, 5, 6]),
                      rng.randint(0, 5), rng.randint(1, 5)) for i in range(n)]
        budget = rng.choice([4, 6, 8, 10, 14])
        g = sch.greedy_schedule(tasks, budget, HPD)
        o = sch.brute_force_optimal(tasks, budget, HPD)
        assert g.total_priority <= o.total_priority


def test_TC13_greedy_is_not_always_optimal_counterexample():
    tasks = [Task("A", 6, 5, 4), Task("B", 5, 5, 3), Task("C", 5, 5, 3)]
    g = sch.greedy_schedule(tasks, 10, HPD)
    o = sch.brute_force_optimal(tasks, 10, HPD)
    assert names(g) == ["A"] and g.total_priority == 4
    assert sorted(names(o)) == ["B", "C"] and o.total_priority == 6


# ------------------------------- Validation -------------------------------
def test_TC14_valid_task_has_no_errors():
    assert sch.validate_task("Read notes", 2.5, 3, 4, []) == []


@pytest.mark.parametrize("bad_name", ["", "   ", None, "x" * 61])
def test_TC15_invalid_name(bad_name):
    assert sch.validate_task(bad_name, 1, 1, 3, [])


@pytest.mark.parametrize("bad", [0, -2, 0.0, 100.5, float("nan"), float("inf"), "abc", None, True])
def test_TC16_invalid_duration(bad):
    assert sch.validate_task("A", bad, 1, 3, [])


@pytest.mark.parametrize("bad", [0, 6, -1, 2.5, "3", None])
def test_TC17_invalid_priority(bad):
    assert sch.validate_task("A", 1, 1, bad, [])


def test_TC18_deadline_in_the_past_rejected():
    assert any("before today" in e for e in sch.validate_task("A", 1, -1, 3, []))


def test_TC19_duplicate_name_rejected_case_insensitive():
    assert sch.validate_task("daa assignment", 1, 1, 3, ["DAA Assignment"])


@pytest.mark.parametrize("total,hpd", [(0, 4), (-5, 4), (10, 0), (10, 25), ("x", 4), (10, None)])
def test_TC20_invalid_budget_settings(total, hpd):
    assert sch.validate_budget(total, hpd)


def test_TC21_valid_budget_settings():
    assert sch.validate_budget(14, 4) == []


# ------------------------ Plan, baseline, brute force ------------------------
def test_TC22_daily_plan_splits_long_task_over_days():
    r = sch.greedy_schedule([Task("Big", 6, 3, 5), Task("Small", 1, 3, 1)], 10, HPD)
    plan = sch.daily_plan(r.items, HPD)
    assert plan == [(0, "Big", 4.0), (1, "Big", 2.0), (1, "Small", 1.0)]


def test_TC23_baseline_follows_entry_order_and_can_miss_deadlines():
    tasks = [Task("First", 3, 5, 1), Task("Urgent", 3, 0, 5)]
    b = sch.baseline_fcfs(tasks, 10, HPD)
    assert names(b) == ["First", "Urgent"]
    assert b.late_count == 1          # Urgent finishes at hour 6 but is due by hour 4
    g = sch.greedy_schedule(tasks, 10, HPD)
    assert names(g) == ["Urgent", "First"] and g.late_count == 0


def test_TC24_brute_force_refuses_large_input():
    tasks = [Task(f"T{i}", 1, 5, 1) for i in range(sch.MAX_BRUTE_FORCE_TASKS + 1)]
    with pytest.raises(ValueError):
        sch.brute_force_optimal(tasks, 100, HPD)


def test_TC25_empty_input_for_baseline_and_brute_force():
    assert sch.baseline_fcfs([], 5, HPD).items == []
    assert sch.brute_force_optimal([], 5, HPD).items == []


def test_TC26_standard_demo_data():
    d = sch.SAMPLES["standard"]
    tasks = [Task(*t) for t in d["tasks"]]
    g = sch.greedy_schedule(tasks, d["total_hours"], d["hours_per_day"])
    assert names(g) == ["DAA Assignment", "DBMS Normalization Revision", "Maths Problem Set",
                        "Blockchain Mini Project", "Resume Update"]
    assert g.used_hours == 14 and g.remaining_hours == 0 and g.total_priority == 19
    assert set(deferred_reasons(g)) == {"Python Practice", "Computer Networks Notes",
                                        "Mock Test Revision"}
    b = sch.baseline_fcfs(tasks, d["total_hours"], d["hours_per_day"])
    assert b.total_priority == 13 and b.late_count == 2 and b.on_time_priority == 6
    o = sch.brute_force_optimal(tasks, d["total_hours"], d["hours_per_day"])
    assert o.total_priority == 19


def test_TC27_limitation_demo_data():
    d = sch.SAMPLES["limitation"]
    tasks = [Task(*t) for t in d["tasks"]]
    g = sch.greedy_schedule(tasks, d["total_hours"], d["hours_per_day"])
    o = sch.brute_force_optimal(tasks, d["total_hours"], d["hours_per_day"])
    assert g.total_priority == 4 and o.total_priority == 6


def test_TC28_final_schedule_is_maximal_no_deferred_task_can_still_be_added():
    """Every deferred task really could not be added to the final set."""
    rng = random.Random(99)
    for _ in range(300):
        n = rng.randint(1, 9)
        tasks = [Task(f"T{i}", rng.choice([0.5, 1, 2, 3, 4, 6]),
                      rng.randint(0, 6), rng.randint(1, 5)) for i in range(n)]
        budget = rng.choice([2, 5, 8, 12])
        r = sch.greedy_schedule(tasks, budget, HPD)
        chosen = [i.task for i in r.items]
        for t, _why in r.deferred:
            too_long = r.used_hours + t.duration > budget + 1e-9
            breaks_deadline = not sch.is_feasible(sch.edf_order(chosen + [t]), HPD)
            assert too_long or breaks_deadline
