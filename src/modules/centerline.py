# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 14:20:57 2020

@author: Saeed
"""

import os
from vmtk import pypes, vmtkscripts, vmtkcenterlines 
import numpy as np
import vtk


class Centerline():
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def extract(self):
        myArguments = f'vmtkimagereader -ifile \"{self.image_path}\" --pipe vmtkmarchingcubes \
            -i @vmtkimagereader.o -l 0.5 --pipe vmtkcenterlines -ofile points.dat --pipe vmtkrenderer \
            --pipe vmtksurfaceviewer -opacity 0.25 --pipe vmtksurfaceviewer -i @vmtkcenterlines.o -array MaximumInscribedSphereRadius'

        myPype = pypes.PypeRun(myArguments)

        myCenterline = myPype.GetScriptObject('vmtkcenterlines','0').Centerlines

        # TODO: load XyzToRas from patient_dir + squeeze
        XyzToRas = myPype.GetScriptObject('vmtkimagereader','0').XyzToRasMatrixCoefficients
        XyzToRas = np.array([[XyzToRas[0:4]],
                            [XyzToRas[4:8]],
                            [XyzToRas[8:12]],
                            [XyzToRas[12:16]]])
        p = [0,0,0]
        numPoints = myCenterline.GetNumberOfPoints()
        center_points = np.zeros([4,4,numPoints])
        for i in range(numPoints):
            myCenterline.GetPoints().GetPoint(i,p)
            p_tmp = np.array([[1, 0, 0, p[0]],
                            [0, 1, 0, p[1]],
                            [0, 0, 1, p[2]],
                            [0, 0, 0, 1]])
            # Apply XYZ2RAS matrix to match the orientation of the image
            p_aligned = np.squeeze(np.matmul(XyzToRas, p_tmp))
            center_points[:,:,numPoints-i-1] = p_tmp

        np.save(os.path.join(self.patient_dir, 'phantom_centerline.npy'), center_points)