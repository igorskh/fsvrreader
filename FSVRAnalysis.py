# -*- coding: utf-8 -*-
"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Analysis module for R&S FSVR Signal Analyzer DAT files

April 2017
"""
import matplotlib.pyplot as plt


class FSVRAnalysis:
    reader = None
    threshold = 0
    filter_mask = []
    # number of points to be analysed
    data_points = 10
    # frequency span
    f_span = None
    # central frequency
    freq = None
    # start and end timestamp
    start_ts = None
    end_ts = None
    # analysis duration
    duration = None

    '''
    '''
    def set_threshold(self, value):
        self.threshold = value

    '''
    Sets number of points to analyze
    '''
    def set_data_points(self, value):
        if value < int(self.reader.get_data_frames_amount()):
            self.data_points = value
        else:
            # TODO: throw error not enough points
            print("Only "+str(self.reader.get_data_frames_amount())+' data frame(s) are available' )
            self.data_points = int(self.reader.get_data_frames_amount())-1

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
                self.end_ts = self.reader.get_last_frame()['Timestamp']
                # get frequency boundaries
                keys = list(self.reader.get_last_frame()['Data'].keys())
                self.freq = keys[int(round(len(keys)/2,0))]
                self.f_span = abs(keys[0] - keys[len(keys)-1])
            elif i == self.data_points:
                self.start_ts = self.reader.get_last_frame()['Timestamp']
        self.duration = round(self.end_ts - self.start_ts,3)
        return True

    '''
    Evaluates time differences between data frames
    '''
    def time_delta_eval(self):
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        time_delta = []
        last_time = 0
        for i in range(self.data_points+1):
            self.reader.read_frame()
            if i == 0:
                time_delta.append(0)
            else:
                time_delta.append(last_time - self.reader.get_last_frame()['Timestamp'])
            last_time = self.reader.get_last_frame()['Timestamp']

        return time_delta

    '''
    Plots time differences between data frames
    '''
    def time_delta_plot(self):
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
        plt.savefig("time_delta_eval" + str(self.data_points) + ".png")
        plt.clf()

    '''
    Evaluates data using filter mask, several values of filters are averaged 
    '''
    def filtering_statistic_analyze(self):
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        result = []
        # go though the data points
        for i in range(self.data_points+1):
            self.reader.read_frame()
            # calculate average value over filtered frequencies
            avg = 0
            for filter_val in self.filter_mask:
                avg += self.reader.get_last_frame()['Data'][filter_val]
            avg = avg / len(self.filter_mask)
            result.append(avg)
        return result

    '''
    Plots filtered values statistic
    '''
    def filtering_statistic_plot(self):
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
        plt.savefig("threshold_statistic" + str(self.data_points) + ".png")
        plt.clf()

    '''
    Gets maximum value of data frames
    '''
    def max_values(self):
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to perform an analysis")
            return False
        # start from the 0 frame
        self.reader.reopen_file()
        result = {}
        # go though the data points
        for i in range(self.data_points+1):
            self.reader.read_frame()
            vals = list(self.reader.get_last_frame()['Data'].values())
            keys = list(self.reader.get_last_frame()['Data'].keys())
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

    '''
    Average values
    '''
    def avg_values(self):
        if self.reader.get_data_frames_amount() < 2:
            print("At least 2 data frames are needed to do take an average")
            return False
        # start from the 0 frame
        self.reader.reopen_file()
        result = []
        # go though the data points
        for i in range(self.data_points+1):
            self.reader.read_frame()
            cnt = len(self.reader.get_last_frame()['Data'])
            result.append(sum(list(self.reader.get_last_frame()['Data'].values()))/cnt)
        return result

    '''
    Plots averaged values over the data frames
    '''
    def avg_values_plot(self):
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
        ax.plot(avg_eval, 'ro')
        # plot horizontal threshold line
        ax.plot([self.threshold for i in range(self.data_points)], 'b-')
        # set axis labels
        ax.set_xlabel('Data frame')
        ax.set_ylabel(self.reader.get_axis_units()[1])
        # get axis information
        axis = fig.gca()
        # draw legend
        yr = abs(axis.get_ylim()[1] - axis.get_ylim()[0])
        xr = abs(axis.get_xlim()[1] - axis.get_xlim()[0])
        ax.text(axis.get_xlim()[0]+xr*0.03, axis.get_ylim()[1]-0.18*yr,
                'Duration = '+ str(self.duration)+" s\n" +
                'Sweep time = ' + str(self.reader.get_sweep_time())+" s\n" +
                "F span = " + str(self.f_span) + " "+self.reader.get_axis_units()[0] +'\n' +
                'Ratio = ' + str(occupation_ratio) + '%',
                style='italic', bbox={'facecolor': 'blue', 'alpha': 0.3, 'pad': 5})
        # save plot
        plt.savefig("avg" + str(self.data_points) + ".png")
        # clear plot
        plt.clf()

    '''
    Plots last frame
    '''
    def last_frame_plot(self):
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
        plt.savefig("figure" + str(frame['Frame']) + ".png")
        plt.clf()

    '''Plots set self.data_points frame'''
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
    def __init__(self, reader):
        self.reader = reader