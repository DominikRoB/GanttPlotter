# author          :Dominik Bleidorn (INOSIM)
# date            :2023-05-25
# python_version  :3.9
# version         :0.2

import math
import os
from collections import defaultdict
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Tuple, Any

import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from matplotlib.patches import Patch
from matplotlib.figure import Figure


class JobTypes(Enum):
    """
    An Enum representing different types of jobs in a Gantt chart.

    Attributes
    ----------
    PROCESS : int
        A constant representing a process job type.
    CHANGEOVER : int
        A constant representing a changeover job type.
    """

    PROCESS = 1
    CHANGEOVER = 2


class GanttJob:
    """
    A class representing a job in a Gantt chart.

    Attributes
    ----------
    start_time : float
        The start time of the job.
    duration : float
        The duration of the job.
    resource : str
        The resource allocated for the job.
    name : str
        The name of the job.
    job_type : JobTypes
        The type of the job, defaults to JobTypes.PROCESS.

    Methods
    -------
    __init__(self, start_time, duration, resource, name, job_type=JobTypes.PROCESS)
        Initializes the GanttJob instance with the given parameters.
    """

    def __init__(
        self,
        start_time: float,
        duration: float,
        resource: str,
        name: str,
        job_type: JobTypes = JobTypes.PROCESS,
    ) -> None:
        """
        Constructs all the necessary attributes for the GanttJob object.

        Parameters
        ----------
        start_time : float
            The start time of the job.
        duration : float
            The duration of the job.
        resource : str
            The resource allocated for the job.
        name : str
            The name of the job.
        job_type : JobTypes, optional
            The type of the job, by default JobTypes.PROCESS.
        """
        self.start_time = start_time
        self.duration = duration
        self.resource = resource
        self.name = name
        self.job_type = job_type


