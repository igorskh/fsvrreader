"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer
"""

import os.path
import time
import datetime


class FSVRReader:
    file_path = ""
    next_line = 1
    next_frame = 0
    last_frame = {}
    header_end = 0
    file = None
    header = {}
    # sweep time multiplier
    # TODO: sweep time usage works incorrectly
    # swt_mlt = 0

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
            self.read_header()
            self.header['SWT'][0] = float(self.header['SWT'][0])
            if (self.header['SWT'][0] < 0.001):
                self.swt_mlt = 1

    '''
    Reads file header, must be used first after initialization
    '''
    def read_header(self, limit = 30):
        if len(self.header) >0:
            return False
        for i in range(limit):
            values = self.read_line().rstrip().split(";")
            self.header[values[0]] = values[1:]
            if values[0] == "Frames":
                self.header_end = self.file.tell()
                return True
        return False

    '''
    Reopens file to the position of first frame
    '''
    def reopen_file(self):
        self.file.close()
        self.file = open(self.file_path, "r")
        self.file.seek(self.header_end)
        return self.file

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
                else:
                    frame[values[0]] = values[1]
            # for values
            else:
                frame_data[float(values[0])] = float(values[1])
        frame['Data'] = frame_data
        self.last_frame = frame

        return frame
