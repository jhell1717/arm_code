from validation import _validate_task
from utils import ExecutionStage

def make_parallel_stages(tasks: list[Task]) -> list[ExecutionStage]:
  """_summary_

  Args:
      tasks (list[Task]): _description_

  Raises:
      RuntimeError: _description_

  Returns:
      list[ExecutionStage]: _description_
  """
    _validate_task(tasks)
    # Create dict of remaining_task & dependencies.
    remaining_tasks = {t.name: set(t.dependencies) for t in tasks}
    
    #Create list of list of strings. 
    stages: list[ExecutionStage] = []

    while remaining_tasks:
      ready = sorted(name for name, deps in remaining_tasks.items() if not deps)


      if not ready:
        stuck = ", ".join(sorted(remaining_tasks))
        raise RuntimeError(f'cycle detected among tasks')
      
      #Add this batch to the stages (multiple tasks)
      stages.append(ready)

      #Remove ready task names from remaining.
      for name in ready:
        del remaining_tasks[name]

      #Remove dependencies from remaining tasks. 
      for deps in remaining_tasks.values():
        deps.difference_update(ready)

    return stages