class GanttPlotter:
    """
    A class to plot jobs in a Gantt chart.

    Attributes
    ----------
    _y_tick_distance : int
        The distance between ticks on the Gantt chart.
    _barheight : int
        The height of bars in the Gantt chart representing jobs.
    _jobs : List[GanttJob]
        The list of jobs to be plotted on the Gantt chart.
    _resources : List[str]
        The list of resources involved in the jobs.
    _job_color_dict : dict
        Dictionary mapping jobs to their respective colors on the Gantt chart.
    xticks_step_size : Optional[int]
        The step size between x-axis ticks, defaults to None.
    xticks_max_value : Optional[int]
        The maximum value for the x-axis ticks, defaults to None.

    Methods
    -------
    __init__(self, resources: Optional[List[str]] = None, jobs: Optional[List[GanttJob]] = None, xticks_step_size: Optional[int] = None, xticks_max_value: Optional[int] = None)
        Initializes the GanttPlotter instance with the given parameters.
    """

    def __init__(
        self,
        resources: Optional[List[str]] = None,
        jobs: Optional[List[GanttJob]] = None,
        xticks_step_size: Optional[int] = None,
        xticks_max_value: Optional[int] = None,
    ) -> None:
        """
        Constructs all the necessary attributes for the GanttPlotter object.

        Parameters
        ----------
        resources : List[str], optional
            The list of resources involved in the jobs, by default None.
        jobs : List[GanttJob], optional
            The list of jobs to be plotted on the Gantt chart, by default None.
        xticks_step_size : int, optional
            The step size between x-axis ticks, by default None.
        xticks_max_value : int, optional
            The maximum value for the x-axis ticks, by default None.
        """

        self._y_tick_distance = 10
        self._barheight = 9
        self._jobs = jobs if jobs is not None else []
        self._resources = resources if resources is not None else []
        self._job_color_dict = {}
        self.xticks_step_size = xticks_step_size
        self.xticks_max_value = xticks_max_value

    def show_gantt(self) -> None:
        """
        Display the Gantt chart.

        This method uses matplotlib's plt.show() to display the Gantt chart.
        """
        plt.show()

    def add_resource(self, resource_name: str) -> None:
        """
        Adds a new resource to the list of resources.

        Parameters
        ----------
        resource_name : str
            Name of the resource to be added.
        """
        self._resources.append(resource_name)

    def add_job(self, job: GanttJob) -> None:
        """
        Adds a new job to the list of jobs.

        Parameters
        ----------
        job : GanttJob
            The job to be added.
        """
        self._jobs.append(job)

    def _find_xticks(
        self, step_size: int, max_value: int
    ) -> Tuple[List[int], List[str]]:
        """
        Private method to find x-ticks and their corresponding labels for the Gantt chart.

        Parameters
        ----------
        step_size : int
            The step size between x-axis ticks.
        max_value : int
            The maximum value for the x-axis ticks.

        Returns
        -------
        Tuple[List[int], List[str]]
            A tuple of two lists. The first list contains the x-tick values and the second list contains their corresponding labels.
        """
        xticklabels = []
        xticks = []

        number_full_ticks = max_value // step_size + 1  # Including Zero

        for ii in range(number_full_ticks):
            value = ii * step_size
            xticklabels.append(str(value))
            xticks.append(value)

        xticklabels.append(str(max_value))
        xticks.append(max_value)

        return xticks, xticklabels

    def _find_yticks(self):
        origin_offset = 5
        yticklabels = []
        yticks = []
        for count, resource_name in enumerate(self._resources):
            yticklabels.append(resource_name)
            ytick_value = origin_offset + (count + 1) * self._y_tick_distance
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
        if self.xticks_max_value:
            return self.xticks_max_value

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
        golden_ratio = (1 + 5**0.5) / 2
        for i in range(0, num_colors):
            hue = math.fmod(i * 1 / golden_ratio, 1.0)
            saturation = 0.5
            value = math.sqrt(1.0 - math.fmod(i * 1 / golden_ratio, 0.5))

            next_color = hsv_to_rgb([hue, saturation, value])
            colors.append(next_color)
        return colors

    def _create_legend(self, color_mode: int, max_elements_per_column: int) -> Any:
        """
        Private method to create the legend for the Gantt chart.

        Parameters
        ----------
        color_mode : int
            The color mode to use for the legend.
        max_elements_per_column : int
            The maximum number of elements per column in the legend.

        Returns
        -------
        Any
            The matplotlib legend.
        """
        legend_elements = []
        if color_mode == 0 or color_mode == 1:
            for jobname in self._get_unique_job_names():
                element_color = self._get_color_for(jobname)
                element_label = jobname
                new_element = Patch(
                    facecolor=element_color,
                    edgecolor="black",
                    linewidth=0.5,
                    label=element_label,
                )
                legend_elements.append(new_element)
        elif color_mode == 2:
            processing_color = hsv_to_rgb([44 / 360, 0.70, 0.9])
            changeover_color = hsv_to_rgb([180, 0.1, 1])
            for type in JobTypes:
                if type == JobTypes.CHANGEOVER:
                    element_label = "changeover"
                    element_color = changeover_color
                elif type == JobTypes.PROCESS:
                    element_label = "processing"
                    element_color = processing_color
                new_element = Patch(
                    facecolor=element_color,
                    edgecolor="black",
                    linewidth=0.5,
                    label=element_label,
                )
                legend_elements.append(new_element)
        legend_columns = math.floor(len(legend_elements) / max_elements_per_column) + 1
        return plt.legend(
            handles=legend_elements,
            bbox_to_anchor=(1, 1),
            loc="upper right",
            ncol=legend_columns,
            fontsize=9,
        )

    def _setup_plot_limits(self, gnt: Any) -> None:
        """
        Private method to set up the limits of the plot in the Gantt chart.

        Parameters
        ----------
        gnt : Any
            The Gantt plot.
        """
        y_maxlim = self._find_ymaxlim()
        gnt.set_ylim(0, y_maxlim)

        x_maxlim = self._find_xmaxlim()
        gnt.set_xlim(0, x_maxlim)

    def _save_figure(self, title: str, filename: str) -> None:
        """
        Private method to save the Gantt chart to disk.

        Parameters
        ----------
        title : str
            The title of the Gantt chart.
        filename : str
            The filename to save the Gantt chart as.
        """
        if filename == "":
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d--%H-%M-%S")
            filename = f"{dt_string}--Gantt-{title.replace(' ', '_')}.png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        figure = plt.gcf()
        figure.set_size_inches(16, 9)
        plt.savefig(filename, dpi=400)

    def _setup_axis_ticks(self, gnt: Any) -> None:
        """
        Private method to set up the x and y axis ticks of the Gantt plot.

        Parameters
        ----------
        gnt : Any
            The Gantt plot.
        """
        if self.xticks_step_size:
            xticks, xticklabels = self._find_xticks(
                self.xticks_step_size, self._find_xmaxlim()
            )
            gnt.set_xticks(xticks)
            gnt.set_xticklabels(xticklabels)

        yticks, yticklabels = self._find_yticks()
        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

    def _plot_jobs(self, gnt: Any, label_processes: bool) -> None:
        """
        Private method to plot the jobs on the Gantt chart.

        Parameters
        ----------
        gnt : Any
            The Gantt plot.
        label_processes : bool
            Whether or not to label the processes in the Gantt chart.
        """

        resource_job_dict = defaultdict(list)
        for job in self._jobs:
            resource_name = job.resource
            resource_job_dict[resource_name].append(job)

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

            # Add labels to the rectangles
            if label_processes:
                self._add_labels_to_bars(gnt, job_list, broken_bars, lower_yaxis)

    def _add_labels_to_bars(
        self,
        gnt: Any,
        job_list: List[GanttJob],
        broken_bars: List[Tuple],
        lower_yaxis: float,
    ) -> None:
        """
        Private method to add labels to the bars in the Gantt chart.

        Parameters
        ----------
        gnt : Any
            The Gantt plot.
        job_list : List[GanttJob]
            List of jobs.
        broken_bars : List[Tuple]
            List of tuples defining the bars.
        lower_yaxis : float
            Lower limit of the y-axis.
        """

        labels = [job.name for job in job_list]
        types = [job.job_type for job in job_list]

        for i, bar in enumerate(broken_bars):
            x = bar[0] + (bar[1] / 2)  # calculate the x position of the label
            y = (
                lower_yaxis + self._barheight / 2
            )  # calculate the y position of the label
            if types[i] == JobTypes.PROCESS:
                gnt.text(
                    x,
                    y,
                    labels[i],
                    rotation=45,
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                    color="black",
                )

    def _add_description(self, gnt: Any, description: str) -> None:
        """
        Private method to add a description to the Gantt chart.

        Parameters
        ----------
        gnt : Any
            The Gantt plot.
        description : str
            The description to be added.
        """
        if description:
            props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
            gnt.text(
                0.5,
                -0.25,
                description,
                transform=gnt.transAxes,
                fontsize=14,
                verticalalignment="top",
                bbox=props,
                ha="center",
            )

    def generate_gantt(
        self,
        title: str = "",
        description: str = "",
        xlabel: str = "t [s]",
        ylabel: str = "Resources",
        label_processes: bool = False,
        color_mode: int = 0,
        save_to_disk: bool = False,
        filename: str = "",
    ) -> Figure:
        """
        Generates a Gantt chart from the jobs and resources data provided.

        Parameters
        ----------
        title : str, optional
            Title of the Gantt chart, by default "".
        description : str, optional
            Description of the Gantt chart, by default "".
        xlabel : str, optional
            Label of the x-axis, by default "t [s]".
        ylabel : str, optional
            Label of the y-axis, by default "Resources".
        label_processes : bool, optional
            If set to True, processes are labeled on the Gantt chart, by default False.
        color_mode : int, optional
            Color mode for the Gantt chart, by default 0.
        save_to_disk : bool, optional
            If set to True, the Gantt chart is saved to disk, by default False.
        filename : str, optional
            The filename for saving the Gantt chart, by default "".

        Returns
        -------
        Figure
            The generated Gantt chart.
        """
        fig, gnt = plt.subplots()

        gnt.set_title(title)
        gnt.set_xlabel(xlabel)
        gnt.set_ylabel(ylabel)
        self._setup_plot_limits(gnt)
        self._setup_axis_ticks(gnt)

        gnt.grid(True)
        gnt.set_axisbelow(True)

        self._generate_color_dict(color_mode)
        self._plot_jobs(gnt, label_processes)

        legend_elements = self._create_legend(color_mode, 11)
        # plt.legend(handles=legend_elements, bbox_to_anchor=(1, 1), loc="upper right", ncol=len(legend_elements), fontsize=9)

        self._add_description(gnt, description)
        fig.tight_layout()

        if save_to_disk:
            self._save_figure(title, filename)

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

    def _get_color_for(self, job_name):
        return self._job_color_dict[job_name]

    def _generate_color_dict(self, mode: int = 0):
        """mode 0: Unique generated color for each job name
        mode 1: Unique color for each processing job, less saturated color for changeovers
        mode 2: All processing times have the same color, all changeovers have the same color
        """

        colors = self._generate_colors()

        unique_job_names = set([job.name for job in self._jobs])
        for count, job in enumerate(unique_job_names):
            if mode == 0 or mode == 1:
                self._job_color_dict[job] = colors[count]
            elif mode == 2:
                self._job_color_dict[job] = hsv_to_rgb([44 / 360, 0.70, 0.9])

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

    my_plotter = GanttPlotter(
        resources=resources, jobs=task_list, xticks_step_size=8, xticks_max_value=160
    )

    new_resource = "Unit 4"
    new_task = GanttJob(70, 15, "Unit 4", "Job4")

    my_plotter.add_resource(new_resource)
    my_plotter.add_job(new_task)

    script = os.path.basename(__file__)
    filename = "MyExampleGanttChart.png"

    my_plotter.generate_gantt(
        "Great Gantt", ylabel="", label_processes=True, color_mode=2
    )
    my_plotter.show_gantt()
