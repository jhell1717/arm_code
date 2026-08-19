from validation import _validate_task
from utils import Task, ExecutionStage

def make_serial_schedule(tasks: list[Task]) -> list[str]:
    _validate_task(tasks)
    # Create dict of remaining_task & dependencies.
    remaining_task = {t.name: set(t.dependencies)for t in tasks}

    #Initialize schedule
    schedule: list[str] = []
    
    #Until all tasks complete (removed)
    while remaining_task:
      #Identify tasks with no remaining dependencies.
      ready = [name for name, deps in remaining_task.items() if not deps]


      # Stop if ready is empty, but tasks remain. 
      if not ready:
        stuck = ", ".join(sorted(remaining_task))
        raise RuntimeError(f"cycle detected among tasks: {stuck}")

      #Pick alphabetically next (for determinism)
      next_task = min(ready)

      #Add this task to the schedule.
      schedule.append(next_task)

      #Remove the task from the remaining.
      del remaining_task[next_task]

      #Remove the dependencies from tasks already acted on. 
      for deps in remaining_task.values():
        deps.discard(next_task)
    return schedule