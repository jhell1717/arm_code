
from collections import deque
from validation import _validate_task
from utils import ExecutionStage, Task

def make_parallel_stages(tasks: list[Task]) -> list[ExecutionStage]:
    _validate_task(tasks)

    remaining_tasks = {t.name: set(t.dependencies) for t in tasks}
    
    #Create list of list of strings. 
    stages: list[ExecutionStage] = []

    while remaining_tasks:
      ready = sorted(name for name, deps in remaining_tasks.items() if not deps)

      if not ready:
        stuck = ", ".join(sorted(remaining_tasks))
        raise RuntimeError(f'cycle detected among tasks in {stuck}')
      
      #Add this batch to the stages (multiple tasks)
      stages.append(ready)

      #Remove ready task names from remaining.
      for name in ready:
        del remaining_tasks[name]

      #Remove dependencies from remaining tasks. 
      for deps in remaining_tasks.values():
        deps.difference_update(ready)

    return stages

def make_parallel_stages_eff(tasks: list[Task]) -> list[ExecutionStage]:
    _validate_task(tasks)

    # remaining_tasks = {t.name: set(t.dependencies) for t in tasks}

    #Create list of list of strings. 
    stages: list[ExecutionStage] = []

    # Changed to tracking how many prequisites does the task still have.
    indegree = {
        task.name: len(task.dependencies)
        for task in tasks
    }

    # For each task, which tasks depend on it?
    dependants = {
        task.name: []
        for task in tasks
    }

    # Adds the dependencies for each task to the task list dependants.
    for task in tasks:
      for dependency in task.dependencies:
        dependants[dependency].append(task.name)

    stages: list[ExecutionStage] = []

    # When degree in the indegree tracker gets to 0, it will add to ready queue (double ended).
    ready = deque(sorted(name for name, degree in indegree.items() if degree == 0))

    while ready:
      current_stage = list(ready)
      ready.clear()

      # Adds the ready items to the stage.
      stages.append(current_stage)

      # Decrement the indegree for each of the staged tasks in the indegree tracker.
      for task in current_stage:
        for dependent in dependants[task]:
          indegree[dependent] -= 1

          # If this indegree count because 0, now add that dependent to the ready list.
          # The while loop will run, clear the queue, add the current stage. 
          if indegree[dependent] == 0:
            ready.append(dependent)

    if any(degree > 0 for degree in indegree.values()):
        stuck = ", ".join(
            sorted(
                name
                for name, degree in indegree.items()
                if degree > 0
            )
        )
        raise RuntimeError(
            f"cycle detected among tasks in {stuck}"
        )

    return stages