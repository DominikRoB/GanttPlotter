# author          :Dominik Bleidorn (INOSIM)
# date            :2022-04-28
# python_version  :3.9
# version         :0.1

import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import math
from collections import defaultdict
from datetime import datetime, date


class GanttPlotter:
    def __init__(self, resources=None, jobs=None):
        if resources is None:
            resources = []
        if jobs is None:
            jobs = []
        self._tickdistance = 10
        self._barheight = 9
        self._jobs = jobs
        self._resources = resources

        self._job_color_dict = {}

    def add_resource(self, resource_name):
        self._resources.append(resource_name)

    def add_job(self, job):
        self._jobs.append(job)

    def _find_yticks(self):
        origin_offset = 5
        yticklabels = []
        yticks = []
        for count, resource_name in enumerate(self._resources):
            yticklabels.append(resource_name)
            ytick_value = origin_offset + (count + 1) * self._tickdistance
            yticks.append(ytick_value)

        return yticks, yticklabels

    def _find_ymaxlim(self):
        return 10 * (len(self._resources) + 2)

    def _find_xmaxlim(self):
        last_endtime = 0
        for job in self._jobs:
            end_time = job.start_time + job.duration
            if end_time > last_endtime:
                last_endtime = end_time

        xmaxlim = last_endtime

        return xmaxlim

    def _generate_colors(self):
        num_colors = len(self._jobs)
        colors = []
        for i in range(0, num_colors):
            hue = math.fmod(i * 0.618033988749895, 1.0)
            saturation = 0.5
            value = math.sqrt(1.0 - math.fmod(i * 0.618033988749895, 0.5))
            next_color = hsv_to_rgb([hue, saturation, value])
            colors.append(next_color)
        return colors

    def generate_gantt(self, title="", save_to_disk=False):

        fig, gnt = plt.subplots()
        yticks, yticklabels = self._find_yticks()

        gnt.set_title(title)

        y_maxlim = self._find_ymaxlim()
        gnt.set_ylim(0, y_maxlim)

        x_maxlim = self._find_xmaxlim()
        gnt.set_xlim(0, x_maxlim)

        gnt.set_xlabel("seconds since start")
        gnt.set_ylabel("Resources")

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        gnt.grid(True)
        gnt.set_axisbelow(True)

        self._generate_color_dict()

        resource_job_dict = defaultdict(list)
        for job in self._jobs:
            resource_name = job.resource
            resource_job_dict[resource_name].append(job)

        resource_count = 0
        for resource, job_list in resource_job_dict.items():
            broken_bars, facecolors = self._generate_bars_for_resource(
                resource, job_list
            )
            lower_yaxis = (resource_count + 1) * self._tickdistance
            gnt.broken_barh(
                broken_bars, (lower_yaxis, self._barheight), facecolors=facecolors,
                alpha=0.8, edgecolor='black'
            )
            resource_count = resource_count + 1

        self._add_footnote(gnt)

        legend_labels = [job_name for job_name in self._job_color_dict.keys()]
        plt.legend(legend_labels, bbox_to_anchor=(1.04, 0.6), loc="upper left")

        fig.tight_layout()
        if save_to_disk:
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y--%H-%M-%S")
            plt.savefig(f"{dt_string}--Gantt-{title.replace(' ','_')}.png")
        return fig

    def _generate_bars_for_resource(self, resource, job_list):
        broken_bars = [(job.start_time, job.duration) for job in job_list]
        facecolors = [self._get_color_for(job.name) for job in job_list]
        return broken_bars, facecolors

    def _add_footnote(self, gnt):
        import os

        today = date.today()
        user = os.getlogin()
        gnt.annotate(
            f"{today} - {user}",
            xy=(1.0, -0.2),
            xycoords="axes fraction",
            ha="right",
            va="center",
            fontsize=8,
        )

    def example_gantt(self):
        # Declaring a figure "gnt"
        fig, gnt = plt.subplots()

        gnt.set_title("Example")

        # Setting Y-axis limits
        gnt.set_ylim(0, 50)

        # Setting X-axis limits
        gnt.set_xlim(0, 160)

        # Setting labels for x-axis and y-axis
        gnt.set_xlabel("seconds since start")
        gnt.set_ylabel("Processor")

        # Setting ticks on y-axis
        gnt.set_yticks([15, 25, 35])
        # Labelling tickes of y-axis
        gnt.set_yticklabels(["1", "2", "3"])

        # Setting graph attribute
        gnt.grid(True)

        # Declaring a bar in schedule
        gnt.broken_barh([(40, 50)], (30, 9), facecolors=("tab:orange"))

        # Declaring multiple bars in at same level and same width
        gnt.broken_barh(
            [(110, 10), (150, 10)], (10, 9), facecolors=["tab:blue", "tab:orange"]
        )

        gnt.broken_barh(
            [(10, 50), (100, 20), (130, 10)], (20, 9), facecolors=("tab:red")
        )

        self._add_footnote(gnt)

        fig.tight_layout()
        return fig

    def _get_color_for(self, job_name):
        return self._job_color_dict[job_name]

    def _generate_color_dict(self):
        colors = self._generate_colors()
        for count, job in enumerate(self._jobs):
            self._job_color_dict[job.name] = colors[count]


class GanttJob:
    def __init__(self, start_time, duration, resource, name):
        self.start_time = start_time
        self.duration = duration
        self.resource = resource
        self.name = name


if __name__ == "__main__":
    resources = ["Unit 1", "Unit 2", "Unit 3"]
    task1 = GanttJob(40, 50, "Unit 1", "Job1")

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
    plt.show()
