from utils import Task

def _validate_task(tasks: list[Task]) -> None:
  seen: set[str] = set() #set so cant contain duplicates.

  # Raise error for duplicate tasks, otherwise add to seen.
  for t in tasks:
    if t.name in seen:
      raise ValueError(f"Duplicate task name: {t.name!r}")
    seen.add(t.name)
  
  # Catch unknown dependencies, checking in seen.
  for t in tasks:
    for dep in t.dependencies:
      if dep not in seen: 
        raise ValueError(
          f"task {t.name!r} depends on unknown task {dep!r}"
        )