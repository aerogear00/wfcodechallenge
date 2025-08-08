Task Scheduler CLI
A Python command-line tool to:
Validate a text-based task list with dependencies.
Calculate expected runtime using critical-path analysis.
Run tasks in parallel while respecting dependencies.
Compare actual vs. expected runtime.
Visualize execution with a Gantt-style summary.

Requirements:
Python 3.8+
Pip
NetworkX (graph analysis)

 Input File Format:
 task_name,duration_in_seconds,dependency1,dependency2,...
task_name → Unique identifier (string).
duration_in_seconds → Integer, the simulated time the task takes.
dependencyN → Optional, other tasks that must finish before this one starts.


Usage:
General syntax:
python task_scheduler.py FILE [--validate] [--run]
Option	Description
--validate	Checks for cycles, missing dependencies, and prints critical path & expected runtime.
--run	Executes tasks in parallel, respecting dependencies, and shows a Gantt-style timing summary.
Both flags can be combined.	You’ll get validation output and then execution results.

Output example: --validate
[✓] Task list is valid
Critical path: taskA → taskB → taskD
Expected total runtime: 7.00 seconds

Output example: --run
Expected runtime: 7.00 seconds
[+] Running taskA for 3s
[-] Finished taskA
[+] Running taskB for 2s
[+] Running taskC for 1s
[-] Finished taskC
[-] Finished taskB
[+] Running taskD for 2s
[-] Finished taskD

Gantt Summary (all times in seconds):
taskA      | start: 0.00  end: 3.00  duration: 3.00
taskC      | start: 3.00  end: 4.00  duration: 1.00
taskB      | start: 3.00  end: 5.00  duration: 2.00
taskD      | start: 5.00  end: 7.00  duration: 2.00

Actual runtime:   7.00 seconds
Difference:       0.00 seconds
