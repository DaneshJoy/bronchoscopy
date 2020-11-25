# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 23:06:25 2020

@author: Saeed
"""

import os
import vtk
import threading
from functools import partial
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialog
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QFileDialog, QMessageBox, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import Qt, QDateTime
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
import numpy as np
from vmtk import pypes, vmtkscripts
from pycpd import RigidRegistration
from ui import NewPatientWin, ToolsWin, RegMatWin, RegWin


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
        for i in range(3):
            for j in range(4):
                newitem = QTableWidgetItem(str(regMat[i, j].round(3)))
                self.ui.table_regMat.setItem(i, j, newitem)

    def getData(self):
        regMat_new = np.zeros([3, 4], dtype='float')
        for i in range(3):
            for j in range(4):
                regMat_new[i, j] = float(self.ui.table_regMat.takeItem(i, j).text())
        return regMat_new

    def setup(self):
        self.ui = RegMatWin.Ui_RegMatWin()
        self.ui.setupUi(self)

from pylab import *
class RegWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup()
        self.steps = 0
        self.reg_mat = []
        self.is_canceled = False

    def setData(self, image_coords, tracker_coords):
        self.target_coords = image_coords
        self.source_coords = tracker_coords
        self.axes1 = self.fig.add_subplot(121, projection='3d')
        self.X = self.coord2points(self.target_coords)
        self.Y = self.coord2points(self.source_coords)

        self.vis_one(self.X, title='Image Points', color='red', marker='+', ax=self.axes1)
        self.axes2 = self.fig.add_subplot(122, projection='3d')
        self.vis_one(self.Y, title='Tracker Points', color='blue', marker='.', ax=self.axes2)

        # draw borders around subplots
        self.rect1 = plt.Rectangle(
            # (lower-left corner), width, height
            (0.02, 0.02), 0.48, 0.97, fill=False, color="k", lw=1, 
            zorder=1000, transform=self.fig.transFigure, figure=self.fig
        )
        self.rect2 = plt.Rectangle(
            # (lower-left corner), width, height
            (0.51, 0.02), 0.47, 0.97, fill=False, color="k", lw=1, 
            zorder=1000, transform=self.fig.transFigure, figure=self.fig
        )
        self.fig.patches.extend([self.rect1, self.rect2])
        self.fig.tight_layout() 

    def coord2points(self, coords):
        numPoints = coords.shape[-1]
        # numPoints = len(coords)
        points = np.zeros([numPoints, 3])
        for i in range(numPoints):
            points[i,:] = coords[:,:,i][:,3][:-1]
        return points

    def prepare_main_frame(self):
        # Create the mpl Figure and FigCanvas objects. 
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.ui.frame_main)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.ui.frame_main)

        vbox = QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        self.ui.frame_main.setLayout(vbox)

        # self.axes = self.fig.add_subplot(111, projection='3d')
        
    def start(self): 
        self.fig.delaxes(self.axes1)
        self.fig.delaxes(self.axes2)
        self.fig.patches = []
        self.axes = self.fig.add_subplot(111, projection='3d') 
        self.fig.tight_layout()    
        self.ui.btn_start.hide()
        self.ui.buttonBox.show()
        self.ui.progressBar.show()  
        X = self.coord2points(self.target_coords)
        Y = self.coord2points(self.source_coords)
        callback = partial(self.visualize, ax=self.axes)
        reg = RigidRegistration(**{'X': self.X, 'Y': self.Y})
        reg.register(callback)
        
        self.ui.progressBar.setMaximum(self.steps)
        self.ui.progressBar.setValue(self.steps)
        self.ui.progressBar.setTextVisible(True)

        RR = reg.s * reg.R
        tt = reg.t
        self.reg_mat = np.array([[RR[0][0], RR[0][1], RR[0][2], tt[0]],
                                [RR[1][0], RR[1][1], RR[1][2], tt[1]],
                                [RR[2][0], RR[2][1], RR[2][2], tt[2]],
                                [0,         0,      0,          1]])
        # self.R = reg.R
        # self.t = reg.t
        # self.scale = reg.s

        # self.reg_mat = np.array([[RR[0][0], RR[1][0], RR[2][0], tt[0]],
        #                         [RR[0][1], RR[1][1], RR[2][1], tt[1]],
        #                         [RR[0][2], RR[1][2], RR[2][2], tt[2]],
        #                         [0,         0,      0,          1]])


        # # regMat_inv = np.linalg.inv(self.reg_mat)
        # # Y_reg = np.squeeze(np.matmul(regMat_inv, self.Y))
        # Y_reg = reg.s * np.dot(self.Y, reg.R) + reg.t
        # self.vis(self.Y, Y_reg, ax=self.axes)


    def visualize(self, iteration, error, X, Y, ax):
        if self.is_canceled:
            return
        ax.cla()
        # plt.cla()
        ax.scatter(X[:, 0],  X[:, 1], X[:, 2], color='red', marker='+', label='Image Points')
        ax.scatter(Y[:, 0],  Y[:, 1], Y[:, 2], color='blue', marker='.', label='Tracker Points')
        ax.text2D(0.87, 0.92, 'Iteration: {:d}\nErr: {:06.4f}'.format(
            iteration, error), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize='x-large')
        ax.legend(loc='upper left', fontsize='x-large')
        self.canvas.draw()

        # if you remove the progressBar value incrementation, you can't see the realtime plot anymore!
        # acts like plt.pause
        self.ui.progressBar.setMaximum(0)
        self.steps += 1
        self.ui.progressBar.setValue(self.ui.progressBar.value() + 1)
        QApplication.processEvents()
        # plt.pause(0.003)
    
    def vis_one(self, X, title, color, marker, ax):
        ax.cla()
        ax.scatter(X[:, 0], X[:, 1], X[:, 2], color=color, marker=marker)
        ax.set_title(title)
        self.canvas.draw()

    def vis_two(self, X, Y, ax):
        ax.cla()
        ax.scatter(X[:, 0],  X[:, 1], X[:, 2], color='red', marker='+', label='Image Points')
        ax.scatter(Y[:, 0],  Y[:, 1], Y[:, 2], color='blue', marker='.', label='Tracker Points')
        self.canvas.draw()

    def cancel_reg(self):
        self.is_canceled = True
        
    def setup(self):
        self.ui = RegWin.Ui_RegWin()
        self.ui.setupUi(self)
        self.prepare_main_frame()
        self.ui.btn_start.clicked.connect(self.start)
        self.ui.buttonBox.rejected.connect(self.cancel_reg)
        self.ui.progressBar.hide()
        self.ui.buttonBox.hide()


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
