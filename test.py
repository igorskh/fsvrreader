"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer DAT files

April 2017
"""
from FSVRAnalysis import FSVRAnalysis
from FSVRReader import FSVRReader

reader = FSVRReader("dat/500mks.DAT")
analyzer = FSVRAnalysis(reader)
analyzer.set_data_points(500)
analyzer.set_threshold(-80)
analyzer.get_info()
analyzer.last_frame_plot()
analyzer.avg_values_plot()