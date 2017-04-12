"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer
"""

import os.path
import matplotlib.pyplot as plt
import time
import datetime


class FSVRReader:
    file_path = ""
    next_line = 1
    next_frame = 0
    last_frame = {}
    file = None
    header = {}

    threshold = 0
    filter = []

    '''
    Read one line of a file, increases a next_line counter
    '''
    def read_line(self):
        result = self.file.readline()
        self.next_line += 1
        return result

    '''
    Init function, inits file
    '''
    def __init__(self, filename):
        if os.path.isfile(filename):
            self.next_line = 1
            self.file_path = filename
            self.file = open(self.file_path, "r")

    '''
    Reads file header, must be used first after initialization
    '''
    def read_header(self, limit = 25):
        for i in range(limit):
            values = self.read_line().rstrip().split(";")
            self.header[values[0]] = values[1:]
            if values[0] == "Frame":
                return True
        return False

    '''
    Reads next data frame
    '''
    def read_frame(self):
        frame = {}
        frame_data = {}
        # read the number provided by Values number in the header
        for i in range(int(self.header['Values'][0])+2):
            values = self.read_line().rstrip().split(";")
            # for the frame header data
            if values[0] in ['Frame', 'Timestamp']:
                # evaluate timestamp
                if values[0] == 'Timestamp':
                    frame['Date'] = values[1]
                    frame['Time'] = values[2]
                    #12.Apr 17;17:55:58.470
                    # TODO: milliseconds do not saved in a timestamp format
                    frame['Timestamp'] = time.mktime(datetime.datetime.strptime(frame['Date']+"T"+frame['Time'], "%d.%b %yT%H:%M:%S.%f").timetuple())
                    # temporary fix
                    frame['Timestamp'] += float(frame['Time'][-4:])
                else:
                    frame[values[0]] = values[1]
            # for values
            else:
                frame_data[float(values[0])] = float(values[1])
        self.last_frame = frame
        frame['Data'] = frame_data

        return frame

    def plot_frame(self, frame={}):
        if len(frame) == 0:
            frame = self.last_frame
        plt.plot(list(frame['Data'].keys()), list(frame['Data'].values()))
        plt.xlabel(self.header['x-Unit'][0])
        plt.ylabel(self.header['y-Unit'][0])
        #value = datetime.datetime.fromtimestamp(frame['Timestamp'])
        #print(frame['Timestamp'], value.strftime("%d.%b %yT%H:%M:%S.%f"), frame['Date']+"T"+frame['Time'])
        plt.title(frame['Date']+" "+ frame['Time'] + " " +str(frame['Timestamp']) +" " +  " Frame #"+ frame['Frame'])
        plt.savefig("test.png")
        plt.clf()