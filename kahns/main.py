import numpy as np

from validation import _validate_task
from serial import make_serial_schedule
from dfs import make_dfs_schedule
from parallel import make_parallel_stages, make_parallel_stages_eff
from utils import Task

tasks = [
    Task("package", ["link"]),
    Task("compile_b", ["parse"]),
    Task("compile_a", ["parse"]),
    Task("link", ["compile_a", "compile_b"]),
    Task("parse", []),
    Task("send",["package"])
]

## Cycle test:
# tasks = [
#     Task("a", ["c"]),
#     Task("b", ["a"]),
#     Task("c", ["b"]),
# ]

def main():
    parallel_schedule = make_parallel_stages(tasks)
    print(f"Kahn Parallel scheduling: {parallel_schedule}")
    print('\n')
    parallel_schedule_eff = make_parallel_stages_eff(tasks)
    print(f"Kahn Parallel with Efficiency scheduling: {parallel_schedule_eff}")
    print('\n')
    serial_schedule = make_serial_schedule(tasks)
    print(f"Kahn Serial scheduling: {serial_schedule}")
    print('\n')
    dfs_schedule = make_dfs_schedule(tasks)
    print(f"Scheduling with DFS: {dfs_schedule}")
    print('\n')

# make_serial_schedule(tasks)
if __name__== "__main__":
    main()







