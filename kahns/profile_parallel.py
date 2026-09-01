"""Quick timing comparison between make_parallel_stages and make_parallel_stages_eff.

Run from the kahns/ directory:
    python profile_parallel.py
"""

import timeit

from parallel import make_parallel_stages, make_parallel_stages_eff
from utils import Task


def make_layered_tasks(num_layers: int, width: int) -> list[Task]:
    """Build a DAG with `num_layers` layers of `width` tasks each,
    where every task in a layer depends on every task in the previous layer.
    """
    tasks: list[Task] = []
    prev_layer: list[str] = []
    for layer in range(num_layers):
        layer_names = [f"l{layer}_t{i}" for i in range(width)]
        for name in layer_names:
            tasks.append(Task(name, list(prev_layer)))
        prev_layer = layer_names
    return tasks


def bench(func, tasks, number: int) -> float:
    return timeit.timeit(lambda: func(tasks), number=number)


if __name__ == "__main__":
    small_tasks = [
        Task("package", ["link"]),
        Task("compile_b", ["parse"]),
        Task("compile_a", ["parse"]),
        Task("link", ["compile_a", "compile_b"]),
        Task("parse", []),
    ]

    big_tasks = make_layered_tasks(num_layers=50, width=20)

    for label, tasks, number in [
        ("small (5 tasks)", small_tasks, 10_000),
        ("large (1000 tasks)", big_tasks, 100),
    ]:
        print(f"\n{label}")
        naive_time = bench(make_parallel_stages, tasks, number)
        eff_time = bench(make_parallel_stages_eff, tasks, number)
        print(f"  make_parallel_stages:     {naive_time:.4f}s total, {naive_time / number * 1e6:.2f}us/call")
        print(f"  make_parallel_stages_eff: {eff_time:.4f}s total, {eff_time / number * 1e6:.2f}us/call")
        print(f"  speedup: {naive_time / eff_time:.2f}x")
