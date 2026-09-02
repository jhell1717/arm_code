# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Task scheduler implementing Kahn's algorithm for topologically sorting a directed acyclic graph (DAG). Provides serial and parallel scheduling of tasks with dependencies.

## Commands

```bash
# Run tests
pytest kahns/tests/ -v

# Run a single test
pytest kahns/tests/test_scheduler.py::test_name -v

# Run example
python kahns/main.py

# Run performance benchmark
python kahns/profile_parallel.py
```

## Architecture

All code lives in `kahns/` package:

- **utils.py** - `Task` dataclass (immutable, `frozen=True`) and `ExecutionStage` type alias
- **validation.py** - `_validate_task()` for upfront input validation (duplicates, unknown deps)
- **serial.py** - `make_serial_schedule()` returns flat `list[str]`
- **parallel.py** - `make_parallel_stages()` (naive) and `make_parallel_stages_eff()` (optimized with indegree tracking)
- **dfs.py** - `make_dfs_schedule()` using depth-first search

### Key patterns

- **Validation-first**: All public schedulers call `_validate_task()` before processing
- **Determinism**: All algorithms sort ready tasks alphabetically for reproducible output
- **Error types**: `ValueError` for validation errors, `RuntimeError` for cycle detection
- **Immutable input**: `Task` is frozen; algorithms create mutable copies internally

### Public API (exported from `kahns/__init__.py`)

```python
from kahns import Task, make_serial_schedule, make_parallel_stages, make_parallel_stages_eff, make_dfs_schedule
```
