# -*- coding: utf-8 -*-
"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer

April 2017
"""

import os.path
import datetime


class FSVRReader:
    """
    Reader module implementation for reading R&S FSVR Signal Analyzer dump files
    """
    file_path = ""  #: object: path to the file
    last_frame = {}  #: dict: last data frame data
    header_end = 0  #: int: byte where the header ends
    file = None  #: object: file object
    header = {}  #: dict: header dictionary

    def __init__(self, filename):
        """
        :param filename: path to the dat file
        """
        if os.path.isfile(filename):
            self.file_path = filename
            self.file = open(self.file_path, "r")
            self.read_header()

    def read_line(self):
        """
        Reads next line of the file
        :return: str: line data
        """
        result = self.file.readline()
        return result

    def get_axis_units(self):
        """
        :return: tuple: (x unit,y unit)
        """
        return self.header['x-Unit'][0], self.header['y-Unit'][0]

    def get_data_frames_amount(self):
        """
        :return: int: number of data frames
        """
        return int(self.header['Frames'][0])

    def get_last_frame(self):
        """
        :return: object: last frame object
        """
        return self.last_frame

    def get_sweep_time(self):
        """
        Returns sweep time got from a header
        :return: float: sweep time
        """
        return float(self.header['SWT'][0])

    def read_header(self, limit=30):
        """
        Reads file header, must be used first after initialization
        :param limit: max lines for header
        :return: bool: True if successful, False otherwise.
        """
        for i in range(limit):
            values = self.read_line().rstrip().split(";")
            self.header[values[0]] = values[1:]
            if values[0] == "Frames":
                # get the pointer where the header ends
                self.header_end = self.file.tell()
                return True
        return False

    def reopen_file(self):
        """ Reopens file to the position of first frame, skips header
        :return: object: File object
        """
        self.file.close()
        self.file = open(self.file_path, "r")
        self.file.seek(self.header_end)
        return self.file

    def read_frame(self):
        """
        Reads next frame
        :return: dict: frame data
        """
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
                    # example time 12.Apr 17;17:55:58.470
                    frame['Timestamp'] = datetime.datetime.strptime(frame['Date']+"T"+frame['Time'], "%d.%b %yT%H:%M:%S.%f").timestamp()
                else:
                    frame[values[0]] = values[1]
            # for values
            else:
                frame_data[float(values[0])] = float(values[1])
        frame['Data'] = frame_data
        self.last_frame = frame

        return frame
