import argparse
import csv
import time
from concurrent.futures import ThreadPoolExecutor
import networkx as nx
from pathlib import Path


def parse_tasks(file_path):
    tasks = {}
    with open(file_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            name = row[0].strip()
            duration = int(row[1].strip())
            dependencies = [dep.strip() for dep in row[2:] if dep.strip()]
            tasks[name] = {"duration": duration, "deps": dependencies}
    return tasks


def build_graph(tasks):
    G = nx.DiGraph()
    for task, data in tasks.items():
        G.add_node(task, duration=data["duration"])
        for dep in data["deps"]:
            if dep not in tasks:
                raise ValueError(f"Task '{task}' depends on unknown task '{dep}'")
            G.add_edge(dep, task)
    return G



def validate_graph(G: nx.DiGraph):
    """
    Validates that G is a DAG and computes the critical path using node 'duration'.
    Returns: (expected_runtime, critical_path [list of node names])
    Raises: ValueError on cycles.
    """
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Cycle detected in task dependencies")

    topo = list(nx.topological_sort(G))
    earliest_finish = {}
    parent = {}

    for u in topo:
        preds = list(G.predecessors(u))
        if preds:
            # predecessor that finishes latest
            p = max(preds, key=lambda x: earliest_finish[x])
            parent[u] = p
            earliest_start = earliest_finish[p]
        else:
            parent[u] = None
            earliest_start = 0
        earliest_finish[u] = earliest_start + G.nodes[u]['duration']

    # end of critical path = node with max earliest_finish
    end = max(earliest_finish, key=lambda n: earliest_finish[n])
    expected_runtime = earliest_finish[end]

    # backtrack to build path
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    return expected_runtime, path

def run_tasks(tasks, G):
    done = set()
    futures = {}
    task_timings = {}
    start_time = time.perf_counter()

    with ThreadPoolExecutor() as executor:
        def submit(task):
            deps = tasks[task]['deps']
            for dep in deps:
                futures[dep].result()

            t_start = time.perf_counter()
            print(f"[+] Running {task} for {tasks[task]['duration']}s")
            time.sleep(tasks[task]['duration'])
            t_end = time.perf_counter()

            task_timings[task] = {
                "start": t_start - start_time,
                "end": t_end - start_time,
            }

            print(f"[-] Finished {task}")
            done.add(task)

        for task in nx.topological_sort(G):
            futures[task] = executor.submit(submit, task)

        for f in futures.values():
            f.result()

    end_time = time.perf_counter()

    # Gantt-like output
    print("\nGantt Summary (all times in seconds):")
    for task, timing in sorted(task_timings.items(), key=lambda x: x[1]["start"]):
        duration = timing["end"] - timing["start"]
        print(f"{task:<10} | start: {timing['start']:.2f}  end: {timing['end']:.2f}  duration: {duration:.2f}")

    return end_time - start_time


def main():
    parser = argparse.ArgumentParser(description="Task Scheduler CLI")
    parser.add_argument("file", type=Path, help="Path to task definition file")
    parser.add_argument("--validate", action="store_true", help="Validate tasks and compute expected runtime")
    parser.add_argument("--run", action="store_true", help="Run the tasks in parallel")

    args = parser.parse_args()

    tasks = parse_tasks(args.file)
    G = build_graph(tasks)

    if args.validate:
        expected_runtime, critical_path = validate_graph(G)
        print(f"[✓] Task list is valid")
        print(f"Critical path: {' → '.join(critical_path)}")
        print(f"Expected total runtime: {expected_runtime:.2f} seconds")

    if args.run:
        expected_runtime, _ = validate_graph(G)
        print(f"Expected runtime: {expected_runtime:.2f} seconds")
        actual_runtime = run_tasks(tasks, G)
        print(f"Actual runtime:   {actual_runtime:.2f} seconds")
        print(f"Difference:       {actual_runtime - expected_runtime:.2f} seconds")

if __name__ == "__main__":
    main()
