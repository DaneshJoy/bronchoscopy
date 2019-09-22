# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 01:09:45 2019

@author: Saeed
"""

import os
import sys
import vtk
import numpy as np
import SimpleITK as sitk
from PyQt5.Qt import QApplication, QMainWindow, QColor, Qt
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtGui import QPalette

from ui.QVtkViewer import QVtkViewer3D, QVtkViewer2D

import MainWindow

class MainWindow(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.vtk_widget_3D = None
        self.vtk_widget_axial = None
        self.vtk_widget_coronal = None
        self.vtk_widget_sagittal = None
        self.ui = None
        self.setup(size)

        self.ui.actionLoad_Image.triggered.connect(self.openFileDialog)
        self.ui.actionLoad_DICOM.triggered.connect(self.openDirDialog)
        self.ui.Slider_axial.valueChanged.connect(self.axialChanged)
        self.ui.Slider_coronal.valueChanged.connect(self.coronalChanged)
        self.ui.Slider_sagittal.valueChanged.connect(self.sagittalChanged)

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, filetype = QFileDialog.getOpenFileName(self, "Open Medical Image", "", "Meta (*.mhd *.mha);;Nifti (*.nii *.nii.gz);;All Files (*)", options=options)
        # QMessageBox.information(self, 'Test Message', fileName)
        if fileName:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            if 'Meta' in filetype:
                reader = vtk.vtkMetaImageReader()
                reader.SetFileName(fileName)
            elif 'Nifti' in filetype:
                reader = vtk.vtkNIFTIImageReader()
                reader.SetFileName(fileName)
            else:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, 'Unknown File Type', 'Can not load selected image!')
                return
            reader.Update()

            # Flip the image
            flipYFilter = vtk.vtkImageFlip()
            flipYFilter.SetFilteredAxis(1) # flip y axis
            flipYFilter.SetInputConnection(reader.GetOutputPort())
            flipYFilter.Update()

            # flipZFilter = vtk.vtkImageFlip()
            # flipZFilter.SetFilteredAxis(0); # flip z axis
            # flipZFilter.SetInputConnection(flipYFilter.GetOutputPort());
            # flipZFilter.Update();

            # Create the Viewer
            # vtkSmartPointer<vtkResliceImageViewer> viewer =
            # vtkSmartPointer<vtkResliceImageViewer>::New();
            # viewer->SetInputData(flipYFilter->GetOutput())

            self.showImages(flipYFilter)
            self.updateSubPanels(flipYFilter)
            QApplication.restoreOverrideCursor()

            # # Real to VTK Camera
            # cam_pos = np.array([[0.6793, -0.7232, -0.1243, 33.3415], [-0.0460, -0.2110, 0.9764, -29.0541], [-0.7324, -0.6576, -0.1767, 152.6576], [0, 0, 0, 1.0000]])
            # self.vtk_widget_3D.setCamera(cam_pos)

    def openDirDialog(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select a Directory", "" )

        if dirname:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            reader = vtk.vtkDICOMImageReader()
            reader.SetDirectoryName(dirname)

            reader1 = sitk.ImageSeriesReader()
            dicom_names = reader1.GetGDCMSeriesFileNames(dirname)
            fileNames = vtk.vtkStringArray()
            # files = os.listdir(dirname)
            for f in dicom_names:
                fileNames.InsertNextValue(f)
            reader.SetFileNames(fileNames)
            # reader.SetMemoryRowOrderToFileNative()
            reader.Update()

            self.showImages(reader)
            self.updateSubPanels(reader)
            QApplication.restoreOverrideCursor()

            # Real to VTK Camera
            cam_pos = np.array([[0.6793, -0.7232, -0.1243, 33.3415], [-0.0460, -0.2110, 0.9764, -29.0541], [-0.7324, -0.6576, -0.1767, 152.6576], [0, 0, 0, 1.0000]])
            self.vtk_widget_3D.setCamera(cam_pos)

    def showImages(self, reader):
        self.vtk_widget_3D.removeImage()
        self.vtk_widget_axial.removeImage()
        self.vtk_widget_coronal.removeImage()
        self.vtk_widget_sagittal.removeImage()

        self.vtk_widget_3D.showImage(reader)
        self.vtk_widget_axial.showImage(reader)
        self.vtk_widget_coronal.showImage(reader)
        self.vtk_widget_sagittal.showImage(reader)

    def updateSubPanels(self, reader):
        self.showSubPanels()
        image = reader.GetOutput()
        dims = image.GetDimensions()
        self.ui.Slider_axial.setRange(0, dims[2]-1)
        self.ui.Slider_coronal.setRange(0, dims[1]-1)
        self.ui.Slider_sagittal.setRange(0, dims[0]-1)
        self.ui.Slider_axial.setValue(dims[2]//2)
        self.ui.Slider_coronal.setValue(dims[1]//2)
        self.ui.Slider_sagittal.setValue(dims[0]//2)

    def axialChanged(self):
        self.vtk_widget_axial.setSlice(self.ui.Slider_axial.value())
        self.vtk_widget_axial.interactor.Initialize()
        return False

    def coronalChanged(self):
        self.vtk_widget_coronal.setSlice(self.ui.Slider_coronal.value())
        self.vtk_widget_coronal.interactor.Initialize()
        return False

    def sagittalChanged(self):
        self.vtk_widget_sagittal.setSlice(self.ui.Slider_sagittal.value())
        self.vtk_widget_sagittal.interactor.Initialize()
        return False
    
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

    def setup(self, size):
        import MainWindow
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
    main_win = MainWindow(size)
    main_win.showMaximized()
    # main_win.show()
    # main_win.initialize()
    sys.exit(app.exec())
