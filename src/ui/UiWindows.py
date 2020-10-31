# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 23:06:25 2020

@author: Saeed
"""

import os
import vtk
import threading
from PyQt5.Qt import QDialog
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QFileDialog, QMessageBox, QDialogButtonBox
from PyQt5.QtCore import Qt, QDateTime
import numpy as np
from vmtk import pypes, vmtkscripts
from ui import NewPatientWin, ToolsWin, RegMatWin


class NewPatientWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patients_dir = '..\\Patients'
        self.setup()
        self.ui.btn_ViewImage.hide()
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.lineEdit_Name.textChanged.connect(self.onNameChanged)
        self.ui.dateEdit.dateChanged.connect(self.onDateChanged)
        self.ui.btn_LoadImage.clicked.connect(self.openFileDialog)
        self.ui.btn_ViewImage.clicked.connect(self.viewImage)
        self.ui.buttonBox.accepted.connect(self.acceptPatient)
    
    def onNameChanged(self):
        # TODO: check validity
        self._name = self.ui.lineEdit_Name.text()
        
    def onDateChanged(self, qDate):
        self._date = f'{qDate.year()}-{qDate.month()}-{qDate.day()}'
    
    def openFileDialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Open Medical Image", "", "Medical Images (*.nii *.nii.gz *.mhd *.mha *.dcm *.);;Nifti (*.nii *.nii.gz);;Meta (*.mhd *.mha);;Dicom (*.dcm *.);;All Files (*)", options=options)
        # QMessageBox.information(self, 'Test Message', fileName)
        if self.fileName:
            self._imageName = os.path.basename(self.fileName)
            _tmp = extension = os.path.splitext(self._imageName)
            if (len(_tmp) > 1):
                extension = os.path.splitext(self._imageName)[1].lower()
                if 'dcm' in extension or extension == '' :
                     self._imageName = os.path.basename(os.path.dirname(self.fileName))
                elif 'gz' in extension:
                    self._imageName = self._imageName[:-7]
                else:
                    self._imageName = self._imageName[:-4]
            self.ui.label_ImageName.setText(self._imageName)
            self.ui.btn_ViewImage.show()
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def visualizeImage(self):
        myArguments = f'vmtkimagereader -ifile \"{self.fileName}\" --pipe vmtkmarchingcubes -l 0.5 --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25'
        myPype = pypes.PypeRun(myArguments)
        self.XyzToRas = myPype.GetScriptObject('vmtkimagereader','0').XyzToRasMatrixCoefficients
        self.XyzToRas = np.array([[self.XyzToRas[0:4]],
                                [self.XyzToRas[4:8]],
                                [self.XyzToRas[8:12]],
                                [self.XyzToRas[12:16]]])
        self.ImageData = myPype.GetScriptObject('vmtkimagereader','0').Image
        QApplication.restoreOverrideCursor()

    def viewImage(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        thread_vis = threading.Thread(target=self.visualizeImage())
        thread_vis.start()

    def prepare(self, p_name):
        self._name = p_name
        self._imageName = None
        self.fileName = ''
        self.ImageData = None
        self.ui.label_ImageName.setText('None')
        self.ui.lineEdit_Name.setText(self._name)
        self.ui.dateEdit.setDateTime(QDateTime.currentDateTime())
        self.ui.btn_ViewImage.hide()

    def getData(self):
        return self._name, self._date, self._imageName

    def writeImage(self):
        if self.ImageData == None:
            myArguments = f'vmtkimagereader -ifile \"{self.fileName}\"'
            myPype = pypes.PypeRun(myArguments)
            self.XyzToRas = myPype.GetScriptObject('vmtkimagereader','0').XyzToRasMatrixCoefficients
            self.XyzToRas = np.array([[self.XyzToRas[0:4]],
                                    [self.XyzToRas[4:8]],
                                    [self.XyzToRas[8:12]],
                                    [self.XyzToRas[12:16]]])
            self.ImageData = myPype.GetScriptObject('vmtkimagereader','0').Image
        patient_dir = os.path.join(self.patients_dir , self._name)
        if (not os.path.exists(patient_dir)):
            os.mkdir(patient_dir)
        myWriter = vmtkscripts.vmtkImageWriter()
        myWriter.Image = self.ImageData
        myWriter.OutputFileName = os.path.join(self.patients_dir , self._name, self._imageName + '.nii.gz')
        myWriter.RasToIjkMatrixCoefficients = myPype.GetScriptObject('vmtkimagereader','0').RasToIjkMatrixCoefficients
        myWriter.ApplyTransform = 1
        myWriter.Execute()

        XyzToRas_file = os.path.join(self.patients_dir , self._name, 'XyzToRasMatrix.npy')
        np.save(XyzToRas_file, self.XyzToRas)
        
        QApplication.restoreOverrideCursor()

    def acceptPatient(self):
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            thread_write = threading.Thread(target=self.writeImage())
            thread_write.start()
        except:
            print('ERROR: Can not create patient')

    def setup(self):
        self.ui = NewPatientWin.Ui_NewPatientWin()
        self.ui.setupUi(self)
        

class RegMatWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup()
    
    def setData(self, regMat):
        for i in range(4):
            for j in range(4):
                newitem = QTableWidgetItem(str(regMat[i, j].round(3)))
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
        self.setup()

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
