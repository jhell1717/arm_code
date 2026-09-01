from utils import Task
from validation import _validate_task

# tasks = [
#     Task("package", ["link"]),
#     Task("compile_b", ["parse"]),
#     Task("compile_a", ["parse"]),
#     Task("link", ["compile_a", "compile_b"]),
#     Task("parse", []),
# ]

def make_dfs_schedule(tasks: list[Task]) -> list[str]:
    """_summary_

    Args:
        tasks (list[Task]): _description_

    Returns:
        list[str]: _description_
    """
    _validate_task(tasks)

    remaining_tasks = {t.name: set(t.dependencies) for t in tasks}

    schedule: list[str] = []

    visited = set()
    visiting = set()

    def dfs(task):
        if task in visiting:
             stuck = ", ".join(sorted(remaining_tasks))
             raise RuntimeError(f"cycle detected among tasks in {stuck}")

        
        if task in visited:
            return
    
        visiting.add(task)

        for dep in sorted(remaining_tasks[task]): #adds sorted for determinism as remaining_tasks is unordered set.
            dfs(dep)

        visiting.remove(task)
        visited.add(task)
        schedule.append(task)

    for task in remaining_tasks:
            dfs(task)

    return schedule
