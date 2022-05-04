[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# GanttPlotter
A set of functions to create gantts quickly using [Matplotlib](https://github.com/matplotlib/matplotlib)

# Usage
```python
# Usage Example
from GanttPlotter import GanttJob, GanttPlotter

if __name__ == "__main__":
    resources = ["Unit 1", "Unit 2", "Unit 3"]
    start_time = 40
    duration = 50
    resource = "Unit 1"
    job_name = "Job1"
    task1 = GanttJob(start_time, duration, resource, job_name)

    task2 = GanttJob(110, 10, "Unit 2", "Job2")
    task3 = GanttJob(150, 10, "Unit 2", "Job1")

    task4 = GanttJob(10, 50, "Unit 3", "Job3")
    task5 = GanttJob(110, 30, "Unit 3", "Job2")
    task6 = GanttJob(130, 20, "Unit 3", "Job3")
    task_list = [task1, task2, task3, task4, task5, task6]

    my_plotter = GanttPlotter(resources=resources, jobs=task_list)

    new_resource = "Unit 4"
    new_task = GanttJob(70, 15, "Unit 4", "Job4")

    my_plotter.add_resource(new_resource)
    my_plotter.add_job(new_task)

    my_plotter.generate_gantt("Great Gantt Generation")
    my_plotter.show_gantt()
```

# ToDo
- Resource Class to make resources groupable
- Testing if colors work really as expected
- Testing if legend really works as expected
- Improved saving figs (e.g. High Quality prints for publications)
