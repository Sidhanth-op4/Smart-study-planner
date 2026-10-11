# 📚 Smart Study Planner — Greedy-Based Task Scheduling System

DAA (Design and Analysis of Algorithms) Lab mini project.
A small Streamlit web app that decides **which study tasks to do and in what order**, given each task's duration, deadline and importance, and the hours you have available. It uses a **greedy algorithm** and explains its rule, its complexity and its limits.

* Language: Python 3  |  Interface: Streamlit  |  No database  |  Tests: pytest
* Built and tested on **Python 3.12.3** with **Streamlit 1.65.0** and pytest 9.1.1. Other recent Python 3 versions should work but were not tested.

## Features

* Add tasks: name, estimated hours, deadline date, importance (1–5).
* Enter total available study hours and study hours per day.
* Shows selected tasks, deferred tasks (with reasons), total scheduled hours, remaining hours and a day-by-day schedule.
* Sample data, a "greedy is not optimal" demo, and a reset button.
* Input validation: no tasks, empty/duplicate names, zero/negative/non-numeric durations, importance out of range, past deadlines, invalid hours, not enough time.
* Comparison of the greedy plan with a first-come-first-served baseline and (for ≤ 12 tasks) the exact optimum found by brute force.

## The greedy rule (short)

1. Rank tasks by **importance ÷ duration** (highest first; ties → earlier deadline, shorter task, name).
2. Go through the list once. **Accept** a task only if it fits in the remaining hours **and** the accepted tasks can still all meet their deadlines. Otherwise **defer** it.
3. Study the accepted tasks in **Earliest Deadline First** order.

> **Limitation:** greedy scheduling is a heuristic. It always gives a *valid* schedule but does **not** guarantee the globally optimal one for every combination of deadlines and priorities. Try the *"greedy is not optimal" demo* in the sidebar. Full details are in `REPORT.md`.

## Project structure

```
smart-study-planner/
├── app.py                  Streamlit user interface
├── scheduler.py            Algorithm code (greedy, baseline, brute force, validation)
├── test_scheduler.py       Algorithm tests (pytest)
├── test_app_ui.py          Headless screen tests (Streamlit AppTest)
├── requirements.txt        Python packages
├── README.md               This file
├── REPORT.md               Full project report (source)
├── REPORT.pdf              Report exported to PDF (no screenshots yet, see below)
├── VIVA.md                 30 viva questions and answers
├── TEST_CASES.md           Test cases with expected and actual results
├── SCREENSHOT_CHECKLIST.md Screenshots you need to take
├── docs/
│   ├── flowchart.dot       Flowchart source (Graphviz)
│   ├── flowchart.png       Flowchart image used in the report
│   └── report.css          Style used for the PDF
└── .streamlit/config.toml  Theme colour
```

## Setup and run (exact commands)

Install Python 3 first and check it: `python --version` (on macOS/Linux you may need `python3`).

**Windows (Command Prompt or PowerShell)**

```
cd smart-study-planner
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

(If PowerShell blocks `activate`, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once in that window, or use Command Prompt.)

**macOS / Linux**

```
cd smart-study-planner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The browser opens at **http://localhost:8501**. If it does not, open that address yourself. Stop the app with `Ctrl + C` in the terminal.

## Run the tests

With the virtual environment active, in the project folder:

```
python -m pytest -v
```

On the machine where this project was built the result was **59 passed**. Run it yourself and use your own output in your report.

## How to use the app

1. Click **Load sample tasks** in the sidebar (or add your own in Step 1).
2. Set **Total available study hours** and **Study hours per day** in the sidebar.
3. Read the numbers and tabs under "3. Your study plan".
4. Click **Load 'greedy is not optimal' demo** and open the *Greedy vs baseline* tab to see a case where greedy loses to the optimum.
5. Click **Reset (clear everything)** to start again.

## Push to GitHub

Create an empty repository on github.com first (no README), then:

```
git init
git add .
git commit -m "Smart Study Planner: greedy task scheduling (DAA Lab mini project)"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

Replace `<your-username>` and `<your-repo-name>` with your own values. Make sure `venv/` is not uploaded (the included `.gitignore` already excludes it).

## Screenshots and the report PDF

* Take the screenshots listed in `SCREENSHOT_CHECKLIST.md` from your own running app and paste them into Section 15 of `REPORT.md`. Screenshots are not included because they must come from your own run.
* Fill in the title-page placeholders (faculty name, academic year, repository URL) in `REPORT.md`.
* **Create the report PDF.** Easiest: open `REPORT.md` in VS Code with the "Markdown PDF" extension, or any Markdown editor, and export to PDF. Command-line alternative (needs `pandoc` and `wkhtmltopdf` installed; this is how the included `REPORT.pdf` was made):

```
pandoc REPORT.md -f markdown -t html5 -s --embed-resources --metadata pagetitle="Smart Study Planner Report" --css docs/report.css --resource-path=. -o report.html
wkhtmltopdf --enable-local-file-access --page-size A4 --margin-top 18mm --margin-bottom 18mm --margin-left 16mm --margin-right 16mm report.html REPORT.pdf
```

## What was and was not verified

* Verified by running: the 59 automated tests passed, and `streamlit run app.py` started and answered HTTP 200 on its health and home endpoints.
* **Not verified:** how the page looks in a real browser. No browser was available in the build environment, so no screenshots were taken. Check the app yourself using Part E of `TEST_CASES.md`.
