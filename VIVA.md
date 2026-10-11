# Viva Questions and Answers — Smart Study Planner

Answers are written to match this project's actual code (`scheduler.py`, `app.py`).

## A. Basics and problem

**Q1. What problem does your project solve?**
A student has many study tasks but limited hours. The program chooses which tasks to study and in what order so that the total hours stay within the budget, every chosen task meets its deadline, and the total importance of the chosen tasks is as high as possible. Tasks that do not fit are deferred with a reason.

**Q2. What are the inputs and outputs?**
Input: for each task a name, duration in hours, deadline date and importance 1–5; plus total available hours and study hours per day. Output: selected tasks in study order, deferred tasks with reasons, total scheduled hours, remaining hours, and a day-by-day plan.

**Q3. What is a greedy algorithm?**
An algorithm that builds a solution step by step and, at each step, makes the choice that looks best at that moment and never undoes it. It is usually fast and simple, but it is optimal only for problems that have the greedy-choice property.

**Q4. What is your greedy rule?**
Rank tasks by importance ÷ duration (importance per hour), highest first. Accept a task only if it fits in the remaining hours and the accepted tasks can still meet all deadlines. Finally order the accepted tasks by Earliest Deadline First.

**Q5. Why did you choose importance per hour?**
It measures how much value we get for each hour spent, the same idea as the value-to-weight ratio in the fractional knapsack problem. Taking a short, important task before a long, less important one is usually the better use of limited hours.

**Q6. Why do you use Earliest Deadline First for the final order?**
EDF is the classical rule for meeting deadlines. If any order of a set of tasks meets all deadlines, then EDF order meets them too (proved by an exchange argument in the report, Lemma 1). So EDF is both the best order to study in and an exact feasibility test.

## B. Correctness

**Q7. Is your algorithm optimal?**
No. It is a heuristic. It always returns a valid schedule, but it does not guarantee the maximum possible importance for every input. Example: H = 10 h, tasks A (6 h, importance 4), B (5 h, 3), C (5 h, 3). Greedy takes A and total is 4; the best is B + C with total 6. The app has a demo button for exactly this.

**Q8. Then in what sense is it "correct"?**
Two senses. (1) *Valid*: by a loop invariant, `chosen` always fits in the hours and is deadline-feasible, so the output never breaks the rules. (2) *Maximal*: after the algorithm finishes, no deferred task can still be added. It is not *optimal*.

**Q9. Explain the loop invariant.**
At the start, `chosen` is empty, so it is feasible and `used = 0`. A task is added only after the budget check and the EDF feasibility check both pass, so after every iteration `used ≤ H` and `chosen` is feasible. When the loop ends the invariant still holds, so the final answer is valid.

**Q10. Explain the exchange argument for EDF.**
Suppose a feasible order has an adjacent pair *i* then *j* with deadline(*i*) > deadline(*j*). Swap them. *j* now finishes earlier, so it is still on time. *i* now finishes exactly when *j* used to finish, which was at most deadline(*j*), which is less than deadline(*i*), so *i* is on time. Other tasks are unaffected. Repeating this sorts the order by deadline without breaking feasibility.

**Q11. Why is the ratio rule optimal for the fractional knapsack but not for your problem?**
In the fractional version, items can be cut, so if a lower-ratio piece is taken while a higher-ratio piece is left, swapping them never lowers the total. Our tasks are all-or-nothing, so the best-ratio task can block a better combination (the A, B, C example).

**Q12. What is the relation to the 0/1 knapsack problem?**
If all deadlines are far away, our problem becomes: choose tasks with durations (weights) and importance (values) to maximise value within *H* hours. That is exactly 0/1 knapsack, which is NP-hard. So no simple greedy rule can be expected to be optimal for all inputs.

**Q13. What does "maximal" mean here and why is it true?**
It means no deferred task can be added to the final set. A task deferred earlier failed either the budget test or the feasibility test with a *smaller* chosen set. Later the set only grows, so `used` only increases and a superset of an infeasible set is still infeasible. Hence the task would still fail. A random test (TC28) checks this.

## C. Complexity

