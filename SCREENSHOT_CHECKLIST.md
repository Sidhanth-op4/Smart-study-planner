# Screenshot Checklist for the Final Report

I could not capture screenshots for you: the environment this project was built in has no web browser, so a screenshot of the real app would have been invented. Take the screenshots below on your own computer from your own running copy, so that every picture is genuine.

**Setup:** run the app (`streamlit run app.py`), open http://localhost:8501, use a full browser window, and zoom to 100%. Save the files in a folder `screenshots/` using the file names below, then paste them into `REPORT.md` / the PDF under Section 15 with a figure number and caption.

Tick each box when done.

## A. Application screenshots

| Done | File name | What to show | Exact steps |
|---|---|---|---|
| [ ] | `01_home_empty.png` | First screen, no tasks, hint message visible | Start the app, or click **Reset (clear everything)** |
| [ ] | `02_add_task_valid.png` | A valid task entered and the success message | Type `Read DAA notes`, 2 hours, deadline 3 days ahead, importance 4, click **Add task** |
| [ ] | `03_validation_error.png` | Error for an invalid duration | Type any name, set duration `0`, click **Add task** (error "Duration must be greater than 0 hours.") |
| [ ] | `04_validation_error_name.png` | Error for empty name and negative duration | Leave name empty, duration `-1`, click **Add task** |
| [ ] | `05_sample_loaded.png` | Task table after loading sample data | Click **Load sample tasks** |
| [ ] | `06_results_summary.png` | The four numbers (Selected 5, Deferred 3, Scheduled hours 14, Remaining hours 0) and the progress bar | Scroll to "3. Your study plan" after loading the sample |
| [ ] | `07_study_schedule_tab.png` | Day-by-day schedule | Tab **Study schedule** |
| [ ] | `08_selected_tasks_tab.png` | Selected tasks in order | Tab **Selected tasks** |
| [ ] | `09_deferred_tasks_tab.png` | Deferred tasks with reasons | Tab **Deferred tasks** |
| [ ] | `10_comparison_tab.png` | Greedy vs baseline vs optimal table | Tab **Greedy vs baseline** |
| [ ] | `11_limitation_demo.png` | Greedy 4 points vs optimal 6 points and the warning "NOT optimal" | Click **Load 'greedy is not optimal' demo**, open **Greedy vs baseline** |
| [ ] | `12_insufficient_time.png` | Warning when nothing fits | Load sample, set **Total available study hours** to `0.5` |
| [ ] | `13_invalid_budget.png` | Error for invalid total hours | Set **Total available study hours** to `0` |
| [ ] | `14_algorithm_tab.png` | Rule and limitations text | Tab **Algorithm & limitations** |
| [ ] | `15_reset.png` | App back to empty state | Click **Reset (clear everything)** |

## B. Terminal / code screenshots

| Done | File name | What to show | Exact command |
|---|---|---|---|
| [ ] | `16_install.png` | Successful dependency install | `pip install -r requirements.txt` |
| [ ] | `17_streamlit_run.png` | Terminal showing the local URL | `streamlit run app.py` |
| [ ] | `18_pytest_pass.png` | All tests passing (59 passed on the machine this was built on; your count should match if you have the same files) | `python -m pytest -v` |
| [ ] | `19_scheduler_code.png` | The `greedy_schedule` function in your editor | Open `scheduler.py` |

## C. GitHub screenshots

| Done | File name | What to show |
|---|---|---|
| [ ] | `20_github_repo.png` | Repository home page: file list and README preview |
| [ ] | `21_github_commits.png` | Commit history page |
| [ ] | `22_github_readme.png` | Rendered README with the setup commands |

## D. Final check before submission

* [ ] Every screenshot shows your real run (not an edited picture).
* [ ] The repository URL is filled in on the title page of the report.
* [ ] Faculty name and academic year are filled in on the title page.
* [ ] Report exported to PDF after the screenshots were added (see README, "Create the report PDF").
