# Test Cases

All automated test IDs below are the same as the function names in `test_scheduler.py` (`TC..`) and `test_app_ui.py` (`UI..`).

**How the "Actual" column was obtained:** the algorithm inputs were run through `scheduler.py` and the values printed; the whole suite was then run with `python -m pytest -v`.

| Run information | |
|---|---|
| Command | `python -m pytest -v` |
| Environment | Python 3.12.3, pytest 9.1.1, Streamlit 1.65.0, Linux |
| Result | **59 passed, 0 failed** (49 in `test_scheduler.py`, 10 in `test_app_ui.py`) |

Notation: a task is written *(name, hours, deadline day, importance)*. Deadline day 0 = today. Unless stated otherwise, study hours per day = 4. "H" = total available hours.

## Part A — Algorithm tests (`test_scheduler.py`)

| ID | Description | Input | Expected | Actual | Result |
|---|---|---|---|---|---|
| TC01 | No tasks | tasks = [ ], H = 10 | nothing selected or deferred; used 0; remaining 10 | selected [ ], deferred [ ], used 0, remaining 10 | PASS |
| TC02 | One task fits | (A, 2, 1, 3), H = 5 | A selected; remaining 3; no late task | selected [A], remaining 3, late 0 | PASS |
| TC03 | Task longer than budget | (A, 6, 5, 3), H = 5 | nothing selected; A deferred "Not enough remaining study hours" | selected [ ]; A deferred: Not enough remaining study hours | PASS |
| TC04 | Exact fit | (A, 2, 3, 3), (B, 3, 3, 2), H = 5 | both selected; used 5; remaining 0 | selected [A, B]; used 5; remaining 0 | PASS |
| TC05 | Higher importance per hour wins | A (4 h, imp 5, ratio 1.25), B (2 h, imp 4, ratio 2.0), H = 4 | only B selected | selected [B]; A deferred (not enough hours) | PASS |
| TC06 | Equal ratio, earlier deadline wins | A (2 h, due 6, imp 2), B (2 h, due 5, imp 2), H = 2 | only B selected | selected [B] | PASS |
| TC07 | Study order is Earliest Deadline First | Late (1, due 6, 5), Soon (1, due 1, 1), Mid (1, due 3, 3), H = 10 | order Soon, Mid, Late | [Soon, Mid, Late] | PASS |
| TC08 | Task cannot meet own deadline | Impossible (5 h, due today, imp 5), H = 20 | deferred "Deadline too close…" | deferred: Deadline too close: it cannot finish in time even if started first | PASS |
| TC09 | Task would miss its deadline after an accepted task | A (4 h, due today, imp 5), B (1 h, due today, imp 1), H = 20 | A selected, B deferred "Adding it would make another task miss its deadline" | selected [A]; B deferred with that reason | PASS |
| TC10 | Order by deadline, not by acceptance order | X (3 h, due 1, imp 5), Z (2 h, due 0, imp 1), H = 20 | order Z, X; no late task | [Z, X]; late 0 | PASS |
| TC11 | 300 random inputs give valid schedules | random tasks and budgets (fixed seed) | budget never exceeded, no late task, every task either selected or deferred exactly once | all 300 satisfied | PASS |
| TC12 | Greedy never beats the exact optimum | 300 random small inputs (fixed seed) | greedy points ≤ brute-force points | all 300 satisfied | PASS |
| TC13 | **Counter-example (limitation)** | A (6 h, imp 4), B (5 h, imp 3), C (5 h, imp 3), deadlines far, H = 10 | greedy = [A] with 4 points; optimal = [B, C] with 6 points | greedy [A], 4 points; optimal [B, C], 6 points | PASS |
| TC28 | Result is maximal | 300 random inputs (fixed seed) | for every deferred task, adding it would break the budget or a deadline | all 300 satisfied | PASS |

## Part B — Validation tests

| ID | Description | Input | Expected | Actual | Result |
|---|---|---|---|---|---|
| TC14 | Valid task | ("Read notes", 2.5 h, day 3, imp 4) | no error | [ ] | PASS |
| TC15 | Invalid name (4 cases) | "", "   ", None, 61 characters | error | "Task name cannot be empty." / "Task name must be at most 60 characters." | PASS |
| TC16 | Invalid duration (9 cases) | 0, −2, 0.0, 100.5, NaN, infinity, "abc", None, True | error | "Duration must be greater than 0 hours." (0, −2, 0.0); "Duration cannot be more than 100 hours." (100.5); "Duration must be a number of hours." (NaN, "abc") | PASS |
| TC17 | Invalid importance (6 cases) | 0, 6, −1, 2.5, "3", None | error | "Priority must be a whole number from 1 to 5." | PASS |
| TC18 | Deadline in the past | deadline day −1 | error | "Deadline cannot be before today." | PASS |
| TC19 | Duplicate name (case-insensitive) | "daa assignment" when "DAA Assignment" exists | error | "A task named 'daa assignment' already exists." | PASS |
| TC20 | Invalid settings (6 cases) | (H, h/day) = (0, 4), (−5, 4), (10, 0), (10, 25), ("x", 4), (10, None) | error | "Total available study hours must be greater than 0." / "Study hours per day must be greater than 0 and at most 24." | PASS |
| TC21 | Valid settings | H = 14, 4 h/day | no error | [ ] | PASS |

