# author          :Dominik Bleidorn (INOSIM)
# date            :2023-05-25
# python_version  :3.9
# version         :0.2

import math
import os
from collections import defaultdict
from datetime import datetime, date
from enum import Enum
from typing import List

import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb


class JobTypes(Enum):
    PROCESS = 1
    CHANGEOVER = 2


class GanttJob:
    def __init__(self, start_time, duration, resource, name, job_type: JobTypes = JobTypes.PROCESS):
        self.start_time = start_time
        self.duration = duration
        self.resource = resource
        self.name = name
        self.type = job_type


class GanttPlotter:
    def __init__(self, resources: List = None, jobs: List[GanttJob] = None):
        if resources is None:
            resources = []
        if jobs is None:
            jobs = []
        self._tickdistance = 10
        self._barheight = 9
        self._jobs = jobs
        self._resources = resources
        self._job_color_dict = {}

    def show_gantt(self):
        plt.show()

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

    def _get_bar_height(self, resource):
        yticks, yticklabels = self._find_yticks()
        origin_offset = 5
        index = yticklabels.index(resource)
        return yticks[index] - origin_offset

    def _find_ymaxlim(self):
        margin = 2
        height_per_resource = 10
        needed_height = height_per_resource * (len(self._resources) + margin)
        lower_limit = margin * height_per_resource
        ymaxlim = max(lower_limit, needed_height)
        return ymaxlim

    def _find_xmaxlim(self):
        last_endtime = 0
        for job in self._jobs:
            end_time = job.start_time + job.duration
            if end_time > last_endtime:
                last_endtime = end_time

        lower_limit = 1
        xmaxlim = max(lower_limit, last_endtime)

        return xmaxlim

    def _calc_num_colors_needed(self):
        unique_job_names = self._get_unique_job_names()
        return len(unique_job_names)

    def _get_unique_job_names(self):
        all_job_names = [job.name for job in self._jobs]
        return list(dict.fromkeys(all_job_names))

    def _generate_colors(self):
        """https://gamedev.stackexchange.com/questions/46463/how-can-i-find-an-optimum-set-of-colors-for-10-players/46469#46469"""
        num_colors = self._calc_num_colors_needed()
        colors = []
        golden_ratio = (1 + 5 ** 0.5) / 2
        for i in range(0, num_colors):
            hue = math.fmod(i * 1 / golden_ratio, 1.0)
            saturation = 0.5
            value = math.sqrt(1.0 - math.fmod(i * 1 / golden_ratio, 0.5))

            next_color = hsv_to_rgb([hue, saturation, value])
            colors.append(next_color)
        return colors

    def generate_gantt(self, title: str = "", description: str = "", xlabel: str = "t [s]", ylabel: str = "Resources",
                       label_processes: bool = False,
                       color_mode: int = 0,
                       save_to_disk: bool = False,
                       filename: str = ""):
        fig, gnt = plt.subplots()
        yticks, yticklabels = self._find_yticks()

        gnt.set_title(title)

        y_maxlim = self._find_ymaxlim()
        gnt.set_ylim(0, y_maxlim)

        x_maxlim = self._find_xmaxlim()
        gnt.set_xlim(0, x_maxlim)

        gnt.set_xlabel(xlabel)
        gnt.set_ylabel(ylabel)

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        gnt.grid(True)
        gnt.set_axisbelow(True)

        self._generate_color_dict(color_mode)

        resource_job_dict = defaultdict(list)
        for job in self._jobs:
            resource_name = job.resource
            resource_job_dict[resource_name].append(job)

        resource_count = 0
        for resource, job_list in resource_job_dict.items():
            broken_bars, facecolors = self._generate_bars_for_resource(
                resource, job_list
            )
            lower_yaxis = self._get_bar_height(resource)
            gnt.broken_barh(
                broken_bars,
                (lower_yaxis, self._barheight),
                facecolors=facecolors,
                alpha=0.9,
                linewidth=0.7,
                edgecolor="black",
            )
            resource_count = resource_count + 1

            # Add labels to the rectangles
            if label_processes:
                labels = [job.name for job in job_list]
                types = [job.type for job in job_list]
                values = [job.duration for job in job_list]

                for i, bar in enumerate(broken_bars):
                    x = (bar[0] + (bar[1] / 2))  # calculate the x position of the label
                    y = lower_yaxis + self._barheight / 2  # calculate the y position of the label
                    if types[i] == JobTypes.PROCESS:
                        gnt.text(x, y, labels[i], rotation=45, ha='center', va="center", fontsize=9, fontweight="bold",
                                 color='black')
                    # else: # == JobTypes.CHANGEOVER:
                    #    gnt.text(x, y, values[i], rotation = 45, ha = "center", va="center", fontsize=9, fontweight="bold", color='black')

        self._add_footnote(gnt)

        # legend_labels = [job_name for job_name in self._job_color_dict.keys()]

        from matplotlib.patches import Patch



        legend_elements = []

        if color_mode == 0 or color_mode == 1:
            for jobname in self._get_unique_job_names():
                element_color = self._get_color_for(jobname)
                element_label = jobname

                new_element = Patch(facecolor=element_color,
                                    edgecolor='black',
                                    linewidth=0.5,
                                    label=element_label)
                legend_elements.append(new_element)
        elif color_mode == 2:
            processing_color = hsv_to_rgb([44 / 360, 0.70, 0.9])
            changeover_color =  hsv_to_rgb([180, 0.1, 1])
            for type in JobTypes:
                if type == JobTypes.CHANGEOVER:
                    element_label = "changeover"
                    element_color = changeover_color
                elif type == JobTypes.PROCESS:
                    element_label = "processing"
                    element_color = processing_color
                new_element = Patch(facecolor=element_color,
                                    edgecolor='black',
                                    linewidth=0.5,
                                    label=element_label)
                legend_elements.append(new_element)

        max_elements_per_column = 11
        legend_columns = math.floor(len(legend_elements) / max_elements_per_column) + 1
        plt.legend(handles=legend_elements, bbox_to_anchor=(1, 1), loc="upper right", ncol=legend_columns, fontsize=9)

        if description:
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            gnt.text(0.5, -0.25, description,
                     transform=gnt.transAxes,
                     fontsize=14,
                     verticalalignment='top',
                     bbox=props,
                     ha="center"
                     )

        fig.tight_layout()
        if save_to_disk:

            if filename == "":
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d--%H-%M-%S")
                filename = f"{dt_string}--Gantt-{title.replace(' ', '_')}.png"

            os.makedirs(os.path.dirname(filename), exist_ok=True)

            figure = plt.gcf()  # get current figure
            figure.set_size_inches(16, 9)  # set figure's size manually to your full screen (32x18)
            plt.savefig(filename, dpi=400)  # bbox_inches removes extra white spaces

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

        gnt.set_title("Kopanos Scheduling Problem")

        # Setting Y-axis limits
        gnt.set_ylim(0, 50)

        # Setting X-axis limits
        gnt.set_xlim(0, 160)

        # Setting labels for x-axis and y-axis
        gnt.set_xlabel("Episode duration [h]")
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

    def _generate_color_dict(self, mode: int = 0):
        """ mode 0: Unique generated color for each job name
            mode 1: Unique color for each processing job, less saturated color for changeovers
            mode 2: All processing times have the same color, all changeovers have the same color
        """

        colors = self._generate_colors()

        unique_job_names = set([job.name for job in self._jobs])
        for count, job in enumerate(unique_job_names):

            if mode == 0 or mode == 1:
                self._job_color_dict[job] = colors[count]
            elif mode == 2:
                self._job_color_dict[job] = hsv_to_rgb([44/360, 0.70, 0.9])

            if job == "CHANGEOVER" and (mode == 1 or mode == 2):
                self._job_color_dict[job] = hsv_to_rgb([180, 0.1, 1])


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
    task5 = GanttJob(110, 30, "Unit 3", "CHANGEOVER", JobTypes.CHANGEOVER)
    task6 = GanttJob(130, 20, "Unit 3", "Job3")
    task_list = [task1, task2, task3, task4, task5, task6]

    my_plotter = GanttPlotter(resources=resources, jobs=task_list)

    new_resource = "Unit 4"
    new_task = GanttJob(70, 15, "Unit 4", "Job4")

    my_plotter.add_resource(new_resource)
    my_plotter.add_job(new_task)


    script = os.path.basename(__file__)
    filename = "MyExampleGanttChart.png"

    my_plotter.generate_gantt("Great Gantt", ylabel="", label_processes=True, color_mode=2)
    my_plotter.show_gantt()
