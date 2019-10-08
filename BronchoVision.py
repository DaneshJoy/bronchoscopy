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
from PyQt5.Qt import QApplication, QMainWindow, QColor, Qt
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtGui import QPalette

from ui.QVtkViewer import QVtkViewer3D, QVtkViewer2D

from ui import MainWindow

class myMainWindow(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.vtk_widget_3D = None
        self.vtk_widget_axial = None
        self.vtk_widget_coronal = None
        self.vtk_widget_sagittal = None
        self.ui = None
        self.registeredPoints = None
        self.setup(size)
        self.paused = False

        self.ui.actionLoad_Image.triggered.connect(self.openFileDialog)
        self.ui.actionLoad_DICOM.triggered.connect(self.openDirDialog)
        self.ui.Slider_axial.valueChanged.connect(self.axialChanged)
        self.ui.Slider_coronal.valueChanged.connect(self.coronalChanged)
        self.ui.Slider_sagittal.valueChanged.connect(self.sagittalChanged)

        self.ui.btn_LoadPoints.clicked.connect(self.readRegisteredPoints)
        self.ui.checkBox_showPoints.stateChanged.connect(self.showHidePoints)
        self.ui.btn_playCam.clicked.connect(self.playCam)
        self.ui.btn_pauseCam.clicked.connect(self.pauseCam)
        self.ui.btn_stopCam.clicked.connect(self.stopCam)
        self.ui.slider_Frames.valueChanged.connect(self.frameChanged)

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, filetype = QFileDialog.getOpenFileName(self, "Open Medical Image", "", "Medical Images (*.nii *.nii.gz *.mhd *.mha);;Nifti (*.nii *.nii.gz);;Meta (*.mhd *.mha);;All Files (*)", options=options)
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

            # Load dimensions using `GetDataExtent`
            _extent = reader.GetDataExtent()
            self.dims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]

            # Flip and Translate the image to the right place
            flipXFilter = vtk.vtkImageFlip()
            flipXFilter.SetFilteredAxis(0); # flip x axis
            flipXFilter.SetInputConnection(reader.GetOutputPort())
            flipXFilter.Update()

            flipYFilter = vtk.vtkImageFlip()
            flipYFilter.SetFilteredAxis(1); # flip y axis
            flipYFilter.SetInputConnection(flipXFilter.GetOutputPort())
            flipYFilter.Update()

            if 'nii' in extension or 'gz' in extension:
                try:
                    _QMatrix = reader.GetQFormMatrix()
                    origin = (-_QMatrix.GetElement(0,3), -_QMatrix.GetElement(1,3), _QMatrix.GetElement(2,3))
                    imageInfo = vtk.vtkImageChangeInformation()
                    imageInfo.SetOutputOrigin(origin)
                    imageInfo.SetInputConnection(flipYFilter.GetOutputPort())
                    self.showImages(imageInfo, self.dims)
                except:
                    QMessageBox.warning(self, 'Wrong Header', 'Can not read Image Origin from header!\nImage position might be wrong')
            else:
                origin = (140, 140, -58)
                imageInfo = vtk.vtkImageChangeInformation()
                imageInfo.SetOutputOrigin(origin)
                imageInfo.SetInputConnection(flipYFilter.GetOutputPort())
                self.showImages(imageInfo, self.dims)

                # self.showImages(flipYFilter, self.dims)
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

            # Load dimensions using `GetDataExtent`
            _extent = reader.GetDataExtent()
            self.dims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]

            # # Load spacing values
            # ConstPixelSpacing = reader.GetPixelSpacing()
            # ConstScalarRange = reader.GetOutput().GetScalarRange()

            # Flip and Translate the image to the right place
            flipXFilter = vtk.vtkImageFlip()
            flipXFilter.SetFilteredAxis(0); # flip x axis
            flipXFilter.SetInputConnection(reader.GetOutputPort())
            flipXFilter.Update()

            flipZFilter = vtk.vtkImageFlip()
            flipZFilter.SetFilteredAxis(2); # flip z axis
            flipZFilter.SetInputConnection(flipXFilter.GetOutputPort())
            flipZFilter.Update()

            try:
                origin = reader.GetImagePositionPatient()
                imageInfo = vtk.vtkImageChangeInformation()
                imageInfo.SetOutputOrigin(origin)
                imageInfo.SetInputConnection(flipZFilter.GetOutputPort())
            except:
                QMessageBox.warning(self, 'Wrong Header', 'Can not read image Origin from header!\nImage position might be wrong')

            self.showImages(imageInfo, self.dims)
            self.updateSubPanels(self.dims)
            QApplication.restoreOverrideCursor()

    def showImages(self, reader, dims):
        self.vtk_widget_3D.removeImage()
        self.vtk_widget_axial.removeImage()
        self.vtk_widget_coronal.removeImage()
        self.vtk_widget_sagittal.removeImage()

        self.vtk_widget_3D.showImage(reader)
        self.vtk_widget_axial.showImage(reader, dims)
        self.vtk_widget_coronal.showImage(reader, dims)
        self.vtk_widget_sagittal.showImage(reader, dims)

        self.ui.btn_LoadPoints.setEnabled(True)
        
    def updateSubPanels(self, dims):
        self.showSubPanels()
        # image = reader.GetOutput()
        # dims = image.GetDimensions()
        self.ui.Slider_axial.setRange(0, dims[2]-1)
        self.ui.Slider_coronal.setRange(0, dims[1]-1)
        self.ui.Slider_sagittal.setRange(0, dims[0]-1)
        self.ui.Slider_axial.setValue(dims[2]//2)
        self.ui.Slider_coronal.setValue(dims[1]//2)
        self.ui.Slider_sagittal.setValue(dims[0]//2)

    def axialChanged(self):
        self.vtk_widget_axial.setSlice(self.ui.Slider_axial.value(), self.dims)
        self.vtk_widget_axial.interactor.Initialize()
        return

    def coronalChanged(self):
        self.vtk_widget_coronal.setSlice(self.ui.Slider_coronal.value(), self.dims)
        self.vtk_widget_coronal.interactor.Initialize()
        return

    def sagittalChanged(self):
        self.vtk_widget_sagittal.setSlice(self.ui.Slider_sagittal.value(), self.dims)
        self.vtk_widget_sagittal.interactor.Initialize()
        return
    
    def hideSubPanels(self):
        self.ui.SubPanel_3D.hide()
        self.ui.SubPanel_axial.hide()
        self.ui.SubPanel_coronal.hide()
        self.ui.SubPanel_sagittal.hide()

    def showSubPanels(self):
        self.ui.SubPanel_3D.show()
        self.ui.SubPanel_axial.show()
        self.ui.SubPanel_coronal.show()
        self.ui.SubPanel_sagittal.show()

    def readRegisteredPoints(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Matlab file", "", "Matlab (*.mat);;All Files (*)", options=options)
        if fileName:
            matFile = loadmat(fileName)
            # self.registeredPoints = matFile[list(matFile.keys())[-1]]
            self.registeredPoints = matFile['EMT_cor']
            self.ui.slider_Frames.setRange(0, self.registeredPoints.shape[-1]-1)
            self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registeredPoints.shape[-1]))
            self.drawTrajectory(self.registeredPoints)
            self.ui.btn_playCam.setEnabled(True)
            self.ui.slider_Frames.setEnabled(True)
            self.ui.checkBox_showPoints.setEnabled(True)

    def showHidePoints(self):
        if self.ui.checkBox_showPoints.isChecked():
            self.drawTrajectory(self.registeredPoints)
        else:
            self.removeTrajectory()

    def drawTrajectory(self, points):
        self.vtk_widget_3D.drawPoints(points)
        self.vtk_widget_3D.addStartPoint(points[:,:,0]) # start point
        self.vtk_widget_3D.addEndPoint(points[:,:,-1]) # end point
        # self.playCam(points)

    def removeTrajectory(self):
        self.vtk_widget_3D.removePoints()
        
    def frameChanged(self):
        if self.registeredPoints is None:
            self.ui.slider_Frames.setValue(0)
            # QMessageBox.critical(self, 'No Points Found', 'Please load the registered points first !')
            return
        pNum = self.ui.slider_Frames.value()
        testPoint = self.registeredPoints[:,:,pNum]
        self.vtk_widget_3D.setCamera(testPoint)
        self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registeredPoints.shape[-1]))

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
            testPoint = self.registeredPoints[:,:,i]
            self.vtk_widget_3D.setCamera(testPoint)
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

    def setup(self, size):
        self.ui = MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        # sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.resize(sizeObject.width(), sizeObject.height())
        # self.resize(size.width(), size.height())
        self.vtk_widget_3D = QVtkViewer3D(self.ui.vtk_panel_3D, size)
        self.vtk_widget_axial = QVtkViewer2D(self.ui.vtk_panel_axial, size, 'axial')
        self.vtk_widget_coronal = QVtkViewer2D(self.ui.vtk_panel_coronal, size, 'coronal')
        self.vtk_widget_sagittal = QVtkViewer2D(self.ui.vtk_panel_sagittal, size, 'sagittal')
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
    sys.exit(app.exec())
