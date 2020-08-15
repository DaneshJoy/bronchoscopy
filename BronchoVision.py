# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 01:09:45 2019

@author: Saeed
"""

import os
import sys
import vtk
import numpy as np
import time
import threading
from scipy.io import loadmat
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog, QLabel, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QPalette, QColor, QIcon
import sqlite3
from sksurgerynditracker.nditracker import NDITracker
# from vmtk import pypes, vmtkscripts, vmtkcenterlines 
from viewers.QVtkViewer2D import QVtkViewer2D
from viewers.QVtkViewer3D import QVtkViewer3D
from ui import MainWin
from ui.UiWindows import RegMatWindow, ToolsWindow, NewPatientWindow
from patients_db import PatientsDB


class MainWindow(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.db = None
        self.db_connection = None
        
        self.tracker = None
        self.tracker_connected = False
        self.isRecordCoords = False
        self.trackerReady = True
        self.captureCoordinates = False

        self.trackerRawCoords_ref = []
        self.trackerRawCoords_tool = []

        self.vtk_widget_3D = None
        self.vtk_widget_3D_2 = None
        self.vtk_widget_2D = None
        self.ui = None
        self.registeredPoints = []
        self.toolCoords = []
        self.refCoords = []
        self.setup(size)
        self.paused = False
        self.size = size
        self.cam_pos = None
        self.XyzToRas = []
        self.lastUpdate = 0
        self.registered_tool = []

        self.toolsWindow = ToolsWindow(self)
        self.regMatWindow = RegMatWindow(self)
        self.newPatientWindow = NewPatientWindow(self)

        self.getPatientsFromDB()
        self.ui.btn_LoadPatient.hide()
        self.ui.btn_DeletePatient.hide()

        self.ui.toolBar.hide()

        self.ui.tabWidget.setCurrentIndex(0)


        # self.regMat = np.array([[0.84,      0.09,   -0.53,  -35.67],
        #                         [-0.51,     -0.14,  -0.85,  -202.98],
        #                         [-0.15,     0.99,   -0.07,  -22.7],
        #                         [0,         0,      0,          1]])

        # self.regMat = np.array([[  9.6680e-02,  -1.0480e-01,  -9.8978e-01,   3.8618e+01], 
        #                         [ -6.0031e-02,   9.9201e-01,  -1.1090e-01,  -4.0377e+01], 
        #                         [  9.9350e-01,   7.0140e-02,   8.9617e-02,   1.3952e+02], 
        #                         [  0,   0,   0,   1]])

        # self.regMat = np.array([[  0.0967,  -0.1048,   -0.9898,   125],
        #                         [ -0.0600,   0.9920,   -0.1109,   58],
        #                         [  0.9935,   0.0701,    0.0896,  -58],
        #                         [  0,   0,   0,   1]])

        # self.regMat = np.array([[  7.35563581e-02,  -1.71236069e-01,   9.82480367e-01,   2.67630473e+02],
        #                         [  1.72677134e-01,   9.72456305e-01,   1.56560985e-01,   3.17539388e+02],
        #                         [ -9.82228115e-01,   1.58135838e-01,   1.01098898e-01,   1.62724952e+02],
        #                         [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])

        # self.regMat = np.array([[  6.46888431e-02,  -3.14844735e-01,  -9.46936189e-01,   4.25743133e+01],
        #                         [ -2.01626482e-02,   9.48317634e-01,  -3.16681437e-01,   9.24174545e+01],
        #                         [  9.97701770e-01,   3.95784970e-02,   5.49974670e-02,   3.43897444e+01],
        #                         [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])

        # self.regMat = np.array([[  6.46888431e-02,  -3.14844735e-01,  -9.46936189e-01,   50],
        #                         [ -2.01626482e-02,   9.48317634e-01,  -3.16681437e-01,   -100],
        #                         [  9.97701770e-01,   3.95784970e-02,   5.49974670e-02,   -50],
        #                         [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])

        self.regMat = np.array([[  2.12947445e-01,  -9.39494389e-01,   2.68335012e-01,   -88],
                                [  2.37930485e-01,   3.16228932e-01,   9.18361774e-01,  -138],
                                [ -9.47651027e-01,  -1.31717714e-01,   2.90874499e-01,   -50],
                                [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])



        self.ui.btn_NewPatient.clicked.connect(self.newPatient)
        self.ui.btn_LoadPatient.clicked.connect(self.loadPatient)
        self.ui.btn_DeletePatient.clicked.connect(self.deletePatient)
        self.ui.btn_ImportPatient.clicked.connect(self.importPatient)
        self.ui.btn_ClearPatients.clicked.connect(self.clearPatients)

        self.ui.Slider_2D.valueChanged.connect(self.sliderChanged)

        self.ui.btn_LoadPoints.clicked.connect(self.readPoints)
        self.ui.btn_LoadRefPoints.clicked.connect(self.readRefPoints)
        self.ui.checkBox_showPoints.stateChanged.connect(self.showHidePoints)
        self.ui.btn_playCam.clicked.connect(self.playCam)
        self.ui.btn_pauseCam.clicked.connect(self.pauseCam)
        self.ui.btn_stopCam.clicked.connect(self.stopCam)
        self.ui.slider_Frames.valueChanged.connect(self.frameChanged)
        self.ui.slider_threshold3D.valueChanged.connect(self.slider3DChanged)
        self.ui.slider_threshold3D_2.valueChanged.connect(self.slider3DChanged_2)
        self.ui.btn_ResetViewports.clicked.connect(self.ResetViewports)
        self.ui.btn_ResetVB.clicked.connect(self.ResetVB)
        self.ui.comboBox_2DView.currentIndexChanged.connect(self.change2DView)

        self.ui.btn_Connect.clicked.connect(self.connectTracker)
        self.ui.btn_ToolsWindow.clicked.connect(self.showToolsWindow)
        self.ui.btn_regMat.clicked.connect(self.showRegMatWindow)
        self.ui.btn_recordToolRef.clicked.connect(self.recordCoords)

        self.ui.tabWidget.currentChanged.connect(self.virtualTabChanged)

    def getPatientsFromDB(self):
        self.ui.tableWidget_Patients.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.db = PatientsDB()
        if (not os.path.exists('Patients')):
            os.mkdir('Patients')
        self.db_connection = self.db.db_createConnection(os.path.join('Patients', 'patients.db'))
        patients = self.db.db_getPatients(self.db_connection)
        print(len(patients))
        for p in patients:
            self.addPatientRow([p[1], p[2]])

    def addPatientRow(self, row_data):
        row = self.ui.tableWidget_Patients.rowCount()
        self.ui.tableWidget_Patients.setRowCount(row+1)
        col = 0
        for item in row_data:
            cell = QTableWidgetItem(str(item))
            self.ui.tableWidget_Patients.setItem(row, col, cell)
            col += 1

    def newPatient(self):
        p_num = self.ui.tableWidget_Patients.rowCount()
        p_name = f'Patient_{p_num+1}'
        self.newPatientWindow.prepare(p_name)
        res = self.newPatientWindow.exec()
        if (res == QDialog.Accepted):
            _name, _date, _image = self.newPatientWindow.getData()
            self.db.db_addPatient(self.db_connection, [_name, _date, _image, 0, 0, 0])
            self.addPatientRow([_name, _date])
            thread_img = threading.Thread(target=self.loadImage(os.path.join('Patients', _name, _image+'.nii.gz')))
            thread_img.start()

    def loadPatient(self):
        # index = self.ui.tableWidget_Patients.selectedIndexes()[0]
        index = self.ui.tableWidget_Patients.selectionModel().selectedRows()[0]
        selected_patient = self.ui.tableWidget_Patients.model().data(index)
        patient_in_db = self.db.db_getPatient(self.db_connection, selected_patient)
        selected_image = patient_in_db[0][3] + '.nii.gz'
        QApplication.setOverrideCursor(Qt.WaitCursor)
        thread_img = threading.Thread(target=self.loadImage(os.path.join('Patients', selected_patient, selected_image)))
        thread_img.start()
        self.ui.tableWidget_Patients.clearSelection()
        self.ui.btn_LoadPatient.hide()
        self.ui.btn_DeletePatient.hide()

    def removePatientDir(self, patient_dir):
        pdir = os.path.join('Patients', patient_dir)
        if os.path.exists(pdir):
            for root, dirs, files in os.walk(pdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(pdir)

    def deletePatient(self):
        index = self.ui.tableWidget_Patients.selectionModel().selectedRows()[0]
        selected_patient = self.ui.tableWidget_Patients.model().data(index)
        ret = QMessageBox.question(self, 'Delete Patient',
                                    f'Do you want to delete {selected_patient} ?\nThis action is NOT reversible',
                                    QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.db.db_deletePatient(self.db_connection, selected_patient)
            self.removePatientDir(selected_patient)
            self.ui.tableWidget_Patients.removeRow(index.row())
        self.ui.btn_LoadPatient.hide()
        self.ui.btn_DeletePatient.hide()
        self.ui.tableWidget_Patients.clearSelection()
        self.removeImagesFromViewports()

    def importPatient(self):
        # TODO: importPatient
        QMessageBox.information(self, 'Comming Soon...', f'Not Implemented Yet !')

    def clearPatients(self):
        ret = QMessageBox.question(self, 'Delete All Patients',
                                    f'Are you sure you want to delete all patients ?!\nThis action is NOT reversible!',
                                    QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.db.db_deleteAllPatients(self.db_connection)
            for d in os.listdir('Patients'):
                if os.path.isdir(os.path.join('Patients', d)):
                    self.removePatientDir(d)
            # Clear table Method1
            self.ui.tableWidget_Patients.setRowCount(0)
            # # Clear table Method2
            # self.ui.tableWidget_Patients.clearContents()
            # self.ui.tableWidget_Patients.model().removeRows(0, self.ui.tableWidget_Patients.rowCount())
            self.ui.btn_LoadPatient.hide()
            self.ui.btn_DeletePatient.hide()
            self.removeImagesFromViewports()

    def showImages(self):
        self.removeImagesFromViewports()

        flipXFilter = vtk.vtkImageFlip()
        flipXFilter.SetFilteredAxis(0); # flip x axis
        flipXFilter.SetInputConnection(self.imgReader.GetOutputPort())
        flipXFilter.Update()

        flipYFilter = vtk.vtkImageFlip()
        flipYFilter.SetFilteredAxis(1); # flip y axis
        flipYFilter.SetInputConnection(flipXFilter.GetOutputPort())
        flipYFilter.Update()

        self.vtk_widget_3D.show_image(flipYFilter)
        self.vtk_widget_3D_2.show_image(flipYFilter)
        self.vtk_widget_2D.show_image(flipYFilter, self.dims, self.spacing, self.origin)
        
        self.ui.btn_LoadPoints.setEnabled(True)
        self.ui.btn_LoadRefPoints.setEnabled(True)
        self.ui.groupBox_Viewports.setEnabled(True)

        self.ui.slider_threshold3D.setEnabled(True)
        self.ui.slider_threshold3D_2.setEnabled(True)
        self.ui.btn_ResetViewports.setEnabled(True)

        self.ui.tabWidget_offline.setEnabled(True)

    def loadImage(self, fileName):
        extension = os.path.splitext(fileName)[1].lower()
        try:
            if 'vtk' in extension or 'vtp' in extension:
                reader = vtk.vtkPolyDataReader()
                reader.SetFileName(fileName)
                _extent = reader.GetOutput().GetBounds()
                self.spacing = (1, 1, 1)
                self.origin = (0, 0, 0)
                reader.Update()
            else:
                if 'nii' in extension or 'gz' in extension:
                    reader = vtk.vtkNIFTIImageReader()
                    reader.SetFileName(fileName)
                elif 'mhd' in extension or 'mha' in extension:
                    reader = vtk.vtkMetaImageReader()
                    reader.SetFileName(fileName)
                reader.Update()
                # Load dimensions using `GetDataExtent`
                # xMin, xMax, yMin, yMax, zMin, zMax = reader.GetDataExtent()
                _extent = reader.GetDataExtent()
                self.spacing = reader.GetOutput().GetSpacing()
                self.origin = reader.GetOutput().GetOrigin()
            
            self.dims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]   
            self.XyzToRas = np.load(os.path.join(os.path.dirname(fileName), 'XyzToRasMatrix.npy'))
        except:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, 'Unknown File Type', 'Can not load selected image!')
            return

        # TODO : Read image orientation and apply IJK to RAS transform (i.e. different flipping for each orientation) 
        # import SimpleITK as sitk
        # reader = sitk.ImageFileReader()
        # reader.SetFileName(fileName)
        # reader.Execute()
        # dd = reader.GetDirection()
        
        # self.origin = (0, 0, 0)

        # Flip and Translate the image to the right place
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
                self.showImages()
            except:
                QMessageBox.warning(self, 'Wrong Header', 'Can not read Image Origin from header!\nImage position might be wrong')
        else:
            # origin = (140, 140, -58)
            # imageInfo = vtk.vtkImageChangeInformation()
            # imageInfo.SetOutputOrigin(self.origin)
            # imageInfo.SetInputConnection(reader.GetOutputPort())
            # self.showImages(imageInfo, self.dims)
            self.imgReader = reader
            self.showImages()

        self.updateSubPanels(self.dims)
        QApplication.restoreOverrideCursor()

    def removeImagesFromViewports(self):
        self.vtk_widget_3D.remove_image()
        self.vtk_widget_3D_2.remove_image()
        self.vtk_widget_2D.remove_image()

    def virtualTabChanged(self):
        if (self.ui.tabWidget.currentIndex() == 0):
            self.trackerReady = True
        else:
            self.trackerReady = False
        # print(self.ui.tabWidget.currentIndex(), self.trackerReady)

    def connectTracker(self):
        if self.tracker_connected == False:
            self.ui.btn_Connect.setText('Connecting...')
            QApplication.setOverrideCursor(Qt.WaitCursor)

            if self.tracker is None:
                # settings_aurora = { "tracker type": "aurora", "ports to use" : [5]}
                settings_aurora = { "tracker type": "aurora"}
                try:
                    self.tracker = NDITracker(settings_aurora)
                    self.captureCoordinates = True
                except:
                    QApplication.restoreOverrideCursor()
                    msg = 'Please check the following:\n' \
                            '  1) NDI device connection\n' \
                            '  2) Is the NDI device switched on?!\n' \
                            '  3) Do you have sufficient privilege to connect to the device?\n' \
                            '     (e.g. on Linux are you part of the \"dialout\" group?)'
                    QMessageBox.critical(self, 'Tracker Connection Failed', f'Can not connect to the tracker!\n{msg}')
                    self.ui.btn_Connect.setText('Connect Tracker')
                    return

            self.tracker.start_tracking()
            tool_desc = self.tracker.get_tool_descriptions()

            self.ui.btn_Connect.setText('Disconnect Tracker')
            self.ui.btn_ToolsWindow.setEnabled(True)
            self.ui.btn_recordToolRef.setEnabled(True)
            self.tracker_connected = True
            icon = QIcon(":/icon/icons/tracker_connected.png")
            self.ui.btn_Connect.setIcon(icon)

            QApplication.restoreOverrideCursor()

            # Multithreading Method 1 (recomended)
            thread_tracker = threading.Thread(target=self.trackerLoop)
            thread_tracker.start()

            # thread_updateViews = threading.Thread(target=self.showToolOnViews(self.registered_tool))
            # thread_updateViews.start()

            # Multithreading Method 2 (not recomended)
            # Use QApplication.processEvents() inside the loop
        else:
            self.disconnectTracker()

    def trackerLoop(self):
        while self.captureCoordinates:
            if self.tracker_connected:
                data = self.tracker.get_frame()
                # Data is numpy.ndarray(4x4)
                self.refData = data[3][0]  # Ref must be attached to the 1st port
                self.toolData = data[3][1]  # Tool must be attached to the 2nd port
                if np.isnan(self.toolData.sum()) or np.isnan(self.refData.sum()):
                    # TODO: Show some messages or info
                    continue
                

                if (self.isRecordCoords):
                    self.trackerRawCoords_ref.append(self.refData) 
                    self.trackerRawCoords_tool.append(self.toolData) 

                if (self.XyzToRas != []):
                    self.registered_tool = self.applyRegistration(self.toolData, self.refData)
                    # registered_tool = np.squeeze(np.matmul(self.XyzToRas, registered_tool))

                    self.showToolOnViews(self.registered_tool)

                self.toolsWindow.setData(self.refData, self.toolData)
            # else:
            #     self.toolsWindow.setData(self.cam_pos, self.cam_pos)

            time.sleep(0.03)
        return

    def recordCoords(self):
        if (self.isRecordCoords == False) and (self.tracker_connected):
            self.isRecordCoords = True
            self.ui.btn_recordToolRef.setText(' Stop Record')
            icon = QIcon(":/icon/icons/rec_stop.png")
            self.ui.btn_recordToolRef.setIcon(icon)
        else:
            self.isRecordCoords = False
            self.ui.btn_recordToolRef.setText(' Start Record')
            icon = QIcon(":/icon/icons/rec_start.png")
            self.ui.btn_recordToolRef.setIcon(icon)
            refFile = 'RefPoints_'+str(int(time.time()))
            toolFile = 'ToolPoints_'+str(int(time.time()))
            refcoords = np.array(self.trackerRawCoords_ref)
            refcoords = np.swapaxes(refcoords, 0, 2)
            refcoords = np.swapaxes(refcoords, 0, 1)
            toolcoords = np.array(self.trackerRawCoords_tool)
            toolcoords = np.swapaxes(toolcoords, 0, 2)
            toolcoords = np.swapaxes(toolcoords, 0, 1)

            recDir = 'Records'
            if (not os.path.exists(recDir)):
                os.mkdir(recDir)
            np.save(os.path.join(recDir, refFile), refcoords)
            np.save(os.path.join(recDir, toolFile), toolcoords)
            
            QMessageBox.information(self, 'Tracker Points Saved', 'Tool points saved to \'' + toolFile + '.npy\'\nRef points saved to \'' + refFile + '.npy\'')

    def disconnectTracker(self):
        if self.tracker_connected:
            print('Disconnecting Tracker...')
            self.captureCoordinates = False
            self.tracker_connected = False
            self.tracker.stop_tracking()
            self.tracker.close()
    
        self.captureCoordinates = False
        self.ui.btn_Connect.setText('Connect Tracker')
        self.ui.btn_ToolsWindow.setEnabled(False)
        self.ui.btn_recordToolRef.setEnabled(False)
        icon = QIcon(":/icon/icons/tracker_disconnected.png")
        self.ui.btn_Connect.setIcon(icon)

    def showToolsWindow(self):
        # self.toolsWindow.setData(self.cam_pos, self.cam_pos)
        self.toolsWindow.show()

    def showRegMatWindow(self):
        self.regMatWindow.setData(self.regMat)
        res = self.regMatWindow.exec()
        if (res == QDialog.Accepted):
            self.regMat = self.regMatWindow.getData()
        print(self.regMat)
        
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
        self.vtk_widget_2D.set_slice(self.ui.Slider_2D.value())
        self.vtk_widget_2D.interactor.Initialize()
        return

    def slider3DChanged(self):
        self.vtk_widget_3D.setThreshold(self.ui.slider_threshold3D.value())
    
    def slider3DChanged_2(self):
        self.vtk_widget_3D_2.setThreshold(self.ui.slider_threshold3D_2.value())
    
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

    def applyRegistration(self, toolMat, refMat):
        # Calculate tool coords in ref space and apply registration matrix
        # tool2ref = inv(inv(refMat) * toolMat)
        # registeredTool = inv(regMat) * tool2ref

        regMat_inv = np.linalg.inv(self.regMat)
        ref_inv = np.linalg.inv(refMat)
        tool2ref = np.squeeze(np.matmul(ref_inv, toolMat))
        reg = np.squeeze(np.matmul(regMat_inv, tool2ref))
        return reg

    def readPoints(self):
        #Read tool points
        self.registeredPoints = []
        self.RemovePoints()
        from vtk.util.numpy_support import vtk_to_numpy
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Read Points from File", "", "All Data Types (*.mat *.npy *.npz);;Matlab (*.mat);;Numpy (*.npy *.npz);;All Files (*)", options=options)

        if fileName:
            extension = os.path.splitext(fileName)[1].lower()
            
            if 'mat' in extension:
                matFile = loadmat(fileName)
                # self.registeredPoints = matFile['EMT_cor']
                self.registeredPoints = matFile[list(matFile)[-1]]
            elif 'np' in extension:
                self.toolCoords = np.load(fileName)
                self.toolCoords = np.squeeze(self.toolCoords)
                # self.toolCoords = np.swapaxes(self.toolCoords, 0, 2)
                # self.toolCoords = np.swapaxes(self.toolCoords, 0, 1)

                # self.toolCoords = np.swapaxes(self.toolCoords, 1, 2)

                tmp = np.zeros_like(self.toolCoords)
                # tmp = np.swapaxes(tmp, 0, 2)
                numPoints = self.toolCoords.shape[-1]

                if (self.refCoords == []):
                    self.registeredPoints = self.toolCoords
                    for i in range(numPoints):
                        self.registeredPoints[:,:,i] = np.squeeze(np.matmul(self.XyzToRas, self.registeredPoints[:,:,i]))
                    # self.registeredPoints = np.swapaxes(self.toolCoords, 1, 2)
                    # self.registeredPoints = np.swapaxes(self.registeredPoints, 0, 2)
                else:
                    # self.toolCoords = np.swapaxes(self.toolCoords, 1, 2)
                    self.registeredPoints = np.zeros_like(self.toolCoords)
                    # self.registeredPoints = np.swapaxes(self.registeredPoints, 0, 2)
                    regMat_inv = np.linalg.inv(self.regMat)
                    pt_tracker = np.zeros([numPoints, 3], dtype='float')
                    # for ref, tool in zip(self.refCoords, self.toolCoords):
                    for ii in range(numPoints):
                        ref = self.refCoords[:,:,ii]
                        tool = self.toolCoords[:,:,ii]
                        ref_inv = np.linalg.inv(ref)
                        tool2ref = np.squeeze(np.matmul(ref_inv, tool))
                        tmp[:,:,ii] = tool2ref
                        pt_tracker[ii, :] = tool2ref[:,3][:-1]
                        reg = np.squeeze(np.matmul(regMat_inv, tool2ref))
                        reg_aligned = np.squeeze(np.matmul(self.XyzToRas, reg))
                        self.registeredPoints[:,:,ii] = reg

                    np.save('tool2ref.npy', tmp)
                # self.vtk_widget_3D.register(pt_tracker)
            numPoints = self.registeredPoints.shape[-1]

            # # Flip/Rotate points to match the orientation of the image
            # for i in range(numPoints):
            #     pt = self.registeredPoints[:,:,i]
            #     pt_vtk = vtk.vtkMatrix4x4()
            #     pt_vtk.DeepCopy(pt.ravel()) 
            #     flipTrans = vtk.vtkTransform()
            #     # flipTrans.Scale(-1,1,1)
            #     flipTrans.Scale(-1,-1,1)
            #     pt_new = vtk.vtkMatrix4x4()
            #     vtk.vtkMatrix4x4.Multiply4x4(flipTrans.GetMatrix(), pt_vtk, pt_new)

            #     pt_t = np.zeros((4,4))
            #     pt_new.DeepCopy(pt_t.ravel(), pt_new)
            #     self.registeredPoints[:,:,i] = pt_t

            self.ui.slider_Frames.setRange(0, numPoints-1)
            self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registeredPoints.shape[-1]))
            if self.ui.checkBox_showPoints.isChecked():
                self.DrawPoints(self.registeredPoints)
            self.ui.btn_playCam.setEnabled(True)
            self.ui.slider_Frames.setEnabled(True)
            self.ui.checkBox_showPoints.setEnabled(True)
            self.ui.btn_ResetVB.setEnabled(True)

    def readRefPoints(self):
        # Read Reference Points
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Read Points from File", "", "All Data Types (*.mat *.npy *.npz);;Matlab (*.mat);;Numpy (*.npy *.npz);;All Files (*)", options=options)

        if fileName:
            extension = os.path.splitext(fileName)[1].lower()

            if 'mat' in extension:
                matFile = loadmat(fileName)
                # self.registeredPoints = matFile['EMT_cor']
                self.refCoords = matFile[list(matFile)[-1]]
            elif 'np' in extension:
                self.refCoords = np.load(fileName)
                # self.refCoords = np.swapaxes(self.refCoords, 0, 2)
                # self.refCoords = np.swapaxes(self.refCoords, 0, 1)

    def showHidePoints(self):
        if self.ui.checkBox_showPoints.isChecked():
            self.DrawPoints(self.registeredPoints)
        else:
            self.RemovePoints()

    def DrawPoints(self, points):
        self.vtk_widget_3D.draw_points(points)
        self.vtk_widget_3D.add_start_point(points[:,:,0]) # start point
        self.vtk_widget_3D.add_end_point(points[:,:,-1]) # end point

        self.vtk_widget_3D_2.draw_points(points)
        self.vtk_widget_3D_2.add_start_point(points[:,:,0]) # start point
        self.vtk_widget_3D_2.add_end_point(points[:,:,-1]) # end point
        # self.playCam(points)

    def RemovePoints(self):
        self.vtk_widget_3D.remove_points()
        self.vtk_widget_3D_2.remove_points()
        
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
        # if (time.monotonic() - self.lastUpdate < 0.3):
        #     continue

        # self.lastUpdate = time.monotonic()
        # if isinstance(toolMatrix, (list)):
        #     continue
        self.vtk_widget_3D.set_camera(toolMatrix)
        self.vtk_widget_3D_2.set_cross_position(toolMatrix[0,3], toolMatrix[1,3], toolMatrix[2,3], is3D=True)

        self.showToolOn2DView(toolMatrix)
        QApplication.processEvents()
        

    def showToolOn2DView(self, toolMatrix):
        if self.ui.comboBox_2DView.currentText() == 'Axial':
            axial_slice = int((toolMatrix[2,3] - self.origin[2]) / self.spacing[2])
            self.vtk_widget_2D.set_slice(axial_slice)
            self.ui.Slider_2D.setValue(axial_slice)
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            coronal_slice = int((toolMatrix[1,3] - self.origin[1]) / self.spacing[1])
            self.vtk_widget_2D.set_slice(coronal_slice)
            self.ui.Slider_2D.setValue(coronal_slice)
        else: # self.ui.comboBox_2DView.currentText() == 'Sagittal'
            sagittal_slice = int((toolMatrix[0,3] - self.origin[0]) / self.spacing[0])
            self.vtk_widget_2D.set_slice(sagittal_slice)
            self.ui.Slider_2D.setValue(sagittal_slice)

        if self.ui.comboBox_2DView.currentText() == 'Axial':
            self.vtk_widget_2D.set_cross_position(toolMatrix[0,3], toolMatrix[1,3])
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            self.vtk_widget_2D.set_cross_position(toolMatrix[0,3], toolMatrix[2,3]+self.origin[1])
        else: # if self.ui.comboBox_2DView.currentText() == 'Sagittal':
            self.vtk_widget_2D.set_cross_position(toolMatrix[1,3], toolMatrix[2,3]+self.origin[0])

    def playCam(self):
        # cam_pos = np.array([[0.6793, -0.7232, -0.1243, 33.3415], [-0.0460, -0.2110, 0.9764, -29.0541], [-0.7324, -0.6576, -0.1767, 152.6576], [0, 0, 0, 1.0000]])
        if self.registeredPoints == []:
            QMessageBox.critical(self, 'No Points Found', 'Please load the registered points first !')
            return
        self.ui.btn_pauseCam.setEnabled(True)
        self.ui.btn_stopCam.setEnabled(True)
        self.paused = False

        # Multithreading Method 1 (recomended)
        thread_cam = threading.Thread(target=self.playCamLoop)
        thread_cam.start()

        # Multithreading Method 2 (not recomended)
        # use QApplication.processEvents() inside the loop

    def playCamLoop(self):
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
        return
    
    def pauseCam(self):
        self.paused = True

    def stopCam(self):
        self.paused = True
        self.ui.slider_Frames.setValue(0)
        self.ui.btn_pauseCam.setEnabled(False)
        self.ui.btn_stopCam.setEnabled(False)
    
    def change2DView(self):
        self.vtk_widget_2D.reset_view(is3D=False)
        # self.vtk_widget_2D.RemoveImage()
        self.vtk_widget_2D.viewType = self.ui.comboBox_2DView.currentText()
        self.vtk_widget_2D.show_image(self.imgReader, self.dims, self.spacing, self.origin)
        self.updateSubPanels(self.dims)

        if not self.vtk_widget_2D.cross == None:
            self.vtk_widget_2D.remove_cross()
            if (self.trackerReady and self.tracker_connected):
                self.showToolOnViews(self.toolData)
            else:
                self.showToolOnViews(self.cam_pos)

    def ResetViewports(self):
        self.vtk_widget_3D.reset_view(is3D=True)
        self.vtk_widget_3D_2.reset_view(is3D=True)
        self.vtk_widget_2D.reset_view(is3D=False)
        self.updateSubPanels(self.dims)
        self.ui.slider_threshold3D.setValue(-600)
        self.ui.slider_threshold3D_2.setValue(-600)


    def ResetVB(self):
        self.RemovePoints()
        self.registeredPoints = []
        self.refCoords = []
        self.toolCoords == []
        self.stopCam()
        self.vtk_widget_2D.remove_cross()
        self.ui.btn_ResetVB.setEnabled(False)
        self.ui.btn_playCam.setEnabled(False)
        self.ui.btn_pauseCam.setEnabled(False)
        self.ui.btn_stopCam.setEnabled(False)
        self.ui.slider_Frames.setEnabled(False)
        self.ui.checkBox_showPoints.setEnabled(False)
        self.ResetViewports()

    def centerlineExtract(self):
        myArguments = 'vmtksurfacereader -ifile m01_AirwaySegments.vtk --pipe vmtkcenterlines --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25 --pipe vmtksurfaceviewer -i @vmtkcenterlines.o -array MaximumInscribedSphereRadius'
        myPype = pypes.PypeRun(myArguments)

    def setup(self, size):
        self.ui = MainWin.Ui_MainWin()
        self.ui.setupUi(self)
        # sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.resize(sizeObject.width(), sizeObject.height())
        # self.resize(size.width(), size.height())
        self.vtk_widget_3D = QVtkViewer3D(self.ui.vtk_panel_3D_1, size, 'Virtual')
        self.vtk_widget_3D_2 =  QVtkViewer3D(self.ui.vtk_panel_3D_2, size, 'Normal')
        self.vtk_widget_2D = QVtkViewer2D(self.ui.vtk_panel_2D, size, self.ui.comboBox_2DView.currentText())
        self.hideSubPanels()

    def initialize(self):
        pass

    def closeEvent(self, event):
        print('Exitting Application...')
        self.disconnectTracker()
        event.accept()

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
    app.setStyle("fusion")

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
    app.setStyleSheet("QToolBar { background-color: rgb(51,51,51); }")

    screen = app.primaryScreen()
    size = screen.availableGeometry()  # size.height(), size.width()
    main_win = MainWindow(size)
    main_win.showMaximized()
    # main_win.show()
    # main_win.initialize()

    # if main_win.tracker_connected == True:
    #     main_win.disconnectTracker()
    sys.exit(app.exec())