## Part C — Plan, baseline, brute force, sample data

| ID | Description | Input | Expected | Actual | Result |
|---|---|---|---|---|---|
| TC22 | Long task split over days | Big (6 h, due 3, imp 5), Small (1 h, due 3, imp 1), H = 10, 4 h/day | Day 1: Big 4 h; Day 2: Big 2 h, Small 1 h | [(day 1, Big, 4), (day 2, Big, 2), (day 2, Small, 1)] | PASS |
| TC23 | Baseline follows entry order and can miss a deadline | First (3 h, due 5, imp 1), Urgent (3 h, due today, imp 5), H = 10 | baseline order First, Urgent with 1 late task; greedy order Urgent, First with 0 late | baseline [First, Urgent], late 1 (Urgent ends at hour 6, due by hour 4); greedy [Urgent, First], late 0 | PASS |
| TC24 | Brute force refuses large input | 13 tasks | `ValueError` | `ValueError` raised | PASS |
| TC25 | Empty input for baseline and brute force | [ ] | empty results | empty results | PASS |
| TC26 | Standard demo data | 8 sample tasks, H = 14, 4 h/day | greedy: DAA Assignment, DBMS Normalization Revision, Maths Problem Set, Blockchain Mini Project, Resume Update; 14 h; 19 points; deferred: Python Practice, Computer Networks Notes, Mock Test Revision. Baseline: 13 points, 2 late, 6 on-time points. Optimal: 19 points | exactly as expected | PASS |
| TC27 | Limitation demo data | 3 tasks, H = 10 | greedy 4 points, optimal 6 points | greedy 4, optimal 6 | PASS |

## Part D — Screen tests (`test_app_ui.py`, Streamlit AppTest, headless)

These check the screen logic without a browser.

| ID | Description | Steps | Expected | Result |
|---|---|---|---|---|
| UI01 | Empty start | open app | no exception; message "No tasks yet…" | PASS |
| UI02 | Sample data | click **Load sample tasks** | Selected 5, Deferred 3, Scheduled hours 14, Remaining hours 0 | PASS |
| UI03 | Reset | load sample, click **Reset** | task list empty; hint message shown | PASS |
| UI04 | Add valid task | name "Read DAA notes", 2 h, importance 4, **Add task** | no error; 1 task stored; Selected 1 | PASS |
| UI05 | Zero duration | duration 0, **Add task** | error "greater than 0"; no task stored | PASS |
| UI06 | Negative duration and empty name | duration −1, empty name | both errors shown | PASS |
| UI07 | Past deadline | deadline = yesterday | error "before today" | PASS |
| UI08 | Insufficient time | sample data, H = 0.5 | Selected 0; warning "No task could be scheduled" | PASS |
| UI09 | Invalid total hours | sample data, H = 0 | error "greater than 0" | PASS |
| UI10 | Limitation demo | click **Load 'greedy is not optimal' demo** | warning that greedy is NOT optimal | PASS |

## Part E — Manual browser checks (NOT run by the author of this file)

These need a real browser, so they were **not** executed. Run them yourself, tick the box and attach the screenshots from `SCREENSHOT_CHECKLIST.md`.

| ID | Check | Done | Observed result (fill in) |
|---|---|---|---|
| M01 | `streamlit run app.py` opens the page at http://localhost:8501 | [ ] | |
| M02 | The banner, sidebar and the tabs display correctly | [ ] | |
| M03 | The date picker accepts a future date and the new task appears in the table | [ ] | |
| M04 | **Remove** deletes the selected task | [ ] | |
| M05 | Changing **Total available study hours** immediately changes the results | [ ] | |
| M06 | Layout is readable on a narrow window | [ ] | |

## Note on the server start-up check

`streamlit run app.py --server.headless true` was started once in the build environment; its health endpoint and home page both returned HTTP 200. This shows the server starts, not that the page looks right in a browser.
