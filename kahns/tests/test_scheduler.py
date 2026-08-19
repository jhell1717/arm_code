import pytest

from utils import Task
from validation import _validate_task
from serial import make_serial_schedule
from parallel import make_parallel_stages


def test_makes_deterministic_serial_schedule() -> None:
    tasks = [
        Task("package", ["link"]),
        Task("compile_b", ["parse"]),
        Task("compile_a", ["parse"]),
        Task("link", ["compile_a", "compile_b"]),
        Task("parse", []),
    ]

    expected = ["parse", "compile_a", "compile_b", "link", "package"]

    assert make_serial_schedule(tasks) == expected


def test_groups_independent_tasks_into_parallel_stages() -> None:
    tasks = [
        Task("emit", ["lower", "quantize"]),
        Task("quantize", ["parse", "validate"]),
        Task("validate", []),
        Task("lower", ["parse"]),
        Task("parse", []),
    ]

    expected = [
        ["parse", "validate"],
        ["lower", "quantize"],
        ["emit"],
    ]
    print(make_parallel_stages(tasks))
    assert make_parallel_stages(tasks) == expected


def test_rejects_duplicate_task_names() -> None:
    tasks = [
        Task("parse", []),
        Task("parse", []),
    ]

    with pytest.raises(ValueError):
        make_serial_schedule(tasks)
    with pytest.raises(ValueError):
        make_parallel_stages(tasks)


def test_rejects_unknown_dependencies() -> None:
    tasks = [
        Task("compile", ["parse"]),
    ]

    with pytest.raises(ValueError):
        make_serial_schedule(tasks)
    with pytest.raises(ValueError):
        make_parallel_stages(tasks)


def test_detects_cycles() -> None:
    tasks = [
        Task("a", ["c"]),
        Task("b", ["a"]),
        Task("c", ["b"]),
    ]

    with pytest.raises(RuntimeError):
        make_serial_schedule(tasks)
    with pytest.raises(RuntimeError):
        make_parallel_stages(tasks)