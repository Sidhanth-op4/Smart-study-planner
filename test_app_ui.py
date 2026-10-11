"""
test_app_ui.py - headless smoke tests of the Streamlit screen using Streamlit's AppTest.
Run:  python -m pytest -v
(These check the app logic and messages; they are NOT screenshots of a real browser.)
"""
from datetime import date, timedelta

from streamlit.testing.v1 import AppTest

TIMEOUT = 30


def new_app():
    at = AppTest.from_file("app.py", default_timeout=TIMEOUT)
    at.run()
    return at


def metric_values(at):
    return {m.label: m.value for m in at.metric}


def submit(at):
    next(b for b in at.button if "Add task" in b.label).click().run()


def test_UI01_empty_start_shows_hint_and_no_exception():
    at = new_app()
    assert not at.exception
    assert any("No tasks yet" in i.value for i in at.info)


def test_UI02_sample_button_fills_tasks_and_shows_results():
    at = new_app()
    at.button(key="btn_sample").click().run()
    assert not at.exception
    m = metric_values(at)
    assert m["Selected tasks"] == "5" and m["Deferred tasks"] == "3"
    assert m["Scheduled hours"] == "14" and m["Remaining hours"] == "0"


def test_UI03_reset_clears_everything():
    at = new_app()
    at.button(key="btn_sample").click().run()
    at.button(key="btn_reset").click().run()
    assert not at.exception
    assert any("No tasks yet" in i.value for i in at.info)
    assert at.session_state["tasks"] == []


def test_UI04_add_valid_task():
    at = new_app()
    at.text_input(key="f_name").set_value("Read DAA notes")
    at.number_input(key="f_duration").set_value(2.0)
    at.slider(key="f_priority").set_value(4)
    submit(at)
    assert not at.exception and not at.error
    assert len(at.session_state["tasks"]) == 1
    assert metric_values(at)["Selected tasks"] == "1"


def test_UI05_zero_duration_rejected():
    at = new_app()
    at.text_input(key="f_name").set_value("Bad task")
    at.number_input(key="f_duration").set_value(0.0)
    submit(at)
    assert any("greater than 0" in e.value for e in at.error)
    assert at.session_state["tasks"] == []


def test_UI06_negative_duration_and_empty_name_rejected():
    at = new_app()
    at.number_input(key="f_duration").set_value(-1.0)
    submit(at)
    messages = " ".join(e.value for e in at.error)
    assert "name cannot be empty" in messages and "greater than 0" in messages


def test_UI07_past_deadline_rejected():
    at = new_app()
    at.text_input(key="f_name").set_value("Old task")
    at.date_input(key="f_deadline").set_value(date.today() - timedelta(days=1))
    submit(at)
    assert any("before today" in e.value for e in at.error)


def test_UI08_insufficient_time_shows_warning():
    at = new_app()
    at.button(key="btn_sample").click().run()
    at.number_input(key="total_hours").set_value(0.5).run()
    assert not at.exception
    assert metric_values(at)["Selected tasks"] == "0"
    assert any("No task could be scheduled" in w.value for w in at.warning)


def test_UI09_invalid_total_hours_shows_error():
    at = new_app()
    at.button(key="btn_sample").click().run()
    at.number_input(key="total_hours").set_value(0.0).run()
    assert any("greater than 0" in e.value for e in at.error)


def test_UI10_limitation_demo_warns_greedy_not_optimal():
    at = new_app()
    at.button(key="btn_limit").click().run()
    assert not at.exception
    assert any("NOT optimal" in w.value for w in at.warning)
