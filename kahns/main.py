import numpy as np

from validation import _validate_task
from serial import make_serial_schedule
from parallel import make_parallel_stages
from utils import Task

tasks = [
    Task("package", ["link"]),
    Task("compile_b", ["parse"]),
    Task("compile_a", ["parse"]),
    Task("link", ["compile_a", "compile_b"]),
    Task("parse", []),
]
def main():
    parallel_schedule = make_parallel_stages(tasks)
    print(parallel_schedule)

    serial_schedule = make_serial_schedule(tasks)
    print(serial_schedule)

# make_serial_schedule(tasks)
if __name__== "__main__":
    main()





