"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Analysis module for R&S FSVR Signal Analyzer DAT files
"""
from FSVRReader import FSVRReader
import matplotlib.pyplot as plt


class FSVRAnalysis:
    reader = None
    threshold = 0
    filter_mask = []

    '''
    Evaluates time differences between data frames
    '''
    def time_delta_eval(self, n=10):
        """
        Evaluates delta time between frames
        """
        time_delta = []
        last_time = 0
        for i in range(n):
            self.reader.read_frame()
            if i == 0:
                time_delta.append(0)
            else:
                time_delta.append(last_time - self.reader.last_frame['Timestamp'])
            last_time = self.reader.last_frame['Timestamp']

        return time_delta

    '''
    Plots time differences between data frames
    '''
    def time_delta_plot(self, n=10):
        # start from the 0 frame
        self.reader.reopen_file()
        td = self.time_delta_eval(n)
        plt.plot(td, "ro")
        plt.xlabel("Frame")
        plt.ylabel("Time Difference")
        plt.savefig("time_delta_eval" + str(n) + ".png")
        plt.clf()

    '''
    Plots filtered values statistic
    '''
    def filtering_statistic_plot(self, n=10):
        # start from the 0 frame
        self.reader.reopen_file()
        # get filtering statistic
        td = self.filtering_statistic_analyze(n)
        # plot the threshold line
        plt.plot([self.threshold for i in range(len(td))], 'b-')
        # plot filtered values
        plt.plot(td, "ro")
        plt.xlabel("Data Frame")
        plt.ylabel("Level")
        plt.savefig("threshold_statistic" + str(n) + ".png")
        plt.clf()

    '''
    Evaluates data using filter mask, several values of filters are averaged 
    '''
    def filtering_statistic_analyze(self, n=10):
        result = []
        # go though the data points
        for i in range(n):
            self.reader.read_frame()
            # calculate average value over filtered frequencies
            avg = 0
            for filter_val in self.filter_mask:
                avg += self.reader.last_frame['Data'][filter_val]
            avg = avg / len(self.filter_mask)
            result.append(avg)
        return result

    '''
    Gets maximum value of data frames
    '''
    def max_values(self, n=10):
        # start from the 0 frame
        self.reader.reopen_file()
        result = {}
        # go though the data points
        for i in range(n):
            self.reader.read_frame()
            vals = list(self.reader.last_frame['Data'].values())
            keys = list(self.reader.last_frame['Data'].keys())
            # get the max value over the last data frame
            max_val = max(vals)
            # get the index of max value
            max_idx = vals.index(max_val)
            result[keys[max_idx]] = max_val
        return result

    '''
    Initialize analysis
    '''
    def __init__(self, filename):
        self.reader = FSVRReader(filename)