# README #

This python modules are developed for analysing dump files of spectrum analyser R&D FSVR

### If you would like to use *FSVRAnalysis* class you have to write your own reader class, which is used in initialisation, following method should be defined: ###
* reopen_file() - resets pointer in the text file
* read_frame() - reads the next time frame followed by a current position of a pointer
* get_axis_units() - returns turple of axis units as strings (x,y), e.g. ("Hz", "dBm")
* get_last_frame() - returns dictionary with a frame information, described below
* get_data_frames_amount() - returns int, number of available frames
* get_sweep_time() - returns float, sweep time in seconds
### Information inside get_last_frame() returned dictionary
* ['Data'] - dictionary, keys are frequencies and values are levels {f1:l1, f2:l2, f3: l3, ...}
* ['Timestamp'] - float, timestamp of the data frame
* ['Frame'] - int, data frame order number
### Typical usage is in *test.py* file