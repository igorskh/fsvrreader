# -*- coding: utf-8 -*-
"""
Author: Igor Kim
E-mail: igor.skh@gmail.com
Repository: https://bitbucket.org/igorkim/fsvrreader

Analysis module for R&S FSVR Signal Analyzer DAT files

April 2017
"""
import matplotlib.pyplot as plt
import numpy as np
import warnings


class FSVRAnalysis:
    """
    Module for analysis basically channel occupation
    """
    reader = None  #: object: dump file reader object from external class
    info_initialized = False #: bool: flag that get_info() method was executed
    threshold = 0.0  #: float: threshold level for analysis
    filter_mask = []  #: list: which frequencies will be used for analysis
    data_points = 10  #: int: number of points to be analysed
    f_span = 0.0  #: float: frequency span
    f_resolution = 0.0 #: float: frequency resolution
    freq = 0.0  #: float: central frequency
    start_ts = 0.0  #: float: start timestamp
    end_ts = 0.0  #: float: end timestamp
    duration = 0.0  #: float: sample duration from the first to the last data frame
    timeline = []

    @property
    def get_threshold(self):
        """
        Returns threshold
        :return: float: current threshold
        """
        return self.threshold

    @property
    def get_data_points(self):
        """
        Return number of points for analysis
        :return: 
            int: number of points for analysis
        """
        return self.data_points

    def set_threshold(self, value):
        """
        Sets a threshold level
        :param value: float: threshold level
        :return: 
        """
        self.threshold = value

    def set_data_points(self, value):
        """
        Sets number of points to analyze, if number of points more than available,
        method will set the maximum available number of points
        :param value: int; number of point to analyze
        :return: 
        """
        if 0 < value <= int(self.reader.get_data_frames_amount()):
            self.data_points = value
        else:
            self.data_points = int(self.reader.get_data_frames_amount())
            warnings.warn("Only " + str(self.data_points) + " data frame(s) are available, was set to this")

    @staticmethod
    def init_plot(xlabel="", ylabel="", title=""):
        """
        Prepares objects to plot
        :param xlabel: label on x axis
        :param ylabel: label on y axis
        :param title: title above the plot
        :return: fig, ax - figure object to process to finish_plot() method
        """
        fig = plt.figure()
        # set title
        fig.suptitle(title, fontsize=14, fontweight='bold')
        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=0.9)
        # set axis labels
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return fig,ax

    @staticmethod
    def finish_plot(fig, ax, filename=None, legend=None):
        """
        Finishes plotting the figure
        :param fig: object from init_plot method
        :param ax: object from init_plot method
        :param filename: filename to save figure
        :param legend: legend text
        :return: 
        """
        # if no object provided throw an exception
        if fig is None or ax is None:
            raise RuntimeError("Unable to preform figure plotting")
        axis = fig.gca()
        yr = abs(axis.get_ylim()[1] - axis.get_ylim()[0])
        xr = abs(axis.get_xlim()[1] - axis.get_xlim()[0])
        # plot legend on a figure
        if not legend is None:
            ax.text(axis.get_xlim()[0] + xr * 0.03,
                    axis.get_ylim()[1] - 0.06 * yr * (legend.count("\n")),
                    legend, bbox={'facecolor': 'blue', 'alpha': 0.2, 'pad': 5})
        if filename is None:
            plt.show()
        else:
            plt.savefig(filename)

    def get_info(self):
        """
        Calculates basic info, start and end timestamp, sample duration,
        central frequency and a frequency span
        :return: bool: True if successful, False otherwise.
        """
        self.info_initialized = True
        # start from the 0 frame
        self.reader.reopen_file()
        # start and end timestamp
        self.start_ts = 0
        self.end_ts = 0
        # go though the data points
        for i in range(self.data_points):
            self.reader.read_frame()
            if i == 0:
                self.end_ts = self.reader.get_last_frame()['Timestamp']
                # get frequency boundaries
                keys = list(self.reader.get_last_frame()['Data'].keys())
                self.freq = keys[int(round(len(keys)/2,0))]
                self.f_span = abs(keys[0] - keys[len(keys)-1])
                self.f_resolution = abs(keys[1] - keys[0])
            elif i == self.data_points-1:
                self.start_ts = self.reader.get_last_frame()['Timestamp']
        self.duration = round(self.end_ts - self.start_ts,3)
        self.timeline = np.linspace(0, self.duration, self.data_points)
        self.info_initialized = True
        return True

    def filtering_statistic_analyze(self):
        """
        Evaluates filtered values of data frames over time
        :return: list: filtered values
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        if not self.info_initialized:
            self.get_info()
        result = []
        # go though the data points
        for i in range(self.data_points):
            self.reader.read_frame()
            # calculate average value over filtered frequencies
            avg = 0
            for filter_val in self.filter_mask:
                avg += self.reader.get_last_frame()['Data'][filter_val]
            avg = avg / len(self.filter_mask)
            result.append(avg)
        return result

    def max_values(self):
        """
        Gets maximum value of data frames
        :return: dict: maximum level in all data frames {f1: l1, ..., fn: ln}
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        if not self.info_initialized:
            self.get_info()
        # start from the 0 frame
        self.reader.reopen_file()
        result = {}
        # go though the data points
        for i in range(self.data_points):
            self.reader.read_frame()
            vals = list(self.reader.get_last_frame()['Data'].values())
            keys = list(self.reader.get_last_frame()['Data'].keys())
            # get the max value over the last data frame
            max_val = max(vals)
            # get the index of max value
            max_idx = vals.index(max_val)
            result[keys[max_idx]] = max_val
        return result

    def values_over_threshold(self):
        """
        Find which maximum values are greater than a threshold
        :return: dict: maximum values greater than a threshold for all data frames
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        if not self.info_initialized:
            self.get_info()
        # get max values over the frames
        max_vals = self.max_values()
        result = {}
        # leave only value which are greater than threshold
        for key, val in max_vals.items():
            if val >= self.threshold:
                result[key] = val
        return result

    def avg_values(self):
        """
        Find average over the all data frame values
        :return: list: averaged values for all data frames
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to do take an average")
            return False
        if not self.info_initialized:
            self.get_info()
        # start from the 0 frame
        self.reader.reopen_file()
        result = []
        # go though the data points
        for i in range(self.data_points):
            self.reader.read_frame()
            cnt = len(self.reader.get_last_frame()['Data'])
            result.append(sum(list(self.reader.get_last_frame()['Data'].values()))/cnt)
        return result

    def plot_filtering_statistic(self):
        """
        Plots filtered values statistic
        :return: 
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        # start from the 0 frame
        self.reader.reopen_file()
        # get filtering statistic
        td = self.filtering_statistic_analyze()

        fig, ax = self.init_plot("Data Frame", "Level", "Filtered statistic")
        # plot the threshold line
        ax.plot([self.threshold for i in range(len(td))], 'b-')
        # plot filtered values
        ax.plot(td, "ro")
        self.finish_plot(fig, ax, self.reader.get_filename() + "_threshold_statistic" + str(self.data_points) + ".png")

    def plot_cdf(self):
        """
        :return: 
        """
        result = self.avg_values()
        # delta time points
        ares = []
        # last time point to calc delta
        last_time_point = 0
        for i in range(self.get_data_points):
            # take only points above the threshold
            if result[i] >= self.get_threshold:
                ares.append(self.timeline[i] - last_time_point)
                last_time_point = self.timeline[i]
        # sort delta time points
        ares = sorted(ares)
        # normalize data
        ares1 = ares / np.sum(ares)
        # get the cumulative sum
        cum_ares = np.cumsum(ares1)
        fig, ax = self.init_plot("Delta time (s)", "CDF",
                                 "Carrier = " + str(self.freq) + " " + self.reader.get_axis_units()[0])
        plt.plot(ares, cum_ares)
        self.finish_plot(fig, ax, self.reader.get_filename() + "_cdf_" + str(self.data_points)+".png",
                         "Duration = " + str(self.duration) + " s\n" +
                         "Sweep time = " + str(self.reader.get_sweep_time()) + " s\n" +
                         "F resolution = " + str(self.f_resolution) + " " + self.reader.get_axis_units()[0] + '\n' +
                         "F span = " + str(self.f_span) + " " + self.reader.get_axis_units()[0])

    def plot_avg_values(self):
        """
        Plots averaged values over the data frames
        :return: 
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to do take an average")
            return False
        # get averaged values
        avg_eval = self.avg_values()

        values_over_threshold = sum(i > self.threshold for i in avg_eval)
        occupation_ratio = round(values_over_threshold*100 / len(avg_eval), 2)
        # initialize plot objects
        fig, ax = self.init_plot("Time (s)", "Level ("+self.reader.get_axis_units()[1]+")",
                                 "Carrier = " + str(self.freq) + " " + self.reader.get_axis_units()[0])
        # plot averaged levels
        ax.plot(self.timeline, avg_eval, 'ro')
        # plot horizontal threshold line
        ax.plot(self.timeline, [self.threshold for i in range(self.data_points)], 'b-')
        self.finish_plot(fig, ax, self.reader.get_filename() + "_avg_" + str(self.data_points) + ".png",
                         "Duration = " + str(self.duration) + " s\n" +
                         "Sweep time = " + str(self.reader.get_sweep_time()) + " s\n" +
                         "F resolution = " + str(self.f_resolution) + " " + self.reader.get_axis_units()[0] + '\n' +
                         "F span = " + str(self.f_span) + " " + self.reader.get_axis_units()[0] + '\n' +
                         "Occupation Ratio = " + str(occupation_ratio) + "%")

    def plot_last_frame(self):
        """
        Plots on the graph the last frame
        :return: 
        """
        # get last frame data
        frame = self.reader.get_last_frame()

        fig, ax = self.init_plot(self.reader.get_axis_units()[0], self.reader.get_axis_units()[1],
                       "Frame #" + str(frame['Frame']) + " at " + str(frame['Timestamp']))
        ax.plot(list(frame['Data'].keys()), list(frame['Data'].values()), 'ro')
        self.finish_plot(fig, ax, self.reader.get_filename() + "_figure_fr" + str(frame['Frame']) + ".png",
                         "Carrier = "+str(self.freq)+" "+self.reader.get_axis_units()[0])

    def plot_frame(self):
        """
        Plots set self.data_points frame
        :return: 
        """
        # start from the 0 frame
        self.reader.reopen_file()
        # go though the data points
        for i in range(self.data_points):
            self.reader.read_frame()
        self.last_frame_plot()

    def __init__(self, reader):
        """
        :param reader: reader object from an external module
        """
        self.reader = reader
