"""
Author: Igor Kim
E-mail: igor.skh@gmail.com
Repository: https://bitbucket.org/igorkim/fsvrreader

Reader module for R&S FSVR Signal Analyzer DAT files

April 2017
"""
from FSVRAnalysis import FSVRAnalysis
from FSVRReader import FSVRReader

# initialize reader object, could be different for different devices
reader = FSVRReader("dat/500mks.DAT")
# initialize analyzer main object
analyzer = FSVRAnalysis(reader)
# set number of points to analyze, or 0 if all points
analyzer.set_data_points(500)
# set reference level
analyzer.set_threshold(-80)
# get main information from the data file
analyzer.get_info()
# do things...
analyzer.last_frame_plot()
analyzer.avg_values_plot()