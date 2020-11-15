# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 00:59:01 2020

@author: Saeed
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from pycpd import RigidRegistration


class Registration():
    '''
    Rigid registration using PyCPD

    Arguments:
        - image_coords:     numpy array of the calculated centerline
        - tracker_coords:   numpy array of the recorded tool coords
    '''
    def __init__(self, image_coords, tracker_coords, patient_dir):
        super().__init__()
        self.target_coords = image_coords
        self.source_coords = tracker_coords
        self.patient_dir = patient_dir

    def visualize(self, X, ax, color):
        plt.cla()
        ax.scatter(X[:, 0],  X[:, 1], X[:, 2], color=color, marker='.')
        # ax.scatter(Y[:, 0],  Y[:, 1], Y[:, 2], color='blue', marker='^', label='Tool')
        plt.draw()

    def visualize(self, iteration, error, X, Y, ax):
        plt.cla()
        ax.scatter(X[:, 0],  X[:, 1], X[:, 2], color='red', marker='+', label='Target')
        ax.scatter(Y[:, 0],  Y[:, 1], Y[:, 2], color='blue', marker='^', label='Source')
        ax.text2D(0.87, 0.92, 'Iteration: {:d}\nQ: {:06.4f}'.format(
            iteration, error), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize='x-large')
        ax.legend(loc='upper left', fontsize='x-large')
        plt.draw()
        plt.pause(0.001)

    def coord2points(self, coords):
        # numPoints = coords.shape[-1]
        numPoints = len(coords)
        points = np.zeros([numPoints, 3])
        for i in range(numPoints):
            points[i,:] = coords[:,:,i][:,3][:-1]
        return points

    def reject_outliers(self, data, m=2):
        data_clean = []
        m = np.mean(data, axis=0)
        s = np.std(data, axis=0)
        for i in range(len(data)):
            if (abs(data - np.mean(data, axis=0)) < m * np.std(data,axis=0)).all():
                data_clean.append(data[i,:])
        return np.array(data_clean)

    def register(self):
        X = self.coord2points(self.target_coords)
        Y = self.coord2points(self.source_coords)

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        # ax = fig.add_subplot(111, projection='3d')
        callback = partial(self.visualize, ax=ax)

        reg = RigidRegistration(**{'X': X, 'Y': Y})
        reg.register(callback)

        RR = reg.R
        tt = reg.t
        reg_mat = np.array([[RR[0][0], RR[0][1], RR[0][2], tt[0]],
                            [RR[1][0], RR[1][1], RR[1][2], tt[1]],
                            [RR[2][0], RR[2][1], RR[2][2], tt[2]],
                            [0,         0,      0,          1]])

        print(reg_mat)
        plt.show()

        # TODO: save reg_mat in patient_dir
        return reg_mat

