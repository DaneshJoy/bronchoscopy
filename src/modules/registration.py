# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 10:39:30 2022

@author: Saeed
"""

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy


class Registeration:
    def __init__(self):
        # methods: icp, cpd, filterreg
        self.method = 'icp'
        self.regmat = None
        self.fixed = None
        self.moving = None
        self.moving_registered = None

    def set_points(self, fixed, moving):
        # TODO: Check the format of points
        self.fixed = fixed
        self.moving = moving

    def register(self, method):
        self.method = method
        is_registered = False

        if 'icp' in method.lower():
            self.regmat = self.register_icp()
            is_registered = True
        elif 'cpd' in method.lower():
            raise NotImplementedError
        elif 'filterreg' in method.lower():
            raise NotImplementedError
        else:
            is_registered = False
            print('❌ Unknown registration method: {method}')

        if not is_registered:
            print('❌ Registration encountered an error')
        else:  # registration successful
            print('✅ Registration completed successfully')
        return self.regmat

    def register_icp(self,
                     landmarkTransformType="RigidBody",
                     meanDistanceType="RMS",
                     start_by_matching_centroids=True):
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(self.moving)
        icp.SetTarget(self.fixed)

        if landmarkTransformType == "RigidBody":
            icp.GetLandmarkTransform().SetModeToRigidBody()
        elif landmarkTransformType == "Similarity":
            icp.GetLandmarkTransform().SetModeToSimilarity()
        elif landmarkTransformType == "Affine":
            icp.GetLandmarkTransform().SetModeToAffine()

        if meanDistanceType == "RMS":
            icp.SetMeanDistanceModeToRMS()
        elif meanDistanceType == "Absolute Value":
            icp.SetMeanDistanceModeToAbsoluteValue()

        # icp.DebugOn()
        icp.SetMaximumNumberOfIterations(30)
        if start_by_matching_centroids:
            icp.StartByMatchingCentroidsOn()
        icp.Modified()
        icp.Update()

        outputMatrix = vtk.vtkMatrix4x4()
        icp.GetMatrix(outputMatrix)
        matrix_np = np.eye(4)
        outputMatrix.DeepCopy(matrix_np.ravel(), outputMatrix)
        t = icp

        # Apply the transformation
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(t)
        transformFilter.SetInputData(self.source_points)
        transformFilter.Update()
        transformed_source = transformFilter.GetOutput()

        self.moving_registered = vtk_to_numpy(
            transformed_source.GetPoints().GetData())

        return matrix_np
