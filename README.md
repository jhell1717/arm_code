# Task Scheduler — Kahn's Algorithm

This project schedules a set of tasks that depend on one another, using
**Kahn's algorithm** — the classic approach for topologically sorting a
directed acyclic graph (DAG). It ships two flavours of the same idea:

- `make_serial_schedule` — a single, deterministic execution order.
- `make_parallel_stages` — tasks grouped into batches ("stages") that can
  run concurrently, respecting dependencies between stages.

Both raise a clear error if the task set is invalid (duplicate names,
unknown dependencies) or contains a dependency cycle.

## How Kahn's algorithm works

Think of each task as a node in a graph, and each dependency as a directed
edge pointing from the dependency to the task that needs it. A task is
**ready** once every task it depends on has already been scheduled.

Kahn's algorithm repeats a simple loop:

1. Find every task with no remaining (unscheduled) dependencies — these are
   "ready".
2. If nothing is ready but tasks are still left, the remaining tasks form a
   cycle (they depend on each other, directly or indirectly) — this is an
   error, not a valid schedule.
3. Schedule the ready task(s).
4. Remove them from every other task's dependency set, since they're now
   satisfied.
5. Repeat until no tasks remain.

The serial and parallel versions in this project both follow exactly this
loop — they only differ in what they do with the "ready" set at each step
(pick one vs. take them all).

## Project structure

```
utils.py        Task dataclass and the ExecutionStage type alias
validation.py    _validate_task — shared validation for both schedulers
serial.py        make_serial_schedule — one task at a time
parallel.py      make_parallel_stages — batches of tasks per stage
main.py          example usage / entry point
tests/           pytest suite
```

## The data model

```python
@dataclass(frozen=True)
class Task:
    name: str
    dependencies: list[str] = field(default_factory=list)

ExecutionStage = list[str]
```

- `Task` is immutable (`frozen=True`) — once created it can't be
  accidentally mutated while the scheduler is working with it.
- `dependencies` defaults to an empty list, so a task with no prerequisites
  can be written as `Task("parse")`.
- `ExecutionStage` is just a readable alias for "a list of task names that
  can all run at the same time".

## Validation

Before either scheduler does any work, it calls `_validate_task`, which
checks the task set up front and fails fast with a `ValueError`:

- **Duplicate task names** — every task name must be unique.
- **Unknown dependencies** — a task can't depend on a name that isn't in
  the task set.

```python
_validate_task([Task("build"), Task("build")])
# ValueError: Duplicate task name: 'build'

_validate_task([Task("compile", ["parse"])])
# ValueError: task 'compile' depends on unknown task 'parse'
```

Neither scheduler needs to worry about these cases internally — by the
time the scheduling loop starts, the task set is known to be well-formed.

## Serial scheduling (`serial.py`)

`make_serial_schedule` produces a single, deterministic list of task
names, in an order that never runs a task before its dependencies.

```python
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
```

Walkthrough:

1. `remaining_task` maps every task name to a *mutable* copy of its
   dependencies (a `set`, so removals are cheap and order-independent).
2. Each iteration collects every task whose dependency set is now empty —
   the `ready` list.
3. If `ready` is empty but `remaining_task` isn't, the loop can never make
   progress — that's a cycle, and it's reported as a `RuntimeError` naming
   every task still stuck.
4. When more than one task is ready at once, `min(ready)` picks the
   alphabetically first name. This is what makes the output **deterministic**
   — running the same task set twice always produces the same order, even
   though "ready" tasks have no real ordering requirement between them.
5. The chosen task is appended to `schedule`, removed from
   `remaining_task`, and cleared out of every other task's dependency set
   (`deps.discard(next_task)`), which may make more tasks ready next round.

## Parallel scheduling (`parallel.py`)

`make_parallel_stages` uses the same loop, but instead of picking one
task per round, it schedules the **entire ready batch at once** as a
single stage — modelling tasks that could genuinely run in parallel.

```python
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
```

Walkthrough:

1. Same setup as the serial version: `remaining_tasks` maps names to a
   mutable set of unmet dependencies.
2. `ready` is *every* task with no remaining dependencies this round,
   sorted alphabetically (again purely for deterministic, readable output —
   there's no dependency ordering between tasks in the same stage).
3. An empty `ready` with tasks still remaining is the same cycle case as
   the serial version, raising `RuntimeError`.
4. The whole `ready` batch becomes the next stage in `stages` — this is
   the key difference from the serial version, which only ever takes
   `min(ready)`.
5. All ready names are removed from `remaining_tasks` in one pass, and
   `deps.difference_update(ready)` clears them from every other task's
   dependency set in bulk before the next round starts.

The result is a list of stages where every task in stage *N* only depends
on tasks in stages `0..N-1` — so everything within a single stage can
safely be run concurrently.

## Serial vs. parallel, side by side

| | `make_serial_schedule` | `make_parallel_stages` |
|---|---|---|
| Returns | `list[str]` — one flat order | `list[list[str]]` — batched stages |
| Per round | Schedules **one** task (`min(ready)`) | Schedules **all** ready tasks at once |
| Use case | Running tasks one after another | Running independent tasks concurrently, stage by stage |
| Determinism | Alphabetical tie-break between ready tasks | Each stage is sorted alphabetically |
| Cycle handling | `RuntimeError` naming stuck tasks | `RuntimeError` (same detection logic) |

## Example

Given this dependency graph (mirrors `main.py`):

```python
tasks = [
    Task("package", ["link"]),
    Task("compile_b", ["parse"]),
    Task("compile_a", ["parse"]),
    Task("link", ["compile_a", "compile_b"]),
    Task("parse", []),
]
```

```python
make_serial_schedule(tasks)
# ["parse", "compile_a", "compile_b", "link", "package"]

make_parallel_stages(tasks)
# [["parse"], ["compile_a", "compile_b"], ["link"], ["package"]]
```

`parse` has no dependencies, so it runs first (and alone, since it's the
only thing ready). `compile_a` and `compile_b` both only depend on `parse`,
so they become ready together — the serial schedule breaks the tie
alphabetically, while the parallel schedule keeps them in the same stage
since they can run at the same time. `link` needs both compiles to finish,
and `package` needs `link`, so each ends up in its own stage.

## Error handling

| Situation | Raised by | Exception |
|---|---|---|
| Duplicate task name | `_validate_task` (called by both schedulers) | `ValueError` |
| Dependency on an unknown task | `_validate_task` (called by both schedulers) | `ValueError` |
| Circular dependency (e.g. `a → b → a`) | `make_serial_schedule` / `make_parallel_stages` | `RuntimeError` |

## Running the tests

The test suite lives in `tests/` and uses `pytest`. An empty `conftest.py`
sits at the project root so pytest can resolve `from utils import Task`,
`from validation import _validate_task`, etc. from inside `tests/`.

```bash
pip install pytest
pytest tests/ -v
```