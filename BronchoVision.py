# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 01:09:45 2019

@author: Saeed
"""

import os
import sys
import vtk
import numpy.random.common # Just for PyInstaller to work
# import numpy.random.bounded_integers
# import numpy.random.entropy
import numpy as np
import time
from scipy.io import loadmat
import fix_qt_import_error
from PyQt5.Qt import QApplication, QMainWindow, QDialog, QColor, Qt, QIcon
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog, QTableWidgetItem, QLabel
from PyQt5.QtGui import QPalette
from ui.QVtkViewer import QVtkViewer3D, QVtkViewer2D
from ui import MainWindow, ToolsWindow, RegMatWindow
from sksurgerynditracker.nditracker import NDITracker

class myRegMatWindow(QDialog):
    def __init__(self, parent=None):
        super(myRegMatWindow, self).__init__(parent)
    
    def setData(self, regMat):
        for i in range(4):
            for j in range(4):
                newitem = QTableWidgetItem(str(regMat[i, j]))
                self.ui.table_regMat.setItem(i, j, newitem)

    def getData(self):
        regMat_new = np.zeros([4, 4], dtype='float')
        for i in range(4):
            for j in range(4):
                regMat_new[i, j] = float(self.ui.table_regMat.takeItem(i, j).text())
        return regMat_new

    def setup(self):
        self.ui = RegMatWindow.Ui_RegMatWindow()
        self.ui.setupUi(self)

class myToolsWindow(QDialog):
    def __init__(self, parent=None):
        super(myToolsWindow, self).__init__(parent)

    def setData(self, refData, toolData):
        if np.asarray(toolData).any():
            self.ui.r11_tool.setText(str(round(toolData[0,0], 3)))
            self.ui.r12_tool.setText(str(round(toolData[0,1], 3)))
            self.ui.r13_tool.setText(str(round(toolData[0,2], 3)))
            self.ui.r21_tool.setText(str(round(toolData[1,0], 3)))
            self.ui.r22_tool.setText(str(round(toolData[1,1], 3)))
            self.ui.r23_tool.setText(str(round(toolData[1,2], 3)))
            self.ui.r31_tool.setText(str(round(toolData[2,0], 3)))
            self.ui.r32_tool.setText(str(round(toolData[2,1], 3)))
            self.ui.r33_tool.setText(str(round(toolData[2,2], 3)))
            self.ui.t1_tool.setText(str(round(toolData[0,3], 2)))
            self.ui.t2_tool.setText(str(round(toolData[1,3], 2)))
            self.ui.t3_tool.setText(str(round(toolData[2,3], 2)))
        else:
            self.ui.r11_tool.setText('-')
            self.ui.r12_tool.setText('-')
            self.ui.r13_tool.setText('-')
            self.ui.r21_tool.setText('-')
            self.ui.r22_tool.setText('-')
            self.ui.r23_tool.setText('-')
            self.ui.r31_tool.setText('-')
            self.ui.r32_tool.setText('-')
            self.ui.r33_tool.setText('-')
            self.ui.t1_tool.setText('-')
            self.ui.t2_tool.setText('-')
            self.ui.t3_tool.setText('-')
        if np.asarray(refData).any():
            self.ui.r11_ref.setText(str(round(refData[0,0], 3)))
            self.ui.r12_ref.setText(str(round(refData[0,1], 3)))
            self.ui.r13_ref.setText(str(round(refData[0,2], 3)))
            self.ui.r21_ref.setText(str(round(refData[1,0], 3)))
            self.ui.r22_ref.setText(str(round(refData[1,1], 3)))
            self.ui.r23_ref.setText(str(round(refData[1,2], 3)))
            self.ui.r31_ref.setText(str(round(refData[2,0], 3)))
            self.ui.r32_ref.setText(str(round(refData[2,1], 3)))
            self.ui.r33_ref.setText(str(round(refData[2,2], 3)))
            self.ui.t1_ref.setText(str(round(refData[0,3], 2)))
            self.ui.t2_ref.setText(str(round(refData[1,3], 2)))
            self.ui.t3_ref.setText(str(round(refData[2,3], 2)))
        else:
            self.ui.r11_ref.setText('-')
            self.ui.r12_ref.setText('-')
            self.ui.r13_ref.setText('-')
            self.ui.r21_ref.setText('-')
            self.ui.r22_ref.setText('-')
            self.ui.r23_ref.setText('-')
            self.ui.r31_ref.setText('-')
            self.ui.r32_ref.setText('-')
            self.ui.r33_ref.setText('-')
            self.ui.t1_ref.setText('-')
            self.ui.t2_ref.setText('-')
            self.ui.t3_ref.setText('-')

    def setup(self):
        self.ui = ToolsWindow.Ui_ToolsWindow()
        self.ui.setupUi(self)

    # TODO: On close, set a flag to false

    # def initialize(self):
    #     pass

class myMainWindow(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.trackerReady = False
        self.captureCoordinates = False

        self.trackerRawCoords_ref = []
        self.trackerRawCoords_tool = []

        self.vtk_widget_3D = None
        self.vtk_widget_3D_2 = None
        self.vtk_widget_2D = None
        self.ui = None
        self.registeredPoints = None
        self.toolCoords = None
        self.refCoords = None
        self.setup(size)
        self.paused = False
        self.size = size
        self.cam_pos = None
        self.toolsWindow = myToolsWindow(self)
        self.toolsWindow.setup()
        self.regMatWindow = myRegMatWindow(self)
        self.regMatWindow.setup()
        self.tracker = None
        self.tracker_connected = False

        self.regMat = np.array([[0.84,      0.09,   -0.53,  -35.67],
                                [-0.51,     -0.14,  -0.85,  -202.98],
                                [-0.15,     0.99,   -0.07,  -22.7],
                                [0,         0,      0,          1]])

        self.ui.actionLoad_Image.triggered.connect(self.openFileDialog)
        self.ui.actionLoad_DICOM.triggered.connect(self.openDirDialog)
        self.ui.Slider_2D.valueChanged.connect(self.sliderChanged)

        self.ui.btn_LoadPoints.clicked.connect(self.readPoints)
        self.ui.checkBox_showPoints.stateChanged.connect(self.showHidePoints)
        self.ui.btn_playCam.clicked.connect(self.playCam)
        self.ui.btn_pauseCam.clicked.connect(self.pauseCam)
        self.ui.btn_stopCam.clicked.connect(self.stopCam)
        self.ui.slider_Frames.valueChanged.connect(self.frameChanged)
        self.ui.btn_ResetViewports.clicked.connect(self.ResetViewports)
        self.ui.btn_ResetVB.clicked.connect(self.ResetVB)
        self.ui.comboBox_2DView.currentIndexChanged.connect(self.change2DView)

        self.ui.btn_Connect.clicked.connect(self.connectTracker)
        self.ui.btn_ToolsWindow.clicked.connect(self.showToolsWindow)
        self.ui.btn_regMat.clicked.connect(self.showRegMatWindow)

    def connectTracker(self):
        if self.tracker_connected == False:
            self.ui.btn_Connect.setText('Connecting...')
            QApplication.setOverrideCursor(Qt.WaitCursor)

            if self.tracker is None:
                # settings_aurora = { "tracker type": "aurora", "ports to use" : [5]}
                settings_aurora = { "tracker type": "aurora"}
                if self.trackerReady:
                    try:
                        self.tracker = NDITracker(settings_aurora)
                        self.captureCoordinates = True
                    except:
                        msg = 'Please check the following:\n' \
                                '  1) Is an NDI device connected to your computer?\n' \
                                '  2) Is the NDI device switched on?\n' \
                                '  3) Do you have sufficient privilege to connect to the device?\n' \
                                '     (e.g. on Linux are you part of the \"dialout\" group?)'
                        QMessageBox.critical(self, 'Tracker Connection Failed', f'Can not connect to the tracker!\n{msg}')
                        return

                    self.tracker.start_tracking()
                    tool_desc = self.tracker.get_tool_descriptions()

            self.ui.btn_Connect.setText('Disconnect Tracker')
            self.ui.btn_ToolsWindow.setEnabled(True)
            self.tracker_connected = True
            icon = QIcon(":/icon/icons/tracker_connected.png")
            self.ui.btn_Connect.setIcon(icon)

            QApplication.restoreOverrideCursor()

            while self.captureCoordinates:
                if self.trackerReady:
                    data = self.tracker.get_frame()
                    # Data is numpy.ndarray(4x4)
                    self.refData = data[3][1]  # Ref must be attached to the 1st port
                    self.toolData = data[3][0]  # Tool must be attached to the 2nd port
                    if np.isnan(self.toolData.sum()) or np.isnan(self.refData.sum()):
                        # TODO: Show some messages or info
                        continue
                    
                    self.trackerRawCoords_ref.append(self.refData) 
                    self.trackerRawCoords_tool.append(self.toolData)    
                    self.showToolOnViews(self.toolData)
                    self.toolsWindow.setData(self.refData, self.toolData)
                else:
                    self.toolsWindow.setData(self.cam_pos, self.cam_pos)

                time.sleep(0.03)
                QApplication.processEvents()
        else:
            self.disconnectTracker()

    def disconnectTracker(self):
        if self.trackerReady:
            self.tracker.stop_tracking()
            self.tracker.close()

            np.save('trackerRawCoords_ref', self.trackerRawCoords_ref)
            np.save('trackerRawCoords_tool', self.trackerRawCoords_tool)
        self.tracker_connected = False
        self.captureCoordinates = False
        self.ui.btn_Connect.setText('Connect Tracker')
        self.ui.btn_ToolsWindow.setEnabled(False)
        icon = QIcon(":/icon/icons/tracker_disconnected.png")
        self.ui.btn_Connect.setIcon(icon)

    def showToolsWindow(self):
        self.toolsWindow.setData(self.cam_pos, self.cam_pos)
        self.toolsWindow.show()

    def showRegMatWindow(self):
        self.regMatWindow.setData(self.regMat)
        res = self.regMatWindow.exec()
        if (res == QDialog.Accepted):
            self.regMat = self.regMatWindow.getData()
        print(self.regMat)

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Medical Image", "", "Medical Images (*.nii *.nii.gz *.mhd *.mha);;Nifti (*.nii *.nii.gz);;Meta (*.mhd *.mha);;All Files (*)", options=options)
        # QMessageBox.information(self, 'Test Message', fileName)
        if fileName:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            extension = os.path.splitext(fileName)[1].lower()
            try:
                if 'nii' in extension or 'gz' in extension:
                    reader = vtk.vtkNIFTIImageReader()
                    reader.SetFileName(fileName)
                elif 'mhd' in extension or 'mha' in extension:
                    reader = vtk.vtkMetaImageReader()
                    reader.SetFileName(fileName)
            except:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, 'Unknown File Type', 'Can not load selected image!')
                return
                
            reader.Update()

            # TODO : Read image orientation and apply IJK to RAS transform (i.e. different flipping for each orientation) 
            # import SimpleITK as sitk
            # reader = sitk.ImageFileReader()
            # reader.SetFileName(fileName)
            # reader.Execute()
            # dd = reader.GetDirection()

            # Load dimensions using `GetDataExtent`
            # xMin, xMax, yMin, yMax, zMin, zMax = reader.GetDataExtent()
            _extent = reader.GetDataExtent()
            self.dims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]

            self.spacing = reader.GetOutput().GetSpacing()
            self.origin = reader.GetOutput().GetOrigin()
            # self.origin = (0, 0, 0)

            # # Flip and Translate the image to the right place
            # flipXFilter = vtk.vtkImageFlip()
            # flipXFilter.SetFilteredAxis(0); # flip x axis
            # flipXFilter.SetInputConnection(reader.GetOutputPort())
            # flipXFilter.Update()

            # flipYFilter = vtk.vtkImageFlip()
            # flipYFilter.SetFilteredAxis(1); # flip y axis
            # flipYFilter.SetInputConnection(flipXFilter.GetOutputPort())
            # flipYFilter.Update()

            if 'nii' in extension or 'gz' in extension:
                try:
                    _QMatrix = reader.GetQFormMatrix()
                    # self.origin = (0, 0, 0)
                    self.origin = (-_QMatrix.GetElement(0,3), -_QMatrix.GetElement(1,3), _QMatrix.GetElement(2,3))
                    imageInfo = vtk.vtkImageChangeInformation()
                    imageInfo.SetOutputOrigin(self.origin)
                    imageInfo.SetInputConnection(reader.GetOutputPort())
                    self.imgReader = imageInfo
                    self.showImages(self.imgReader, self.dims)
                except:
                    QMessageBox.warning(self, 'Wrong Header', 'Can not read Image Origin from header!\nImage position might be wrong')
            else:
                # origin = (140, 140, -58)
                # imageInfo = vtk.vtkImageChangeInformation()
                # imageInfo.SetOutputOrigin(self.origin)
                # imageInfo.SetInputConnection(reader.GetOutputPort())
                # self.showImages(imageInfo, self.dims)
                self.imgReader = reader
                self.showImages(self.imgReader, self.dims)

            self.updateSubPanels(self.dims)
            QApplication.restoreOverrideCursor()

    def openDirDialog(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select a Directory", "" )

        if dirname:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            reader = vtk.vtkDICOMImageReader()
            reader.SetDirectoryName(dirname)

            # reader1 = sitk.ImageSeriesReader()
            # dicom_names = reader1.GetGDCMSeriesFileNames(dirname)
            fileNames = vtk.vtkStringArray()
            dicom_names = os.listdir(dirname)
            for f in dicom_names:
                fileNames.InsertNextValue(f)
            reader.SetFileNames(fileNames)
            reader.Update()

            # TODO : Read image orientation and apply IJK to RAS transform (i.e. different flipping for each orientation) 
            # import SimpleITK as sitk
            # reader = sitk.ImageFileReader()
            # reader.SetFileName(fileName)
            # reader.Execute()
            # dd = reader.GetDirection()

            # Load dimensions using `GetDataExtent`
            _extent = reader.GetDataExtent()
            self.dims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]

            self.spacing = reader.GetOutput().GetSpacing()

            # # Load spacing values
            # ConstPixelSpacing = reader.GetPixelSpacing()
            # ConstScalarRange = reader.GetOutput().GetScalarRange()

            # Flip and Translate the image to the right place
            flipYFilter = vtk.vtkImageFlip()
            flipYFilter.SetFilteredAxis(1); # flip y axis
            flipYFilter.SetInputConnection(reader.GetOutputPort())
            flipYFilter.Update()

            flipZFilter = vtk.vtkImageFlip()
            flipZFilter.SetFilteredAxis(2); # flip z axis
            flipZFilter.SetInputConnection(flipYFilter.GetOutputPort())
            flipZFilter.Update()

            try:
                self.origin = reader.GetImagePositionPatient()
                imageInfo = vtk.vtkImageChangeInformation()
                imageInfo.SetOutputOrigin(self.origin)
                imageInfo.SetInputConnection(flipZFilter.GetOutputPort())
            except:
                QMessageBox.warning(self, 'Wrong Header', 'Can not read image Origin from header!\nImage position might be wrong')

            self.imgReader = imageInfo
            self.showImages(self.imgReader, self.dims)
            self.updateSubPanels(self.dims)
            QApplication.restoreOverrideCursor()

    def showImages(self, reader, dims):
        self.vtk_widget_3D.RemoveImage()
        self.vtk_widget_3D_2.RemoveImage()
        self.vtk_widget_2D.RemoveImage()

        self.vtk_widget_3D.showImage(reader)
        self.vtk_widget_3D_2.showImage(reader)
        self.vtk_widget_2D.showImage(reader, dims)
        
        self.ui.btn_LoadPoints.setEnabled(True)
        self.ui.groupBox_Viewports.setEnabled(True)
        
    def updateSubPanels(self, dims):
        self.showSubPanels()
        # image = reader.GetOutput()
        # dims = image.GetDimensions()
        if self.ui.comboBox_2DView.currentText() == 'Axial':
            self.ui.Slider_2D.setRange(0, dims[2]-1)
            self.ui.Slider_2D.setValue(dims[2]//2)
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            self.ui.Slider_2D.setRange(0, dims[1]-1)
            self.ui.Slider_2D.setValue(dims[1]//2)
        else: # if self.ui.comboBox_2DView.currentText() == 'Sagittal':
            self.ui.Slider_2D.setRange(0, dims[0]-1)
            self.ui.Slider_2D.setValue(dims[0]//2)

    def sliderChanged(self):
        self.vtk_widget_2D.setSlice(self.ui.Slider_2D.value())
        self.vtk_widget_2D.interactor.Initialize()
        return
    
    def hideSubPanels(self):
        self.ui.SubPanel_3D.hide()
        self.ui.SubPanel_3D_2.hide()
        self.ui.SubPanel_2D.hide()
        self.ui.SubPanel_endoscope.hide()

    def showSubPanels(self):
        self.ui.SubPanel_3D.show()
        self.ui.SubPanel_3D_2.show()
        self.ui.SubPanel_2D.show()
        self.ui.SubPanel_endoscope.show()

    def applyRegistration(self, toolMat, refMat, regMat):
        # TODO: Calculate tool coords in ref space and apply registration matrix
        # tool2ref = inv(inv(refMat) * toolMat)
        # registeredTool = inv(regMat) * tool2ref
        pass

    def readPoints(self):
        self.registeredPoints = None
        self.RemovePoints()
        from vtk.util.numpy_support import vtk_to_numpy
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Read Points from File", "", "All Data Types (*.mat *.npy *.npz);;Matlab (*.mat);;Numpy (*.npy *.npz);;All Files (*)", options=options)

        if fileName:
            extension = os.path.splitext(fileName)[1].lower()

            if 'mat' in extension:
                matFile = loadmat(fileName)
                # self.registeredPoints = matFile['EMT_cor']
                self.registeredPoints = matFile[list(matFile)[-1]]
            elif 'np' in extension:
                self.toolCoords = np.load(fileName)
                self.registeredPoints = np.zeros_like(self.toolCoords)
                self.registeredPoints = np.swapaxes(self.registeredPoints, 0, 2)
                # self.toolCoords = np.swapaxes(self.toolCoords, 0, 2)
                # self.toolCoords = np.swapaxes(self.toolCoords, 0, 1)

                # self.toolCoords = np.swapaxes(self.toolCoords, 1, 2)


                # self.regMat = np.array([[0.3, 0.86, 0.41, 9.09],
                #                         [0.03, 0.42, -0.91, -1.49],
                #                         [-0.95, 0.28, 0.098, -27.97],
                #                         [0, 0, 0, 1]])

                
                regMat_inv = np.linalg.inv(self.regMat)
                ii = 0
                pt_tracker = np.zeros([len(self.toolCoords), 3], dtype='float')
                for ref, tool in zip(self.refCoords, self.toolCoords):
                    ref_inv = np.linalg.inv(ref)
                    tool2ref = np.dot(ref_inv, tool)
                    pt_tracker[ii, :] = tool2ref[:,3][:-1]
                    reg = np.dot(regMat_inv, tool2ref)
                    self.registeredPoints[:,:,ii] = reg
                    ii += 1

                # self.vtk_widget_3D.register(pt_tracker)
            numPoints = self.registeredPoints.shape[-1]

            # Flip/Rotate points to match the orientation of the image
            for i in range(numPoints):
                pt = self.registeredPoints[:,:,i]
                pt_vtk = vtk.vtkMatrix4x4()
                pt_vtk.DeepCopy(pt.ravel()) 
                flipTrans = vtk.vtkTransform()
                flipTrans.Scale(-1,-1,1)
                pt_new = vtk.vtkMatrix4x4()
                vtk.vtkMatrix4x4.Multiply4x4(flipTrans.GetMatrix(), pt_vtk, pt_new)

                pt_t = np.zeros((4,4))
                pt_new.DeepCopy(pt_t.ravel(), pt_new)
                self.registeredPoints[:,:,i] = pt_t

            self.ui.slider_Frames.setRange(0, numPoints-1)
            self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registeredPoints.shape[-1]))
            if self.ui.checkBox_showPoints.isChecked():
                self.DrawPoints(self.registeredPoints)
            self.ui.btn_playCam.setEnabled(True)
            self.ui.slider_Frames.setEnabled(True)
            self.ui.checkBox_showPoints.setEnabled(True)
            self.ui.btn_ResetVB.setEnabled(True)

    def showHidePoints(self):
        if self.ui.checkBox_showPoints.isChecked():
            self.DrawPoints(self.registeredPoints)
        else:
            self.RemovePoints()

    def DrawPoints(self, points):
        self.vtk_widget_3D.DrawPoints(points)
        self.vtk_widget_3D.AddStartPoint(points[:,:,0]) # start point
        self.vtk_widget_3D.AddEndPoint(points[:,:,-1]) # end point
        # self.playCam(points)

    def RemovePoints(self):
        self.vtk_widget_3D.RemovePoints()
        
    def frameChanged(self):
        if self.registeredPoints is None:
            self.ui.slider_Frames.setValue(0)
            # QMessageBox.critical(self, 'No Points Found', 'Please load the registered points first !')
            return

        pNum = self.ui.slider_Frames.value()
        self.cam_pos = self.registeredPoints[:,:,pNum]

        # cam_pos_t = vtk.vtkMatrix4x4()
        # cam_pos_t.DeepCopy(cam_pos.ravel()) 
        # flipTrans = vtk.vtkTransform()
        # flipTrans.Scale(-1,-1,1)
        # newMat = vtk.vtkMatrix4x4()
        # vtk.vtkMatrix4x4.Multiply4x4(flipTrans.GetMatrix(), cam_pos_t, newMat)
        # self.vtk_widget_3D.setCamera(newMat)

        self.showToolOnViews(self.cam_pos)

        self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registeredPoints.shape[-1]))

    def showToolOnViews(self, toolMatrix):
        self.vtk_widget_3D.setCamera(toolMatrix)

        if self.ui.comboBox_2DView.currentText() == 'Axial':
            axial_slice = int((toolMatrix[2,3] - self.origin[2]) / self.spacing[2])
            self.vtk_widget_2D.setSlice(axial_slice)
            self.ui.Slider_2D.setValue(axial_slice)
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            coronal_slice = int((toolMatrix[1,3] - self.origin[1]) / self.spacing[1])
            self.vtk_widget_2D.setSlice(coronal_slice)
            self.ui.Slider_2D.setValue(coronal_slice)
        else: # self.ui.comboBox_2DView.currentText() == 'Sagittal'
            sagittal_slice = int((toolMatrix[0,3] - self.origin[0]) / self.spacing[0])
            self.vtk_widget_2D.setSlice(sagittal_slice)
            self.ui.Slider_2D.setValue(sagittal_slice)

        self.vtk_widget_3D_2.SetCrossPosition(toolMatrix[0,3], toolMatrix[1,3], toolMatrix[2,3])
        if self.ui.comboBox_2DView.currentText() == 'Axial':
            self.vtk_widget_2D.SetCrossPosition(toolMatrix[0,3], toolMatrix[1,3])
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            self.vtk_widget_2D.SetCrossPosition(toolMatrix[0,3], toolMatrix[2,3]+self.origin[1])
        else: # if self.ui.comboBox_2DView.currentText() == 'Sagittal':
            self.vtk_widget_2D.SetCrossPosition(toolMatrix[1,3], toolMatrix[2,3]+self.origin[0])

    def playCam(self, points):
        # cam_pos = np.array([[0.6793, -0.7232, -0.1243, 33.3415], [-0.0460, -0.2110, 0.9764, -29.0541], [-0.7324, -0.6576, -0.1767, 152.6576], [0, 0, 0, 1.0000]])
        if self.registeredPoints is None:
            QMessageBox.critical(self, 'No Points Found', 'Please load the registered points first !')
            return
        self.ui.btn_pauseCam.setEnabled(True)
        self.ui.btn_stopCam.setEnabled(True)
        self.paused = False
        for i in range(self.ui.slider_Frames.value(),self.registeredPoints.shape[-1]):
            if self.paused:
                break

            self.cam_pos = self.registeredPoints[:,:,i]

            # cam_pos_t = vtk.vtkMatrix4x4()
            # cam_pos_t.DeepCopy(self.cam_pos.ravel()) 
            # flipTrans = vtk.vtkTransform()
            # flipTrans.Scale(-1,-1,1)
            # newMat = vtk.vtkMatrix4x4()
            # vtk.vtkMatrix4x4.Multiply4x4(flipTrans.GetMatrix(), cam_pos_t, newMat)
            # self.vtk_widget_3D.setCamera(newMat)

            # self.vtk_widget_3D.setCamera(self.cam_pos)

            self.ui.slider_Frames.setValue(i)
            self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registeredPoints.shape[-1]))

            time.sleep(0.1)
            QApplication.processEvents()
    
    def pauseCam(self):
        self.paused = True

    def stopCam(self):
        self.paused = True
        self.ui.slider_Frames.setValue(0)
        self.ui.btn_pauseCam.setEnabled(False)
        self.ui.btn_stopCam.setEnabled(False)
    
    def change2DView(self):
        self.vtk_widget_2D.ResetView()
        # self.vtk_widget_2D.RemoveImage()
        self.vtk_widget_2D.planeType = self.ui.comboBox_2DView.currentText()
        self.vtk_widget_2D.showImage(self.imgReader, self.dims)
        self.updateSubPanels(self.dims)

        if not self.vtk_widget_2D.cross == None:
            self.vtk_widget_2D.RemoveCross()
            if self.trackerReady:
                self.showToolOnViews(self.toolData)
            else:
                self.showToolOnViews(self.cam_pos)

    def ResetViewports(self):
        self.vtk_widget_3D.ResetView()
        self.vtk_widget_3D_2.ResetView()
        self.vtk_widget_2D.ResetView()
        self.updateSubPanels(self.dims)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Read Points from File", "", "All Data Types (*.mat *.npy *.npz);;Matlab (*.mat);;Numpy (*.npy *.npz);;All Files (*)", options=options)

        if fileName:
            extension = os.path.splitext(fileName)[1].lower()

            if 'mat' in extension:
                matFile = loadmat(fileName)
                # self.registeredPoints = matFile['EMT_cor']
                self.refCoords = matFile[list(matFile)[-1]]
            elif 'np' in extension:
                self.refCoords = np.load(fileName)
                # self.refCoords = np.swapaxes(self.refCoords, 1, 2)


    def ResetVB(self):
        self.RemovePoints()
        self.registeredPoints = None
        self.stopCam()
        self.vtk_widget_2D.RemoveCross()
        self.ui.btn_ResetVB.setEnabled(False)
        self.ui.btn_playCam.setEnabled(False)
        self.ui.btn_pauseCam.setEnabled(False)
        self.ui.btn_stopCam.setEnabled(False)
        self.ui.slider_Frames.setEnabled(False)
        self.ui.checkBox_showPoints.setEnabled(False)
        self.ResetViewports()

    def setup(self, size):
        self.ui = MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        # sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.resize(sizeObject.width(), sizeObject.height())
        # self.resize(size.width(), size.height())
        self.vtk_widget_3D = QVtkViewer3D(self.ui.vtk_panel_3D_1, size, 'Virtual')
        self.vtk_widget_3D_2 =  QVtkViewer3D(self.ui.vtk_panel_3D_2, size, 'Prespective')
        self.vtk_widget_2D = QVtkViewer2D(self.ui.vtk_panel_2D, size, self.ui.comboBox_2DView.currentText())
        self.hideSubPanels()

    def initialize(self):
        pass

if __name__ == "__main__":
    # # ReCompile Ui
    # os.chdir(os.path.dirname(__file__))
    # with open("MainWindow.ui") as ui_file:
    #     with open("MainWindow.py", "w") as py_ui_file:
    #         uic.compileUi(ui_file, py_ui_file, execute=True)

    # Pipe error output to a text file instead of the usual vtk pop-up window
    fileOutputWindow = vtk.vtkFileOutputWindow()
    fileOutputWindow.SetFileName("vtk_log.txt")
    vtk.vtkOutputWindow.SetInstance(fileOutputWindow)

    app = QApplication([])

    '''
    Set Dark Pallete
    '''
    # # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # # Now use a palette to switch to dark colors:
    # palette = QPalette()
    # palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # palette.setColor(QPalette.WindowText, Qt.white)
    # palette.setColor(QPalette.Base, QColor(25, 25, 25))
    # palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # palette.setColor(QPalette.ToolTipBase, Qt.white)
    # palette.setColor(QPalette.ToolTipText, Qt.white)
    # palette.setColor(QPalette.Text, Qt.white)
    # palette.setColor(QPalette.Button, QColor(53, 53, 53))
    # palette.setColor(QPalette.ButtonText, Qt.white)
    # palette.setColor(QPalette.BrightText, Qt.red)
    # palette.setColor(QPalette.Link, QColor(42, 130, 218))
    # palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    # palette.setColor(QPalette.HighlightedText, Qt.black)
    # app.setPalette(palette)

    screen = app.primaryScreen()
    size = screen.availableGeometry()  # size.height(), size.width()
    main_win = myMainWindow(size)
    main_win.showMaximized()
    # main_win.show()
    # main_win.initialize()

    if main_win.tracker_connected == True:
        main_win.disconnectTracker()
    sys.exit(app.exec())
