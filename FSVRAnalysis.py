"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Analysis module for R&S FSVR Signal Analyzer DAT files

April 2017
"""
from FSVRReader import FSVRReader
import matplotlib.pyplot as plt


class FSVRAnalysis:
    reader = None
    threshold = 0
    filter_mask = []
    # number of points to be analysed
    data_points = 10
    # frequency span
    f_span = 0
    # central frequency
    freq = 0
    # start and end timestamp
    start_ts = 0
    end_ts = 0
    # analysis duration
    duration = 0

    '''
    Gets basic info
    '''
    def get_info(self):
        # start from the 0 frame
        self.reader.reopen_file()
        # start and end timestamp
        self.start_ts = 0
        self.end_ts = 0
        # go though the data points
        for i in range(self.data_points+1):
            self.reader.read_frame()
            if i == 0:
                self.end_ts = self.reader.last_frame['Timestamp']
                # get frequency boundaries
                keys = list(self.reader.last_frame['Data'].keys())
                self.freq = keys[int(round(len(keys)/2,0))]
                self.f_span = keys[0] - keys[len(keys)-1]
            elif i == self.data_points:
                self.start_ts = self.reader.last_frame['Timestamp']
        self.duration = round(self.end_ts - self.start_ts,3)
        return True

    '''
    Evaluates time differences between data frames
    '''
    def time_delta_eval(self):
        """
        Evaluates delta time between frames
        """
        time_delta = []
        last_time = 0
        for i in range(self.data_points+1):
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
    def time_delta_plot(self):
        # start from the 0 frame
        self.reader.reopen_file()
        td = self.time_delta_eval()
        plt.plot(td, "ro")
        plt.xlabel("Frame")
        plt.ylabel("Time Difference")
        plt.savefig("time_delta_eval" + str(self.data_points) + ".png")
        plt.clf()

    '''
    Evaluates data using filter mask, several values of filters are averaged 
    '''
    def filtering_statistic_analyze(self):
        result = []
        # go though the data points
        for i in range(self.data_points+1):
            self.reader.read_frame()
            # calculate average value over filtered frequencies
            avg = 0
            for filter_val in self.filter_mask:
                avg += self.reader.last_frame['Data'][filter_val]
            avg = avg / len(self.filter_mask)
            result.append(avg)
        return result

    '''
    Plots filtered values statistic
    '''
    def filtering_statistic_plot(self):
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
        plt.savefig("threshold_statistic" + str(self.data_points) + ".png")
        plt.clf()

    '''
    Gets maximum value of data frames
    '''
    def max_values(self):
        # start from the 0 frame
        self.reader.reopen_file()
        result = {}
        # go though the data points
        for i in range(self.data_points+1):
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
    Find values over threshold
    '''
    def values_over_threshold(self):
        max_vals = self.max_values()
        result = {}
        for key, val in max_vals.items():
            if val >= self.threshold:
                result[key] = val
        return result

    '''
    Average values
    '''
    def avg_values(self):
        # start from the 0 frame
        self.reader.reopen_file()
        result = []
        plt.plot([self.threshold for i in range(self.data_points)], 'b-')
        # go though the data points
        for i in range(self.data_points+1):
            self.reader.read_frame()
            cnt = len(self.reader.last_frame['Data'])
            vals = list(self.reader.last_frame['Data'].values())
            keys = list(self.reader.last_frame['Data'].keys())
            result.append(sum(vals)/cnt)
        return result

    '''
    Plots averaged values over the data frames
    '''
    def avg_values_plot(self):
        avg_eval = self.avg_values()

        plt.plot(avg_eval, 'ro')
        plt.xlabel('Data frame')
        plt.ylabel(self.reader.header['y-Unit'][0])
        plt.title("duration " + str(self.duration)+" s at "+str(self.freq)+" "+self.reader.header['x-Unit'][0])
        plt.savefig("avg"+str(self.data_points)+".png")
        plt.clf()

    '''
    Plots last frame
    '''
    def last_frame_plot(self):
        frame = self.reader.last_frame
        plt.plot(list(frame['Data'].keys()), list(frame['Data'].values()), 'ro')
        plt.xlabel(self.reader.header['x-Unit'][0])
        plt.ylabel(self.reader.header['y-Unit'][0])
        plt.title(frame['Date'] + " " + frame['Time'] + " " + str(frame['Timestamp']) + " " +  " Frame #"+ frame['Frame'])
        plt.savefig("figure"+str(frame['Frame'])+".png")
        plt.clf()

    '''Shows frame'''
    def frame_plot(self):
        # start from the 0 frame
        self.reader.reopen_file()
        # go though the data points
        for i in range(self.data_points+1):
            self.reader.read_frame()
        self.last_frame_plot()

    '''
    Initialize analysis
    '''
    def __init__(self, filename):
        self.reader = FSVRReader(filename)