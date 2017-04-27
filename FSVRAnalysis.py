# -*- coding: utf-8 -*-
"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

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
    threshold = 0.0  #: float: threshold level for analysis
    filter_mask = []  #: list: which frequencies will be used for analysis
    data_points = 10  #: int: number of points to be analysed
    f_span = 0.0  #: float: frequency span
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

    def get_info(self):
        """
        Calculates basic info, start and end timestamp, sample duration,
        central frequency and a frequency span
        :return: bool: True if successful, False otherwise.
        """
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
            elif i == self.data_points-1:
                self.start_ts = self.reader.get_last_frame()['Timestamp']
        self.duration = round(self.end_ts - self.start_ts,3)
        self.timeline = np.linspace(0, self.duration, self.data_points)
        return True

    def time_delta_eval(self):
        """
        Evaluates differences between each two data frames
        :return: list: delta time
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        time_delta = []
        last_time = 0
        for i in range(self.data_points):
            self.reader.read_frame()
            if i == 0:
                time_delta.append(0)
            else:
                time_delta.append(last_time - self.reader.get_last_frame()['Timestamp'])
            last_time = self.reader.get_last_frame()['Timestamp']
        return time_delta

    def time_delta_plot(self):
        """
        Plots the differences between each two data frames using time_delta_eval() method
        :return: 
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        # start from the 0 frame
        self.reader.reopen_file()
        td = self.time_delta_eval()
        plt.plot(td, "ro")
        plt.xlabel("Frame")
        plt.ylabel("Time Difference")
        plt.title("duration " + str(self.duration)+" s at "+str(self.freq)+" "+self.reader.get_axis_units()[0])
        plt.savefig(self.reader.get_filename() + "_time_delta_eval" + str(self.data_points) + ".png")
        plt.clf()

    def filtering_statistic_analyze(self):
        """
        Evaluates filtered values of data frames over time
        :return: list: filtered values
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
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

    def filtering_statistic_plot(self):
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
        # plot the threshold line
        plt.plot([self.threshold for i in range(len(td))], 'b-')
        # plot filtered values
        plt.plot(td, "ro")
        plt.xlabel("Data Frame")
        plt.ylabel("Level")
        plt.savefig(self.reader.get_filename() + "_threshold_statistic" + str(self.data_points) + ".png")
        plt.clf()

    def max_values(self):
        """
        Gets maximum value of data frames
        :return: dict: maximum level in all data frames {f1: l1, ..., fn: ln}
        """
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
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
        # start from the 0 frame
        self.reader.reopen_file()
        result = []
        # go though the data points
        for i in range(self.data_points):
            self.reader.read_frame()
            cnt = len(self.reader.get_last_frame()['Data'])
            result.append(sum(list(self.reader.get_last_frame()['Data'].values()))/cnt)
        return result

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
        # set axis labels
        plt.xlabel('Delta time')
        plt.ylabel('CDF')
        # plot the 1 porbability line
        plt.plot(ares, [1 for i in range(len(ares))], 'y--')
        plt.plot(ares, cum_ares)
        plt.savefig(self.reader.get_filename() + "_cdf_" + str(self.data_points)+".png")


    def avg_values_plot(self):
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

        fig = plt.figure()
        # set plot title
        fig.suptitle('Carrier = '+str(self.freq)+" "+self.reader.get_axis_units()[0], fontsize=14, fontweight='bold')
        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=0.9)
        # plot averaged levels
        ax.plot(self.timeline, avg_eval, 'ro')
        # plot horizontal threshold line
        ax.plot(self.timeline, [self.threshold for i in range(self.data_points)], 'b-')
        # set axis labels
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Level ('+self.reader.get_axis_units()[1]+')')
        # get axis information
        axis = fig.gca()
        # draw legend
        yr = abs(axis.get_ylim()[1] - axis.get_ylim()[0])
        xr = abs(axis.get_xlim()[1] - axis.get_xlim()[0])
        ax.text(axis.get_xlim()[0]+xr*0.03, axis.get_ylim()[0]+0.06*yr,
                'Duration = '+ str(self.duration)+" s\n" +
                'Sweep time = ' + str(self.reader.get_sweep_time())+" s\n" +
                "F span = " + str(self.f_span) + " "+self.reader.get_axis_units()[0] +'\n' +
                'Ratio = ' + str(occupation_ratio) + '%',
                style='italic', color='white', bbox={'facecolor': 'black', 'alpha': 0.6, 'pad': 5})
        # save plot
        plt.savefig(self.reader.get_filename() + "_avg_" + str(self.data_points) + ".png")
        # clear plot
        plt.clf()

    def last_frame_plot(self):
        """
        Plots on the graph the last frame
        :return: 
        """
        # get last frame data
        frame = self.reader.get_last_frame()
        fig = plt.figure()
        fig.suptitle('Frame #'+str(frame['Frame']) + ' at ' + str(frame['Timestamp']), fontsize=14, fontweight='bold')
        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=0.9)
        ax.plot(list(frame['Data'].keys()), list(frame['Data'].values()), 'ro')
        # set axis labels
        ax.set_xlabel(self.reader.get_axis_units()[0])
        ax.set_ylabel(self.reader.get_axis_units()[1])
        axis = fig.gca()
        yr = abs(axis.get_ylim()[1] - axis.get_ylim()[0])
        xr = abs(axis.get_xlim()[1] - axis.get_xlim()[0])
        ax.text(axis.get_xlim()[0]+xr*0.03, axis.get_ylim()[1]-0.06*yr,
                'Carrier = '+str(self.freq)+" "+self.reader.get_axis_units()[0],
                style='italic', bbox={'facecolor': 'blue', 'alpha': 0.2, 'pad': 5})
        plt.savefig(self.reader.get_filename() + "_figure_fr" + str(frame['Frame']) + ".png")
        plt.clf()

    def frame_plot(self):
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