**Q14. What is the time complexity?**
Sorting by ratio is O(n log n). The loop runs *n* times; each time I re-sort the accepted tasks by EDF (O(k log k)) and check feasibility (O(k)), so the loop is O(n² log n). Total: **O(n² log n)** as implemented.

**Q15. Can it be made faster?**
Yes. If the accepted tasks are kept in a sorted list and the new task is inserted in position, each iteration is O(n), giving O(n²) overall. I kept the re-sort for simplicity.

**Q16. What is the space complexity?**
O(n): the ranked list, the chosen list and the deferred list each have at most *n* tasks.

**Q17. What is the complexity of the brute-force comparison?**
It tries all 2<sup>n</sup> subsets and, for each, sorts and checks in O(n log n), so O(2<sup>n</sup> · n log n). That is why the app only runs it for 12 tasks or fewer (4096 subsets).

**Q18. Which is the dominant step in practice?**
For the small inputs of a study planner (a few dozen tasks) all steps finish instantly; the O(n² log n) loop is the dominant term in theory.

## D. Design and implementation

**Q19. How do you convert a deadline date into something the algorithm can check?**
`deadline_day` = (deadline date − today) in days. The deadline in hours is (deadline_day + 1) × hours per day, because a task due on day *d* may use up to the end of day *d*. A task is on time if its cumulative finishing hour is at most that number.

**Q20. How do you break ties in the ranking?**
Higher ratio first; then earlier deadline; then shorter duration; then name. The last rule only makes the output repeatable.

**Q21. Why is the algorithm in a separate file from the Streamlit code?**
`scheduler.py` has no Streamlit code, so it can be tested directly with pytest and explained without the UI. `app.py` only reads input, calls the functions and displays results.

**Q22. How does Streamlit work, and why do you use `st.session_state`?**
Streamlit re-runs the whole script from top to bottom each time the user interacts with a widget. Normal variables are lost on each rerun, so the task list is stored in `st.session_state`, which survives reruns within a browser session.

**Q23. What input validation did you implement?**
Name not empty, at most 60 characters and unique; duration a real number, greater than 0 and at most 100 hours (so 0, negatives, NaN, infinity and text are rejected); importance a whole number from 1 to 5; deadline not before today; total hours greater than 0; hours per day between 0 and 24. The code is in `validate_task` and `validate_budget`.

**Q24. What happens if the user has no tasks, or the time is not enough?**
No tasks: a message asks the user to add tasks and no results are computed. Not enough time for any task: a warning is shown. Not enough time for some: those tasks go to the Deferred tab with a reason (budget, deadline too close, or would break another deadline).

**Q25. What is the baseline and why did you add it?**
First-come-first-served: take tasks in the order entered while they fit in the hours, ignoring importance and deadlines. It shows what the greedy rule adds. The result depends on the entry order, so the comparison is an illustration, not a proof that greedy always wins.

## E. Limitations and extensions

**Q26. List the limitations of your project.**
Heuristic, not always optimal; never reconsiders choices; assumes a fixed number of hours every day from the start of today; tasks cannot be split; importance is a coarse 1–5 value; durations are estimates; data is lost on page refresh; the exact optimum is only computed for ≤ 12 tasks.

**Q27. How could you get the exact optimum?**
For whole-hour durations, a dynamic-programming knapsack table gives the best total value in O(n × H) time (pseudo-polynomial). With deadlines the DP must also respect EDF order, which is more complex. Brute force works for small *n*.

**Q28. Greedy vs dynamic programming?**
Greedy commits to one choice at each step and never reconsiders; it is fast but gives optimal answers only when the problem has the greedy-choice property. DP considers all sub-problem choices and stores their results; it is slower but exact when the problem has optimal substructure.

**Q29. How did you test the project?**
With pytest: 59 tests in total, namely 49 algorithm and validation test cases (28 test functions, some with several parameter sets) plus 10 headless screen tests with Streamlit's AppTest. They include random tests with a fixed seed that check validity, maximality, and that greedy never beats the brute-force optimum. They do not replace manual checks in a real browser.

**Q30. What would you improve first?**
Add the DP-based exact solver for whole-hour tasks, support different study hours on different days, and let the user save and load the task list.
