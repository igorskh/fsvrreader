"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer DAT files
"""
from FSVRAnalysis import FSVRAnalysis


class Main:
    data_points = 10
    analyzer = None

    def __init__(self):
        while True:
            print(">", end=" ")
            cmd = str(input()).split(" ")
            if cmd[0] == 'exit':
                print("Bye!")
                break
            if hasattr(self, cmd[0]):
                getattr(self, cmd[0])(cmd)
            else:
                print("Command "+cmd[0]+" is not found")

    def tdp(self, params):
        self.analyzer.time_delta_plot(self.data_points)
        return True

    def fsp(self, params):
        self.analyzer.filtering_statistic_plot(self.data_points)
        return True

    def lfp(self, params):
        self.analyzer.last_frame_plot()
        return True

    def fp(self, params):
        if len(params) < 2:
            print("Not enough params")
            return False
        self.analyzer.frame_plot(int(params[1]))
        return True

    def clr_filter(self, params):
        if len(params) < 2:
            print("Not enough params")
            return False
        self.analyzer.filter_mask.clear()
        return True

    def add_filter(self, params):
        if len(params) < 2:
            print("Not enough params")
            return False
        self.analyzer.filter_mask.append(float(params[1]))
        return True

    def open(self, params):
        if len(params) < 2:
            print("Not enough params")
            return False
        self.analyzer = None
        self.analyzer = FSVRAnalysis(params[1])
        return True

    def points(self, params):
        if len(params) < 2:
            print("Not enough params")
            return False
        self.data_points = int(params[1])
        return True

    def threshold(self, params):
        if len(params) < 2:
            print("Not enough params")
            return False
        self.analyzer.threshold = float(params[1])
        return True


if __name__ == '__main__':
    # analyzer = FSVRAnalysis("252MKS_001.DAT")
    # analyzer.threshold = -75
    # analyzer.filter_mask = [2433075000.0]
    cln = Main()