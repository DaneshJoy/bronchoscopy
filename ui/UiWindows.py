# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 23:06:25 2020

@author: Saeed
"""

import os
import vtk
from PyQt5.Qt import QDialog
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QDateTime
import numpy as np
from vmtk import pypes
from ui import NewPatientWin, ToolsWin, RegMatWin


class NewPatientWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._imageName = None
        self._name = ''
        
        self.setup()
        self.ui.lineEdit_Name.textChanged.connect(self.onNameChanged)
        self.ui.dateEdit.dateChanged.connect(self.onDateChanged)
        # self.ui.btn_LoadDicom.triggered.connect(self.openDirDialog)
        self.ui.btn_LoadImage.clicked.connect(self.openFileDialog)
    
    def onNameChanged(self):
        # TODO: check validity
        self._name = self.ui.lineEdit_Name.text
        
    def onDateChanged(self, qDate):
        self._date = f'{qDate.year()}-{qDate.month()}-{qDate.day()}'
    
    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Medical Image", "", "Medical Images (*.nii *.nii.gz *.mhd *.mha);;Nifti (*.nii *.nii.gz);;Meta (*.mhd *.mha);;All Files (*)", options=options)
        # QMessageBox.information(self, 'Test Message', fileName)
        if fileName:
            myArguments = f'vmtkimagereader -ifile {fileName} --pipe vmtkmarchingcubes -l 0.5 --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25'
            myPype = pypes.PypeRun(myArguments)
            self._imageName = os.path.basename(fileName)
            self.ui.label_ImageName.setText(self._imageName)
            # QApplication.setOverrideCursor(Qt.WaitCursor)
            # extension = os.path.splitext(fileName)[1].lower()
            # try:
            #     if 'vtk' in extension or 'vtp' in extension:
            #         reader = vtk.vtkPolyDataReader()
            #         reader.SetFileName(fileName)
            #         _extent = reader.GetOutput().GetBounds()
            #         self.spacing = (1, 1, 1)
            #         self.origin = (0, 0, 0)
            #         reader.Update()
            #     else:
            #         if 'nii' in extension or 'gz' in extension:
            #             reader = vtk.vtkNIFTIImageReader()
            #             reader.SetFileName(fileName)
            #         elif 'mhd' in extension or 'mha' in extension:
            #             reader = vtk.vtkMetaImageReader()
            #             reader.SetFileName(fileName)
            #         reader.Update()
            #         # Load dimensions using `GetDataExtent`
            #         # xMin, xMax, yMin, yMax, zMin, zMax = reader.GetDataExtent()
            #         _extent = reader.GetDataExtent()
            #         self.spacing = reader.GetOutput().GetSpacing()
            #         self.origin = reader.GetOutput().GetOrigin()
                
            #     self.dims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]   
            # except:
            #     QApplication.restoreOverrideCursor()
            #     QMessageBox.critical(self, 'Unknown File Type', 'Can not load selected image!')
            #     return

            # # TODO : Read image orientation and apply IJK to RAS transform (i.e. different flipping for each orientation) 
            # # import SimpleITK as sitk
            # # reader = sitk.ImageFileReader()
            # # reader.SetFileName(fileName)
            # # reader.Execute()
            # # dd = reader.GetDirection()

            
            # # self.origin = (0, 0, 0)

            # # Flip and Translate the image to the right place
            # # flipXFilter = vtk.vtkImageFlip()
            # # flipXFilter.SetFilteredAxis(0); # flip x axis
            # # flipXFilter.SetInputConnection(reader.GetOutputPort())
            # # flipXFilter.Update()

            # # flipYFilter = vtk.vtkImageFlip()
            # # flipYFilter.SetFilteredAxis(1); # flip y axis
            # # flipYFilter.SetInputConnection(flipXFilter.GetOutputPort())
            # # flipYFilter.Update()

            # if 'nii' in extension or 'gz' in extension:
            #     try:
            #         _QMatrix = reader.GetQFormMatrix()
            #         # self.origin = (0, 0, 0)
            #         self.origin = (-_QMatrix.GetElement(0,3), -_QMatrix.GetElement(1,3), _QMatrix.GetElement(2,3))
            #         imageInfo = vtk.vtkImageChangeInformation()
            #         imageInfo.SetOutputOrigin(self.origin)
            #         imageInfo.SetInputConnection(reader.GetOutputPort())
            #         self.imgReader = imageInfo
            #         self.showImages()
            #     except:
            #         QMessageBox.warning(self, 'Wrong Header', 'Can not read Image Origin from header!\nImage position might be wrong')
            # else:
            #     # origin = (140, 140, -58)
            #     # imageInfo = vtk.vtkImageChangeInformation()
            #     # imageInfo.SetOutputOrigin(self.origin)
            #     # imageInfo.SetInputConnection(reader.GetOutputPort())
            #     # self.showImages(imageInfo, self.dims)
            #     self.imgReader = reader
            #     self.showImages()

            # self.updateSubPanels(self.dims)
            # QApplication.restoreOverrideCursor()

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
            self.showImages()
            self.updateSubPanels(self.dims)
            QApplication.restoreOverrideCursor()


    def setData(self, p_name):
        self._name = p_name
        self._imageName = None
        self.ui.label_ImageName.setText('None')
        self.ui.lineEdit_Name.setText(self._name)
        self.ui.dateEdit.setDateTime(QDateTime.currentDateTime())

    def getData(self):
        return self._name, self._date, self._imageName

    def setup(self):
        self.ui = NewPatientWin.Ui_NewPatientWin()
        self.ui.setupUi(self)
        

class RegMatWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
    
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
        self.ui = RegMatWin.Ui_RegMatWin()
        self.ui.setupUi(self)


class ToolsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.ui = ToolsWin.Ui_ToolsWin()
        self.ui.setupUi(self)
