import sys
from pathlib import Path

_package_dir = Path(__file__).resolve().parent
if str(_package_dir) not in sys.path:
    sys.path.insert(0, str(_package_dir))

from parallel import make_parallel_stages, make_parallel_stages_eff
from serial import make_serial_schedule
from dfs import make_dfs_schedule
from utils import Task, ExecutionStage
from validation import _validate_task

__all__ = [
    "make_parallel_stages",
    "make_parallel_stages_eff",
    "make_serial_schedule",
    "make_dfs_schedule",
    "Task",
    "ExecutionStage",
]
