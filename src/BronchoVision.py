# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 01:09:45 2019

@author: Saeed
"""

import os
import sqlite3
import sys
import threading
import time

import numpy as np
import vtk
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                             QFileDialog, QLabel, QMainWindow, QMessageBox,
                             QSplashScreen, QTableWidgetItem, QWidget)
from scipy.io import loadmat

from modules.patient import Patient
from modules.tracker import Tracker
from modules.registration import Registration
from modules.centerline import Centerline
from ui import MainWin
from ui.UiWindows import NewPatientWindow, RegMatWindow, ToolsWindow
from viewers.QVtkViewer2D import QVtkViewer2D
from viewers.QVtkViewer3D import QVtkViewer3D


class MainWindow(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.db = None
        self.db_connection = None
        
        self.record_coords = False

        self.trackerRawCoords_ref = []
        self.trackerRawCoords_tool = []

        self.vtk_widget_3D = None
        self.vtk_widget_3D_2 = None
        self.vtk_widget_2D = None
        self.ui = None
        self.registered_points = []
        self.tool_coords = []
        self.ref_coords = []
        self.setup(size)
        self.paused = False
        self.size = size
        self.cam_pos = None
        self.exitting = False
        
        self.last_update = 0
        self.registered_tool = []

        self.patients_dir = '..\\Patients'
        # TODO: record in the patient_dir 
        self.records_dir = '..\\Records'
        self.curr_patient = None
        
        self.toolsWindow = ToolsWindow(self)
        self.regMatWindow = RegMatWindow(self)
        self.newPatientWindow = NewPatientWindow(self)

        os.path.abspath

        self.patient_cls = Patient(self.ui.tableWidget_Patients, self.newPatientWindow, self.patients_dir)
        self.patient_cls.get_patients_from_db()
        self.tracker_cls = Tracker()
        self.centerline_cls = None

        self.ui.btn_LoadPatient.hide()
        self.ui.btn_DeletePatient.hide()
        self.ui.checkBox_showCenterline_image.hide()

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



        self.ui.btn_NewPatient.clicked.connect(self.new_patient)
        self.ui.btn_LoadPatient.clicked.connect(self.load_patient)
        self.ui.btn_DeletePatient.clicked.connect(self.delete_patient)
        self.ui.btn_ImportPatient.clicked.connect(self.import_patient)
        self.ui.btn_ClearPatients.clicked.connect(self.clear_patients)

        self.ui.Slider_2D.valueChanged.connect(self.slider_changed)

        self.ui.btn_LoadToolPoints.clicked.connect(self.read_tool_points)
        self.ui.btn_LoadRefPoints.clicked.connect(self.read_ref_points)
        self.ui.checkBox_showPoints.stateChanged.connect(self.show_hide_points)
        self.ui.checkBox_showCenterline_image.stateChanged.connect(self.show_hide_centerline_image)
        self.ui.btn_playCam.clicked.connect(self.play_cam)
        self.ui.btn_pauseCam.clicked.connect(self.pause_cam)
        self.ui.btn_stopCam.clicked.connect(self.stop_cam)
        self.ui.slider_Frames.valueChanged.connect(self.frame_changed)
        self.ui.slider_threshold3D.valueChanged.connect(self.slider_3D_changed)
        self.ui.slider_threshold3D_2.valueChanged.connect(self.slider_3D_changed_2)
        self.ui.btn_ResetViewports.clicked.connect(self.reset_viewports)
        self.ui.btn_ResetVB.clicked.connect(self.reset_VB)
        self.ui.comboBox_2DView.currentIndexChanged.connect(self.change_2D_view)

        self.ui.btn_Connect.clicked.connect(self.connect_tracker)
        self.ui.btn_ToolsWindow.clicked.connect(self.show_tools_window)
        self.ui.btn_regMat.clicked.connect(self.show_regMat_window)
        self.ui.btn_recordToolRef.clicked.connect(self.coords_record)

        self.ui.tabWidget.currentChanged.connect(self.virtual_tab_changed)
        self.ui.btn_loadCenterline.clicked.connect(self.load_centerline)
        self.ui.btn_extractCenterline.clicked.connect(self.centerline_extract)

    '''
    >>> ----------------------------------------
    >>> Patients ops
    >>> ----------------------------------------
    '''
    def new_patient(self):
        self.patient_cls.new_patient()
        index = self.ui.tableWidget_Patients.model().index(self.ui.tableWidget_Patients.rowCount()-1,0)
        self.curr_patient = self.ui.tableWidget_Patients.model().data(index)
        self.load_patient()

    def load_patient(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if not self.curr_patient:
            index = self.ui.tableWidget_Patients.selectionModel().selectedRows()[0]
            self.curr_patient = self.ui.tableWidget_Patients.model().data(index)
        try:
            self.patient_cls.load_patient(self.curr_patient)
            self.show_images()
            self.update_subPanels(self.patient_cls.dims)
            self.ui.btn_LoadPatient.hide()
            self.ui.btn_DeletePatient.hide()

            # TODO : check and load image centerline if available
            # self.ui.label_imageCenterline.setText('Available')
            # self.ui.label_imageCenterline.setStyleSheet("color: rgb(100, 255, 130);")
            self.ui.label_imageCenterline.setText('Not Available')
            self.ui.label_imageCenterline.setStyleSheet("color: rgb(255, 55, 120);")
            self.ui.label_trackerCenterline.setText('Not Available')
            self.ui.label_trackerCenterline.setStyleSheet("color: rgb(255, 55, 120);")
            
            QApplication.restoreOverrideCursor()
        except:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(None, 'Wrong Header', 'Can not read Image Origin from header!\nImage position might be wrong')

    def delete_patient(self):
        index = self.ui.tableWidget_Patients.selectionModel().selectedRows()[0]
        selected_patient = self.ui.tableWidget_Patients.model().data(index)
        ret = QMessageBox.question(None, 'Delete Patient',
                                    f'Do you want to delete {selected_patient} ?\nThis action can NOT be undone',
                                    QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            if self.patient_cls.delete_patient(selected_patient):
                self.ui.tableWidget_Patients.removeRow(index.row())
                self.ui.tableWidget_Patients.clearSelection()
                self.ui.btn_LoadPatient.hide()
                self.ui.btn_DeletePatient.hide()
                if selected_patient == self.curr_patient:
                    self.curr_patient = None
                    self.set_ui_elements_enabled(False)
                    self.remove_images_from_viewports()
            else:
                QMessageBox.critical(self, 'Failed to delete patient', f'Can not delete this patient!')

    def clear_patients(self):
        ret = QMessageBox.question(self, 'Delete All Patients',
                                    f'Are you sure you want to delete all patients ?!\nThis action is NOT reversible!',
                                    QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.patient_cls.clear_patients()
            self.ui.btn_LoadPatient.hide()
            self.ui.btn_DeletePatient.hide()
            self.set_ui_elements_enabled(False)
            self.remove_images_from_viewports()
    
    def import_patient(self):
        # TODO: importPatient
        QMessageBox.information(None, 'Comming Soon...', f'Not Implemented Yet !')

    '''
    >>> ----------------------------------------
    >>> Tracker ops
    >>> ----------------------------------------
    '''

    def connect_tracker(self):
        if self.tracker_cls.tracker_connected == False:
            self.ui.btn_Connect.setText('Connecting...')
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if self.tracker_cls.connect():
                self.ui.btn_Connect.setText('Disconnect Tracker')
                self.ui.btn_ToolsWindow.setEnabled(True)
                self.ui.btn_recordToolRef.setEnabled(True)
                icon = QIcon(":/icon/icons/tracker_connected.png")
                self.ui.btn_Connect.setIcon(icon)
                QApplication.restoreOverrideCursor()
            else:
                QApplication.restoreOverrideCursor()
                msg = 'Please check the following:\n' \
                        '  1) NDI device connection\n' \
                        '  2) Is the NDI device switched on?!\n' \
                        '  3) Do you have sufficient privilege to connect to the device?\n' \
                        '     (e.g. on Linux are you part of the \"dialout\" group?)'
                QMessageBox.critical(self, 'Tracker Connection Failed', f'Can not connect to the tracker!\n{msg}')
                self.ui.btn_Connect.setText('Connect Tracker')
                self.ui.btn_Connect.setStyleSheet("background-color: rgb(65, 65, 65)")
        else:
            self.disconnect_tracker()

    def disconnect_tracker(self):
        if self.tracker_cls.tracker_connected:
            print('Disconnecting Tracker...')
            self.tracker_cls.disconnect()
            self.ui.btn_Connect.setText('Connect Tracker')
            self.ui.btn_ToolsWindow.setEnabled(False)
            self.ui.btn_recordToolRef.setEnabled(False)
            icon = QIcon(":/icon/icons/tracker_disconnected.png")
            self.ui.btn_Connect.setIcon(icon)

    def tracker_loop(self):
        while self.tracker_cls.capture_coords:
            if (self.exitting):
                break
            if self.tracker_cls.tracker_connected:
                ref_mat, tool_mat = self.tracker_cls.get_frame()
                if np.isnan(tool_mat.sum()) or np.isnan(ref_mat.sum()):
                    # TODO: Show some messages or info
                    continue

                if (self.record_coords):
                    self.trackerRawCoords_ref.append(ref_mat) 
                    self.trackerRawCoords_tool.append(tool_mat) 

                if (self.patients.XyzToRas != []):
                    self.registered_tool = self.applyRegistration(tool_mat, ref_mat)
                    # registered_tool = np.squeeze(np.matmul(self.patients.XyzToRas, registered_tool))

                    self.showToolOnViews(self.registered_tool)

                self.toolsWindow.setData(ref_mat, tool_mat)

            time.sleep(0.03)
        return
        
    def coords_record(self):
        if (self.record_coords == False) and (self.tracker_cls.tracker_connected):
            self.ui.btn_recordToolRef.setEnabled(False)
            self.countdownSplash()
            self.ui.btn_recordToolRef.setEnabled(True)
            self.record_coords = True
            self.ui.btn_recordToolRef.setText(' Stop Record')
            icon = QIcon(":/icon/icons/rec_stop.png")
            self.ui.btn_recordToolRef.setIcon(icon)
            self.ui.btn_recordToolRef.setStyleSheet("background-color: rgba(235, 25, 75, 100)")
        else:
            self.record_coords = False
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

            self.ui.btn_recordToolRef.setStyleSheet("background-color: rgb(65, 65, 65)")
            self.ui.btn_registerCenterlines.setEnabled(True)

            if (not os.path.exists(self.records_dir)):
                os.mkdir(self.records_dir)
            np.save(os.path.join(self.records_dir, refFile), refcoords)
            np.save(os.path.join(self.records_dir, toolFile), toolcoords)
            
            QMessageBox.information(self, 'Tracker Points Saved', 'Tool points saved to \'' + toolFile + '.npy\'\nRef points saved to \'' + refFile + '.npy\'')

    '''
    >>> ----------------------------------------
    >>> Viewers ops
    >>> ----------------------------------------
    '''
    def show_images(self):
        self.remove_images_from_viewports()

        flipXFilter = vtk.vtkImageFlip()
        flipXFilter.SetFilteredAxis(0); # flip x axis
        flipXFilter.SetInputConnection(self.patient_cls.imgReader.GetOutputPort())
        flipXFilter.Update()

        flipYFilter = vtk.vtkImageFlip()
        flipYFilter.SetFilteredAxis(1); # flip y axis
        flipYFilter.SetInputConnection(flipXFilter.GetOutputPort())
        flipYFilter.Update()

        self.patient_cls.reoriented_image = flipYFilter

        self.vtk_widget_3D.show_image(self.patient_cls.reoriented_image)
        self.vtk_widget_3D_2.show_image(self.patient_cls.reoriented_image)
        self.vtk_widget_2D.show_image(self.patient_cls.reoriented_image, self.patient_cls.dims, self.patient_cls.spacing, self.patient_cls.origin)
        
        self.set_ui_elements_enabled(True)

        self.ui.tabWidget_offline.setEnabled(True)

    def set_ui_elements_enabled(self, isEnabled):
        self.ui.btn_LoadToolPoints.setEnabled(isEnabled)
        self.ui.btn_LoadRefPoints.setEnabled(isEnabled)
        self.ui.btn_extractCenterline.setEnabled(isEnabled)
        self.ui.btn_loadCenterline.setEnabled(isEnabled)
        self.ui.btn_Segment.setEnabled(isEnabled)
        self.ui.groupBox_Viewports.setEnabled(isEnabled)

        self.ui.slider_threshold3D.setEnabled(isEnabled)
        self.ui.slider_threshold3D_2.setEnabled(isEnabled)
        self.ui.btn_ResetViewports.setEnabled(isEnabled)

    def remove_images_from_viewports(self):
        self.vtk_widget_3D.remove_image()
        self.vtk_widget_3D_2.remove_image()
        self.vtk_widget_2D.remove_image()

    def virtual_tab_changed(self):
        if (self.ui.tabWidget_2.currentIndex() == 0):
            self.tracker_cls.tracker_ready = True
        else:
            self.tracker_cls.tracker_ready = False
        # print(self.ui.tabWidget.currentIndex(), self.tracker_cls.tracker_ready)
        
    def countdown_splash(self):
        splash_pix = QPixmap('ui/icons/5.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        # splash.showMessage("<h1><font color='orange'>Ready for record</font></h1>", Qt.AlignTop | Qt.AlignCenter, Qt.black)
        timer = QtCore.QElapsedTimer()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/4.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/3.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/2.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/1.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.close()

    def show_tools_window(self):
        # self.toolsWindow.setData(self.cam_pos, self.cam_pos)
        self.toolsWindow.show()

    def show_regMat_window(self):
        self.regMatWindow.setData(self.regMat)
        res = self.regMatWindow.exec()
        if (res == QDialog.Accepted):
            self.regMat = self.regMatWindow.getData()
        print(self.regMat)
        
    def update_subPanels(self, dims):
        self.show_subPanels()
        # image = reader.GetOutput()
        # dims = image.GetDimensions()

        # Commented parts are correct, changed only for this phantom image!
        # if self.ui.comboBox_2DView.currentText() == 'Axial':
        if self.ui.comboBox_2DView.currentText() == 'Coronal':    
            # self.ui.Slider_2D.setRange(0, dims[2]-1)
            # self.ui.Slider_2D.setValue(dims[2]//2)
            self.ui.Slider_2D.setRange(0, dims[0]-1)
            self.ui.Slider_2D.setValue(dims[0]//2)
        # elif self.ui.comboBox_2DView.currentText() == 'Coronal':
        elif self.ui.comboBox_2DView.currentText() == 'Sagittal':
            # self.ui.Slider_2D.setRange(0, dims[1]-1)
            # self.ui.Slider_2D.setValue(dims[1]//2)
            self.ui.Slider_2D.setRange(0, dims[2]-1)
            self.ui.Slider_2D.setValue(dims[2]//2)
        # else: self.ui.comboBox_2DView.currentText() == 'Sagittal':
        elif self.ui.comboBox_2DView.currentText() == 'Axial':
            # self.ui.Slider_2D.setRange(0, dims[0]-1)
            # self.ui.Slider_2D.setValue(dims[0]//2)
            self.ui.Slider_2D.setRange(0, dims[1]-1)
            self.ui.Slider_2D.setValue(dims[1]//2)

    def slider_changed(self):
        self.vtk_widget_2D.set_slice(self.ui.Slider_2D.value())
        self.vtk_widget_2D.interactor.Initialize()
        return

    def slider_3D_changed(self):
        self.vtk_widget_3D.setThreshold(self.ui.slider_threshold3D.value())
    
    def slider_3D_changed_2(self):
        self.vtk_widget_3D_2.setThreshold(self.ui.slider_threshold3D_2.value())
    
    def hide_subPanels(self):
        self.ui.SubPanel_3D.hide()
        self.ui.SubPanel_3D_2.hide()
        self.ui.SubPanel_2D.hide()
        self.ui.SubPanel_endoscope.hide()

    def show_subPanels(self):
        self.ui.SubPanel_3D.show()
        self.ui.SubPanel_3D_2.show()
        self.ui.SubPanel_2D.show()
        self.ui.SubPanel_endoscope.show()

    def apply_registration(self, toolMat, refMat):
        # Calculate tool coords in ref space and apply registration matrix
        # tool2ref = inv(inv(refMat) * toolMat)
        # registeredTool = inv(regMat) * tool2ref

        regMat_inv = np.linalg.inv(self.regMat)
        ref_inv = np.linalg.inv(refMat)
        tool2ref = np.squeeze(np.matmul(ref_inv, toolMat))
        reg = np.squeeze(np.matmul(regMat_inv, tool2ref))
        return reg

    def read_points(self):
        points = []
        # from vtk.util.numpy_support import vtk_to_numpy
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Read Points from File", "",
                                                "All Data Types (*.mat *.npy *.npz);;Matlab (*.mat);;Numpy (*.npy *.npz);;All Files (*)",
                                                options=options)
        if fileName:
            extension = os.path.splitext(fileName)[1].lower()
            if 'mat' in extension:
                matFile = loadmat(fileName)
                # self.registered_points = matFile['EMT_cor']
                points = matFile[list(matFile)[-1]]
            elif 'np' in extension:
                points = np.load(fileName)
                points = np.squeeze(points)
        return points

    def load_centerline(self):
        self.patient_cls.centerline = self.read_points()
        if self.patient_cls.centerline != []:
            self.ui.checkBox_showCenterline_image.show()
            self.ui.checkBox_showCenterline_image.setEnabled(True)
            self.ui.checkBox_showCenterline_image.setChecked(True)
            self.show_hide_centerline_image()
            self.ui.label_imageCenterline.setText('Available')
            self.ui.label_imageCenterline.setStyleSheet("color: rgb(100, 255, 130);")
            self.save_image_centerline()
        # TODO : edit patient and add centerline to dir + db

    def save_image_centerline(self):
        try:
            image_centerline_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'centerline_image.npy')
            if os.path.exists(image_centerline_path):
                os.remove(image_centerline_path)
            np.save(image_centerline_path, self.patient_cls.centerline)
        except:
            QMessageBox.critical(self, 'Centerline NOT Saved', 'There was a problem saving the centerline!')

    def read_tool_points(self):
        #Read tool points
        points = self.read_points()
        if points != []:
            self.registered_points = []
            self.remove_points()
            self.tool_coords = points
            # self.toolCoords = np.swapaxes(self.toolCoords, 0, 2)
            # self.toolCoords = np.swapaxes(self.toolCoords, 0, 1)
            # self.toolCoords = np.swapaxes(self.toolCoords, 1, 2)

            tmp = np.zeros_like(self.tool_coords)
            # tmp = np.swapaxes(tmp, 0, 2)
            numPoints = self.tool_coords.shape[-1]

            if (self.ref_coords == []):
                self.registered_points = self.tool_coords
                for i in range(numPoints):
                    self.registered_points[:,:,i] = np.squeeze(np.matmul(self.patient_cls.XyzToRas, self.registered_points[:,:,i]))
                # self.registered_points = np.swapaxes(self.toolCoords, 1, 2)
                # self.registered_pointsregistered_points = np.swapaxes(self.registered_points, 0, 2)
            else:
                # self.toolCoords = np.swapaxes(self.toolCoords, 1, 2)
                self.registered_points = np.zeros_like(self.tool_coords)
                # self.registered_points = np.swapaxes(self.registered_points, 0, 2)
                regMat_inv = np.linalg.inv(self.regMat)
                pt_tracker = np.zeros([numPoints, 3], dtype='float')
                # for ref, tool in zip(self.refCoords, self.toolCoords):
                for ii in range(numPoints):
                    ref = self.ref_coords[:,:,ii]
                    tool = self.tool_coords[:,:,ii]
                    ref_inv = np.linalg.inv(ref)
                    tool2ref = np.squeeze(np.matmul(ref_inv, tool))
                    tmp[:,:,ii] = tool2ref
                    pt_tracker[ii, :] = tool2ref[:,3][:-1]
                    reg = np.squeeze(np.matmul(regMat_inv, tool2ref))
                    reg_aligned = np.squeeze(np.matmul(self.patient_cls.XyzToRas, reg))
                    self.registered_points[:,:,ii] = reg

                np.save('tool2ref.npy', tmp)
            # self.vtk_widget_3D.register(pt_tracker)
            numPoints = self.registered_points.shape[-1]

            # # Flip/Rotate points to match the orientation of the image
            # for i in range(numPoints):
            #     pt = self.registered_points[:,:,i]
            #     pt_vtk = vtk.vtkMatrix4x4()
            #     pt_vtk.DeepCopy(pt.ravel()) 
            #     flipTrans = vtk.vtkTransform()
            #     # flipTrans.Scale(-1,1,1)
            #     flipTrans.Scale(-1,-1,1)
            #     pt_new = vtk.vtkMatrix4x4()
            #     vtk.vtkMatrix4x4.Multiply4x4(flipTrans.GetMatrix(), pt_vtk, pt_new)

            #     pt_t = np.zeros((4,4))
            #     pt_new.DeepCopy(pt_t.ravel(), pt_new)
            #     self.registered_points[:,:,i] = pt_t

            self.ui.slider_Frames.setRange(0, numPoints-1)
            self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registered_points.shape[-1]))
            if self.ui.checkBox_showPoints.isChecked():
                self.draw_points(self.registered_points)
            self.ui.btn_playCam.setEnabled(True)
            self.ui.slider_Frames.setEnabled(True)
            self.ui.checkBox_showPoints.setEnabled(True)
            self.ui.btn_ResetVB.setEnabled(True)

    def read_ref_points(self):
        # Read Reference Points
        self.ref_coords = self.read_points()
        if self.ref_coords != []:
            self.registered_points = []
            self.remove_points()
        # self.ref_coords = np.swapaxes(self.ref_coords, 0, 2)
        # self.ref_coords = np.swapaxes(self.ref_coords, 0, 1)

    def show_hide_points(self):
        if self.ui.checkBox_showPoints.isChecked():
            self.draw_points(self.registered_points)
        else:
            self.remove_points()

    def show_hide_centerline_image(self):
        if self.ui.checkBox_showCenterline_image.isChecked():
            self.draw_centerline(self.patient_cls.centerline)
        else:
            self.remove_centerline()

    def draw_points(self, points):
        self.vtk_widget_3D.draw_points(points)
        self.vtk_widget_3D.add_start_point(points[:,:,0]) # start point
        self.vtk_widget_3D.add_end_point(points[:,:,-1]) # end point

        self.vtk_widget_3D_2.draw_points(points)
        self.vtk_widget_3D_2.add_start_point(points[:,:,0]) # start point
        self.vtk_widget_3D_2.add_end_point(points[:,:,-1]) # end point
        # self.playCam(points)

    def draw_centerline(self, points):
        self.vtk_widget_3D.draw_centerline(points)
        self.vtk_widget_3D_2.draw_centerline(points)

    def remove_points(self):
        self.vtk_widget_3D.remove_points()
        self.vtk_widget_3D_2.remove_points()
    
    def remove_centerline(self):
        self.vtk_widget_3D.remove_centerline()
        self.vtk_widget_3D_2.remove_centerline()
        
    def frame_changed(self):
        if self.registered_points is None:
            self.ui.slider_Frames.setValue(0)
            # QMessageBox.critical(self, 'No Points Found', 'Please load the registered points first !')
            return

        pNum = self.ui.slider_Frames.value()
        self.cam_pos = self.registered_points[:,:,pNum]
        
        # cam_pos_t = vtk.vtkMatrix4x4()
        # cam_pos_t.DeepCopy(cam_pos.ravel()) 
        # flipTrans = vtk.vtkTransform()
        # flipTrans.Scale(-1,-1,1)
        # newMat = vtk.vtkMatrix4x4()
        # vtk.vtkMatrix4x4.Multiply4x4(flipTrans.GetMatrix(), cam_pos_t, newMat)
        # self.vtk_widget_3D.setCamera(newMat)

        self.show_tool_on_views(self.cam_pos)

        self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registered_points.shape[-1]))

    def show_tool_on_views(self, tool_mat):
        # if (time.monotonic() - self.lastUpdate < 0.3):
        #     continue

        # self.lastUpdate = time.monotonic()
        # if isinstance(toolMatrix, (list)):
        #     continue
        self.vtk_widget_3D.set_camera(tool_mat)
        self.vtk_widget_3D_2.set_cross_position(tool_mat[0,3], tool_mat[1,3], tool_mat[2,3], is3D=True)

        self.show_tool_on_2D_view(tool_mat)
        QApplication.processEvents()
        

    def show_tool_on_2D_view(self, tool_mat):
        # Commented parts are correct, changed only for this phantom image!
        # if self.ui.comboBox_2DView.currentText() == 'Axial':
        if self.ui.comboBox_2DView.currentText() == 'Coronal':
            # axial_slice = int((tool_mat[2,3] - self.patient_cls.origin[2]) / self.patient_cls.spacing[2])
            axial_slice = int((tool_mat[0,3] - self.patient_cls.origin[0]) / self.patient_cls.spacing[0])
            self.vtk_widget_2D.set_slice(axial_slice)
            self.ui.Slider_2D.setValue(axial_slice)
        # elif self.ui.comboBox_2DView.currentText() == 'Coronal':
        elif self.ui.comboBox_2DView.currentText() == 'Sagittal':
            # coronal_slice = int((tool_mat[1,3] - self.patient_cls.origin[1]) / self.patient_cls.spacing[1])
            coronal_slice = int((tool_mat[2,3] - self.patient_cls.origin[2]) / self.patient_cls.spacing[2])
            self.vtk_widget_2D.set_slice(coronal_slice)
            self.ui.Slider_2D.setValue(coronal_slice)
        # elif self.ui.comboBox_2DView.currentText() == 'Sagittal':
        elif self.ui.comboBox_2DView.currentText() == 'Axial':
            # sagittal_slice = int((tool_mat[0,3] - self.patient_cls.origin[0]) / self.patient_cls.spacing[0])
            sagittal_slice = int((tool_mat[1,3] - self.patient_cls.origin[1]) / self.patient_cls.spacing[1])
            self.vtk_widget_2D.set_slice(sagittal_slice)
            self.ui.Slider_2D.setValue(sagittal_slice)

        # if self.ui.comboBox_2DView.currentText() == 'Axial':
        if self.ui.comboBox_2DView.currentText() == 'Sagittal':
            self.vtk_widget_2D.set_cross_position(tool_mat[0,3], tool_mat[1,3])
        # elif self.ui.comboBox_2DView.currentText() == 'Coronal':
        elif self.ui.comboBox_2DView.currentText() == 'Axial':
            self.vtk_widget_2D.set_cross_position(tool_mat[0,3], tool_mat[2,3]+self.patient_cls.origin[1])
        # else: # if self.ui.comboBox_2DView.currentText() == 'Sagittal':
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            self.vtk_widget_2D.set_cross_position(tool_mat[1,3], tool_mat[2,3]+self.patient_cls.origin[0])

    def play_cam(self):
        # cam_pos = np.array([[0.6793, -0.7232, -0.1243, 33.3415], [-0.0460, -0.2110, 0.9764, -29.0541], [-0.7324, -0.6576, -0.1767, 152.6576], [0, 0, 0, 1.0000]])
        if self.registered_points == []:
            QMessageBox.critical(self, 'No Points Found', 'Please load the registered points first !')
            return
        self.ui.btn_pauseCam.setEnabled(True)
        self.ui.btn_stopCam.setEnabled(True)
        self.paused = False

        # Multithreading Method 1 (recomended)
        thread_cam = threading.Thread(target=self.play_cam_loop)
        thread_cam.start()

        # Multithreading Method 2 (not recomended)
        # use QApplication.processEvents() inside the loop

    def play_cam_loop(self):
        for i in range(self.ui.slider_Frames.value(),self.registered_points.shape[-1]):
            if (self.exitting):
                break
            if self.paused:
                break

            self.cam_pos = self.registered_points[:,:,i]

            # cam_pos_t = vtk.vtkMatrix4x4()
            # cam_pos_t.DeepCopy(self.cam_pos.ravel()) 
            # flipTrans = vtk.vtkTransform()
            # flipTrans.Scale(-1,-1,1)
            # newMat = vtk.vtkMatrix4x4()
            # vtk.vtkMatrix4x4.Multiply4x4(flipTrans.GetMatrix(), cam_pos_t, newMat)
            # self.vtk_widget_3D.setCamera(newMat)

            # self.vtk_widget_3D.setCamera(self.cam_pos)

            self.ui.slider_Frames.setValue(i)
            self.ui.lbl_FrameNum.setText(str(self.ui.slider_Frames.value()) + ' of ' + str(self.registered_points.shape[-1]))

            time.sleep(0.1)
        return
    
    def pause_cam(self):
        self.paused = True

    def stop_cam(self):
        self.paused = True
        self.ui.slider_Frames.setValue(0)
        self.ui.btn_pauseCam.setEnabled(False)
        self.ui.btn_stopCam.setEnabled(False)
    
    def change_2D_view(self):
        self.vtk_widget_2D.reset_view(is3D=False)
        # self.vtk_widget_2D.RemoveImage()

        # Messed up! only for this phantom image!
        if self.ui.comboBox_2DView.currentText() == 'Axial':
            phantom_view = 'Coronal'
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            phantom_view = 'Sagittal'
        elif self.ui.comboBox_2DView.currentText() == 'Sagittal':
            phantom_view = 'Axial'
        self.vtk_widget_2D.viewType = phantom_view
        
        # self.vtk_widget_2D.viewType = self.ui.comboBox_2DView.currentText()
        self.vtk_widget_2D.show_image(self.patient_cls.reoriented_image, self.patient_cls.dims, self.patient_cls.spacing, self.patient_cls.origin)
        self.update_subPanels(self.patient_cls.dims)

        if self.vtk_widget_2D.cross != None:
            self.vtk_widget_2D.remove_cross()
            if (self.tracker_cls.tracker_ready and self.tracker_connected):
                self.show_tool_on_views(self.tool_mat)
            else:
                self.show_tool_on_views(self.cam_pos)

    def reset_viewports(self):
        self.vtk_widget_3D.reset_view(is3D=True)
        self.vtk_widget_3D_2.reset_view(is3D=True)
        self.vtk_widget_2D.reset_view(is3D=False)
        self.update_subPanels(self.patient_cls.dims)
        self.ui.slider_threshold3D.setValue(-600)
        self.ui.slider_threshold3D_2.setValue(-600)


    def reset_VB(self):
        self.stop_cam()
        self.vtk_widget_2D.remove_cross()
        self.ui.btn_ResetVB.setEnabled(False)
        self.ui.btn_playCam.setEnabled(False)
        self.ui.btn_pauseCam.setEnabled(False)
        self.ui.btn_stopCam.setEnabled(False)
        self.ui.slider_Frames.setEnabled(False)
        self.ui.checkBox_showPoints.setEnabled(False)
        self.reset_viewports()
        self.remove_points()
        self.registered_points = []
        self.ref_coords = []
        self.tool_coords == []

    def centerline_extract(self):
        if self.centerline != None:
            del self.centerline
        self.centerline = Centerline(self.patient_cls.image_path)

        self.patient_cls.centerline = self.centerline_cls.extract()

    def setup(self, size):
        self.ui = MainWin.Ui_MainWin()
        self.ui.setupUi(self)
        # sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.resize(sizeObject.width(), sizeObject.height())
        # self.resize(size.width(), size.height())
        self.vtk_widget_3D = QVtkViewer3D(self.ui.vtk_panel_3D_1, size, 'Virtual')
        self.vtk_widget_3D_2 = QVtkViewer3D(self.ui.vtk_panel_3D_2, size, 'Normal')

        # Messed up! only for this phantom image!
        phantom_view = ''
        if self.ui.comboBox_2DView.currentText() == 'Axial':
            phantom_view = 'Coronal'
        elif self.ui.comboBox_2DView.currentText() == 'Coronal':
            phantom_view = 'Sagittal'
        elif self.ui.comboBox_2DView.currentText() == 'Sagittal':
            phantom_view = 'Axial'
        viewType = phantom_view

        # viewType = self.ui.comboBox_2DView.currentText()
        self.vtk_widget_2D = QVtkViewer2D(self.ui.vtk_panel_2D, size, viewType)
        self.hide_subPanels()

    def initialize(self):
        pass

    def closeEvent(self, event):
        self.exitting = True
        print('Exitting Application...')
        self.disconnect_tracker()
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
    #     main_win.disconnect_tracker()
    sys.exit(app.exec())
