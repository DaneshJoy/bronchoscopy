# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 16:05:56 2020

@author: Saeed
"""

import threading
from sksurgerynditracker.nditracker import NDITracker


class Tracker():
    def __init__(self):
        super().__init__()
        self.tracker = None
        self.tracker_ready = False
        self.tracker_connected = False
        self.capture_coords = False

    def connect(self):
        if self.tracker is None:
            # settings_aurora = { "tracker type": "aurora", "ports to use" : [5]}
            settings_aurora = { "tracker type": "aurora"}
            try:
                self.tracker = NDITracker(settings_aurora)
                self.captureCoordinates = True
                self.tracker.start_tracking()
                tool_desc = self.tracker.get_tool_descriptions()
                self.tracker_connected = True

                # Multithreading Method 1 (recomended)
                thread_tracker = threading.Thread(target=self.trackerLoop)
                thread_tracker.start()
                # thread_updateViews = threading.Thread(target=self.showToolOnViews(self.registered_tool))
                # thread_updateViews.start()
                # Multithreading Method 2 (not recomended)
                # Use QApplication.processEvents() inside the loop
                return True
            except:
                self.tracker_connected = False
                return False
            
    def disconnect(self):
        self.capture_coords = False
        self.tracker_connected = False
        self.tracker.stop_tracking()
        self.tracker.close()
        self.tracker = None

    def get_frame(self):
        data = self.tracker.get_frame()
        # Data is numpy.ndarray(4x4)
        ref_mat = data[3][0]  # Ref must be attached to the 1st port
        tool_mat = data[3][1]  # Tool must be attached to the 2nd port
        return ref_mat, tool_mat


