# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 01:09:45 2019

@author: Saeed
"""

import os
import sys
import threading
import time

import numpy as np
from scipy.misc.common import face
import vtk
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                             QFileDialog, QLabel, QMainWindow, QMessageBox,
                             QSplashScreen, QTableWidgetItem, QWidget, QVBoxLayout)
from scipy.io import loadmat

from modules.patient import Patient
from modules.tracker import Tracker
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
        
        self.pause_tracker_loop = False
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

        self.new_patient = False

        self.is_segmented = False
        self.is_image_cl = False
        self.is_tracker_cl = False
        self.is_registered = False
        
        self.last_update = 0
        self.registered_tool = []

        self.patients_dir = '..\\Patients'
        # TODO: record in the patient_dir 
        self.records_dir = ''
        self.curr_patient = None
        

        os.path.abspath

        self.patient_cls = Patient(self.ui.tableWidget_Patients, self.newPatientWindow, self.patients_dir)
        self.patient_cls.get_patients_from_db()
        self.tracker_cls = Tracker()
        self.centerline_cls = None
        self.register_cls = None

        self.regMat = np.array([[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]])
        self.R = []
        self.t = []
        self.s = []
    

    '''
    >>> ----------------------------------------
    >>> Patients ops
    >>> ----------------------------------------
    '''
    def new_patient(self):
        if self.patient_cls.new_patient():
            index = self.ui.tableWidget_Patients.model().index(self.ui.tableWidget_Patients.rowCount()-1,0)
            self.curr_patient = self.ui.tableWidget_Patients.model().data(index)
            self.new_patient = True
            self.load_patient()
            self.new_patient = False

    def load_patient(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if not self.new_patient:
            index = self.ui.tableWidget_Patients.selectionModel().selectedRows()[0]
            self.curr_patient = self.ui.tableWidget_Patients.model().data(index)
        try:
            self.patient_cls.load_patient(self.curr_patient)
            self.show_images()
            self.set_ui_elements_enabled(True)
            self.update_subPanels(self.patient_cls.dims)
            self.ui.btn_LoadPatient.hide()
            self.ui.btn_DeletePatient.hide()

            # Check and load image and tracker centerlines if available
            image_centerline_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'image_centerline.npy')
            if (os.path.exists(image_centerline_path)):
                self.patient_cls.centerline = self.read_points(image_centerline_path)
                self.is_image_cl = True
                self.ui.checkBox_showImageCenterline.show()
            tracker_centerline_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'tracker_centerline.npy')
            if (os.path.exists(tracker_centerline_path)):
                self.tracker_cls.centerline = self.read_points(tracker_centerline_path)
                self.is_tracker_cl = True
                self.ui.checkBox_showTrackerCenterline.show()
            regmat_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_matrix.npy')
            R_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_R.npy')
            t_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_t.npy')
            s_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_s.npy')
            if (os.path.exists(regmat_path)):
                self.regMat = self.load_regmat(regmat_path)
                self.regMat_inv = np.linalg.inv(self.regMat)
                self.R = self.load_regmat(R_path)
                self.t = self.load_regmat(t_path)
                self.s = self.load_regmat(s_path)

            if self.is_image_cl and self.is_tracker_cl:
                self.ui.btn_registerCenterlines.setEnabled(True)
            self.set_centerline_available_labels()
            
            QApplication.restoreOverrideCursor()
        except:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(None, 'Wrong Header', 'Can not read Image Origin from header!\nImage position might be wrong')

    def update_patient(self):
        self.patient_cls.update_patient(self.curr_patient, self.is_segmented, self.is_image_cl, self.is_tracker_cl, self.is_registered)

    def delete_patient(self):
        index = self.ui.tableWidget_Patients.selectionModel().selectedRows()[0]
        selected_patient = self.ui.tableWidget_Patients.model().data(index)
        ret = QMessageBox.question(None, 'Delete Patient',
                                    f'Do you want to delete {selected_patient} ?\nThis action is NOT reversible!',
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
        # QMessageBox.information(None, 'Comming Soon...', f'Not Implemented Yet !')
        self.ui.stackedWidget.setCurrentIndex((self.ui.stackedWidget.currentIndex()+1)%3)
        if self.ui.stackedWidget.currentIndex() == 1:
            self.remove_images_from_viewports()
            self.vtk_widget_3D.show_image(self.patient_cls.reoriented_image)
            self.vtk_widget_3D_2.show_image(self.patient_cls.reoriented_image)
            self.vtk_widget_3D_2.ren.SetActiveCamera(self.vtk_widget_3D_max.ren.GetActiveCamera())
            self.vtk_widget_2D.show_image(self.patient_cls.reoriented_image, self.patient_cls.dims, self.patient_cls.spacing, self.patient_cls.origin)
        elif self.ui.stackedWidget.currentIndex() == 2:
            self.remove_images_from_viewports()
            self.vtk_widget_3D_max.show_image(self.patient_cls.reoriented_image)
            self.vtk_widget_3D_max.ren.SetActiveCamera(self.vtk_widget_3D_2.ren.GetActiveCamera())
            size = self.ui.frame_Viewport_max.size()
            self.vtk_widget_3D_max.ren.GetRenderWindow().SetSize(size.width(),size.height())
            # self.vtk_widget_3D_max.interactor.ReInitialize()

    '''
    >>> ----------------------------------------
    >>> Tracker ops
    >>> ----------------------------------------
    '''

    def connect_tracker(self):
        if not self.tracker_cls.tracker_connected:
            splash_pix = QPixmap('ui/icons/connecting.png')
            splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
            x_pos = self.geometry().x()+self.ui.stackedWidget.x()+int((self.ui.vtk_panel_endoscope.width()-splash.width())/2)+20
            y_pos = self.geometry().y()+self.ui.vtk_panel_3D_1.height()+self.ui.SubPanel_3D.height()+int((self.ui.vtk_panel_endoscope.height()-splash.height())/2)+20
            splash.move(x_pos, y_pos)
            splash.show()
            self.ui.btn_Connect.setText('Connecting...')
            self.ui.btn_ToolsWindow.setEnabled(False)
            self.ui.btn_recordCoords.setEnabled(False)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            QApplication.processEvents()
            if self.tracker_cls.connect():
                # Multithreading Method 1 (recomended)
                thread_tracker = threading.Thread(target=self.tracker_loop)
                thread_tracker.start()

                # thread_updateViews = threading.Thread(target=self.show_tool_on_views(self.registered_tool))
                # thread_updateViews.start()

                # Multithreading Method 2 (not recomended)
                # Use QApplication.processEvents() inside the loop

                self.ui.btn_Connect.setText('Disconnect Tracker')
                self.ui.btn_ToolsWindow.setEnabled(True)
                self.ui.btn_recordCoords.setEnabled(True)
                icon = QIcon(":/icon/icons/tracker_connected.png")
                self.ui.btn_Connect.setIcon(icon)
                QApplication.restoreOverrideCursor()
                splash.close()
                # QApplication.processEvents()
            else:
                QApplication.restoreOverrideCursor()
                splash.close()
                msg = 'Please check the following:\n' \
                        '  1) NDI device connection\n' \
                        '  2) Is the NDI device switched on?!\n' \
                        '  3) Do you have sufficient privilege to connect to the device?\n' \
                        '     (e.g. on Linux are you part of the \"dialout\" group?)'
                QMessageBox.critical(self, 'Tracker Connection Failed', f'Can not connect to the tracker!\n{msg}')
                self.ui.btn_Connect.setText('Connect Tracker')
                self.ui.btn_Connect.setStyleSheet("background-color: rgb(65, 65, 65)")
                QApplication.processEvents()
        else:
            self.disconnect_tracker()

    def disconnect_tracker(self):
        if self.tracker_cls.tracker_connected:
            print('Disconnecting Tracker...')
            self.record_coords = False
            self.tracker_cls.disconnect()
            self.ui.btn_Connect.setText('Connect Tracker')
            self.ui.btn_ToolsWindow.setEnabled(False)
            icon = QIcon(":/icon/icons/tracker_disconnected.png")
            self.ui.btn_Connect.setIcon(icon)

    def tracker_loop(self):
        warmup_counter = 0

        splash_tool_shown = False
        splash_ref_shown = False
        splash_pix_ref = QPixmap('ui/icons/ref_not_detected.png')
        splash_ref = QSplashScreen(splash_pix_ref, Qt.WindowStaysOnTopHint)
        splash_pix_tool = QPixmap('ui/icons/tool_not_detected.png')
        splash_tool = QSplashScreen(splash_pix_tool, Qt.WindowStaysOnTopHint)

        x_pos = self.geometry().x()+self.ui.stackedWidget.x()+int((self.ui.vtk_panel_endoscope.width()-splash_ref.width())/2)+20
        y_pos = self.geometry().y()+self.ui.vtk_panel_3D_1.height()+self.ui.SubPanel_3D.height()+int((self.ui.vtk_panel_endoscope.height()-splash_ref.height())/2)+20
        splash_ref.move(x_pos, y_pos-int(splash_tool.height()/2))
        x_pos = self.geometry().x()+self.ui.stackedWidget.x()+int((self.ui.vtk_panel_endoscope.width()-splash_tool.width())/2)+20
        y_pos = self.geometry().y()+self.ui.vtk_panel_3D_1.height()+self.ui.SubPanel_3D.height()+int((self.ui.vtk_panel_endoscope.height()-splash_tool.height())/2)+20
        splash_tool.move(x_pos, y_pos+int(splash_ref.height()/2))

        non_vis_counter_ref = 0
        non_vis_counter_tool = 0

        while self.tracker_cls.capture_coords:
            if (self.exitting):
                break

            # if warmup_counter < 10:
            #     warmup_counter += 1
            #     time.sleep(0.1)
            #     continue

            if self.tracker_cls.tracker_connected and not self.pause_tracker_loop:
                ref_mat, tool_mat = self.tracker_cls.get_frame()
                if np.isnan(ref_mat.sum()):
                    if non_vis_counter_ref > 10:
                        if not splash_ref_shown:
                            splash_ref.show()
                            QApplication.processEvents()
                            splash_ref_shown = True
                    else:
                        non_vis_counter_ref += 1
                elif splash_ref_shown:
                    splash_ref.close()
                    QApplication.processEvents()
                    splash_ref_shown = False
                    non_vis_counter_ref = 0
                

                if np.isnan(tool_mat.sum()):
                    if non_vis_counter_tool > 10:
                        if not splash_tool_shown:
                            splash_tool.show()
                            QApplication.processEvents()
                            splash_tool_shown = True
                    else:
                        non_vis_counter_tool += 1
                elif splash_tool_shown:
                    splash_tool.close()
                    QApplication.processEvents()
                    splash_tool_shown = False
                    non_vis_counter_tool = 0

                if np.isnan(ref_mat.sum()) or np.isnan(tool_mat.sum()):
                    continue

                if (self.record_coords):
                    self.trackerRawCoords_ref.append(ref_mat) 
                    self.trackerRawCoords_tool.append(tool_mat) 

                elif self.R != []:
                    self.registered_tool = self.apply_registration(tool_mat, ref_mat)
                    self.show_tool_on_views(self.registered_tool)
                    self.toolsWindow.setData(ref_mat, tool_mat)
                # if (self.patient_cls.XyzToRas != []):
                    # # refcoords = np.swapaxes(refcoords, 0, 2)
                    # # refcoords = np.swapaxes(ref_mat, 0, 1)
                    # # toolcoords = np.swapaxes(toolcoords, 0, 2)
                    # # toolcoords = np.swapaxes(tool_mat, 0, 1)
                    # self.registered_tool = self.apply_registration(tool_mat, ref_mat)
                    # # registered_tool = np.squeeze(np.matmul(self.patient_cls.XyzToRas, registered_tool))
                    # self.show_tool_on_views(self.registered_tool)

            time.sleep(0.1)
        return
        
    def coords_record(self):
        if (not self.tracker_cls.tracker_connected) and (not self.record_coords):
            self.connect_tracker()

        if (not self.record_coords) and (self.tracker_cls.tracker_connected):
            self.pause_tracker_loop = True
            self.ui.btn_recordCoords.setEnabled(False)
            self.countdown_splash()
            self.ui.btn_recordCoords.setEnabled(True)
            self.ui.btn_recordCoords.setText(' Stop Record')
            icon = QIcon(":/icon/icons/rec_stop.png")
            self.ui.btn_recordCoords.setIcon(icon)
            self.ui.btn_recordCoords.setStyleSheet("background-color: rgba(235, 25, 75, 100)")
            QApplication.processEvents()
            self.record_coords = True
            self.pause_tracker_loop = False
        else:
            self.ui.btn_recordCoords.setText(' Start Record')
            icon = QIcon(":/icon/icons/rec_start.png")
            self.ui.btn_recordCoords.setIcon(icon)
            self.ui.btn_recordCoords.setStyleSheet("background-color: rgb(65, 65, 65)")

            ret = QMessageBox.question(self, f'Accept the Record?', 'Save and Use This Record?', QMessageBox.Ok | QMessageBox.Cancel)
            if ret == QMessageBox.Cancel:
                self.record_coords = False
                return

            # Calculate Tool2Ref (tracker centerline)
            refcoords = np.array(self.trackerRawCoords_ref)
            # refcoords = np.swapaxes(refcoords, 0, 2)
            # refcoords = np.swapaxes(refcoords, 0, 1)
            toolcoords = np.array(self.trackerRawCoords_tool)
            # toolcoords = np.swapaxes(toolcoords, 0, 2)
            # toolcoords = np.swapaxes(toolcoords, 0, 1)
            numPoints = refcoords.shape[0]
            tool2ref = np.zeros_like(refcoords)
            tool2ref = np.swapaxes(tool2ref, 0, 2)
            for ii in range(numPoints):
                    ref = refcoords[ii,:,:]
                    tool = toolcoords[ii,:,:]
                    ref_inv = np.linalg.inv(ref)
                    tool2ref[:,:,ii] = np.squeeze(np.matmul(ref_inv, tool))

            self.tracker_cls.centerline = tool2ref
            self.trackerRawCoords_ref = []
            self.trackerRawCoords_tool = []
            self.ui.checkBox_showTrackerCenterline.show()
            self.ui.checkBox_showTrackerCenterline.setChecked(True)
            self.ui.label_trackerCenterline.setText('Available')
            self.ui.label_trackerCenterline.setStyleSheet("color: rgb(100, 255, 130);")
            self.is_tracker_cl = True
            if self.is_image_cl and self.is_tracker_cl:
                self.ui.btn_registerCenterlines.setEnabled(True)
            self.update_patient()

            # Output paths
            tracker_centerline_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'tracker_centerline.npy')
            self.records_dir = os.path.join(self.patients_dir, self.curr_patient, 'Records')
            tool2ref_file = f'tracker_centerline_{str(int(time.time()))}.npy'
            refFile = f'RefPoints_{str(int(time.time()))}.npy'
            toolFile = f'ToolPoints_{str(int(time.time()))}.npy'

            # Save files
            try:
                # Save/Replace the tracker centerline
                if os.path.exists(tracker_centerline_path):
                    os.remove(tracker_centerline_path)
                np.save(tracker_centerline_path, self.tracker_cls.centerline)
                # Save tool/ref/tool2ref(tracker enterline) for each record
                if (not os.path.exists(self.records_dir)):
                    os.mkdir(self.records_dir)
                np.save(os.path.join(self.records_dir, tool2ref_file), tool2ref)
                np.save(os.path.join(self.records_dir, refFile), refcoords)
                np.save(os.path.join(self.records_dir, toolFile), toolcoords)
            except:
                QMessageBox.critical(self, f'Saving Failed!', 'Failed to save the recorded points\nPoints would not be available after closing the application.')
            finally:
                self.record_coords = False
            QMessageBox.information(self, f'Tracker Points Saved', f'Tool/Ref points saved to \"{self.records_dir}\" ')

    '''
    >>> ----------------------------------------
    >>> Viewers ops
    >>> ----------------------------------------
    '''
    def show_images(self):
        self.ui.stackedWidget.setCurrentIndex(1)
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
        # self.patient_cls.reoriented_image = self.paQVtkViewer3Dtient_cls.imgReader

        self.vtk_widget_3D.show_image(self.patient_cls.reoriented_image)
        self.vtk_widget_3D_2.show_image(self.patient_cls.reoriented_image)
        self.vtk_widget_2D.show_image(self.patient_cls.reoriented_image, self.patient_cls.dims, self.patient_cls.spacing, self.patient_cls.origin)
        self.ui.label_bronchoscopeStatus.show()

    def set_ui_elements_enabled(self, isEnabled):
        self.ui.groupBox_Viewports.setEnabled(isEnabled)
        self.ui.btn_Segment.setEnabled(isEnabled)
        self.ui.frame_imageCenterline.setEnabled(isEnabled)
        self.ui.frame_trackerCenterline.setEnabled(isEnabled)
        self.ui.btn_LoadToolPoints.setEnabled(isEnabled)

        self.ui.slider_threshold3D.setEnabled(isEnabled)
        self.ui.slider_threshold3D_2.setEnabled(isEnabled)
        self.ui.btn_ResetViewports.setEnabled(isEnabled)

    def remove_images_from_viewports(self):
        self.vtk_widget_3D.remove_image()
        self.vtk_widget_3D_2.remove_image()
        self.vtk_widget_3D_max.remove_image()
        self.vtk_widget_2D.remove_image()
        self.hide_subPanels()
        self.ui.label_bronchoscopeStatus.hide()
        
    def countdown_splash(self):
        splash_pix = QPixmap('ui/icons/5.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        x_pos = self.geometry().x()+self.ui.stackedWidget.geometry().x()+int((self.ui.vtk_panel_endoscope.width()-splash.width())/2)+20
        y_pos = self.geometry().y()+self.ui.vtk_panel_3D_1.height()+self.ui.SubPanel_3D.height()+int((self.ui.vtk_panel_endoscope.height()-splash.height())/2)+20
        splash.move(x_pos, y_pos)
        splash.show()
        # splash.showMessage("<h1><font color='orange'>Ready for record</font></h1>", Qt.AlignTop | Qt.AlignCenter, Qt.black)
        timer = QtCore.QElapsedTimer()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/4.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.move(x_pos, y_pos)
        splash.show()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/3.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.move(x_pos, y_pos)
        splash.show()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/2.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.move(x_pos, y_pos)
        splash.show()
        timer.start()
        while timer.elapsed() < 1000 :
            app.processEvents()
        splash.hide()
        splash_pix = QPixmap('ui/icons/1.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.move(x_pos, y_pos)
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
        self.ui.label_sliceNum.setNum(self.ui.Slider_2D.value()+1)
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

        # regMat_inv = np.linalg.inv(self.regMat)
        reg = np.zeros_like(toolMat)
        refMat_inv = np.linalg.inv(refMat)
        tool2ref = np.squeeze(np.matmul(refMat_inv, toolMat))
        pt_tracker = self.coord2points(tool2ref)
        # reg[0:3,3] = np.dot(pt_tracker, self.regMat[0:3,0:3])+self.regMat[:3,3]
        reg[0:3,3] = self.s * np.dot(pt_tracker, self.R) + self.t
        # self.regMat_inv = np.linalg.inv(self.regMat)
        reg[0:3,0:3] = np.dot(self.regMat_inv[0:3,0:3], tool2ref[0:3,0:3])
        # reg[0:3,0:3] = self.s * np.dot(self.R, tool2ref[0:3,0:3])
        # reg = np.squeeze(np.matmul(regMat_inv, tool2ref))
        # reg = np.squeeze(np.matmul(self.patient_cls.XyzToRas, reg))
        return reg

    def read_points(self, filepath=None):
        points = []
        if filepath == None:
            # from vtk.util.numpy_support import vtk_to_numpy
            options = QFileDialog.Options()
            # options |= QFileDialog.DontUseNativeDialog
            filepath, _ = QFileDialog.getOpenFileName(self, "Read Points from File", "",
                                                    "All Data Types (*.mat *.npy *.npz);;Matlab (*.mat);;Numpy (*.npy *.npz);;All Files (*)",
                                                    options=options)
        if filepath:
            extension = os.path.splitext(filepath)[1].lower()
            if 'mat' in extension:
                matFile = loadmat(filepath)
                # self.registered_points = matFile['EMT_cor']
                points = matFile[list(matFile)[-1]]
            elif 'np' in extension:
                points = np.load(filepath)
                points = np.squeeze(points)
        return points

    def load_image_centerline(self):
        tmp_centerline = self.read_points()
        if tmp_centerline != []:
            self.patient_cls.centerline = tmp_centerline 
            self.remove_centerline()
            self.ui.checkBox_showImageCenterline.show()
            self.ui.checkBox_showImageCenterline.setChecked(False)
            self.ui.checkBox_showImageCenterline.setChecked(True)
            self.set_centerline_available_labels()
            self.save_image_centerline()
            self.is_image_cl = True
            if self.is_image_cl and self.is_tracker_cl:
                self.ui.btn_registerCenterlines.setEnabled(True)
            self.update_patient()

    def load_tracker_centerline(self):        
        self.tracker_cls.centerline = self.read_points()
        if self.tracker_cls.centerline != []:
            self.remove_points()
            self.ui.checkBox_showTrackerCenterline.show()
            self.ui.checkBox_showTrackerCenterline.setChecked(False)
            self.ui.checkBox_showTrackerCenterline.setChecked(True)
            self.set_centerline_available_labels()
            self.save_tracker_centerline()
            self.is_tracker_cl = True
            if self.is_image_cl and self.is_tracker_cl:
                self.ui.btn_registerCenterlines.setEnabled(True)
            self.update_patient() 

    def save_image_centerline(self):
        try:
            image_centerline_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'image_centerline.npy')
            if os.path.exists(image_centerline_path):
                os.remove(image_centerline_path)
            np.save(image_centerline_path, self.patient_cls.centerline)
        except:
            QMessageBox.critical(self, 'Centerline NOT Saved', 'There was a problem saving the centerline!')
    
    def save_tracker_centerline(self):
        try:
            tracker_centerline_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'tracker_centerline.npy')
            if os.path.exists(tracker_centerline_path):
                os.remove(tracker_centerline_path)
            np.save(tracker_centerline_path, self.tracker_cls.centerline)
        except:
            QMessageBox.critical(self, 'Centerline NOT Saved', 'There was a problem saving the centerline!')

    def load_regmat(self, filepath=None):
        points = []
        if filepath == None:
            # from vtk.util.numpy_support import vtk_to_numpy
            options = QFileDialog.Options()
            # options |= QFileDialog.DontUseNativeDialog
            filepath, _ = QFileDialog.getOpenFileName(self, "Read Points from File", "",
                                                    "All Data Types (*.mat *.npy *.npz);;Matlab (*.mat);;Numpy (*.npy *.npz);;All Files (*)",
                                                    options=options)
        if filepath:
            extension = os.path.splitext(filepath)[1].lower()
            if 'mat' in extension:
                matFile = loadmat(filepath)
                # self.registered_points = matFile['EMT_cor']
                points = matFile[list(matFile)[-1]]
            elif 'np' in extension:
                points = np.load(filepath)
                points = np.squeeze(points)
        return points


    def set_centerline_available_labels(self):
        if self.is_image_cl:
            self.ui.label_imageCenterline.setText('Available')
            self.ui.label_imageCenterline.setStyleSheet("color: rgb(100, 255, 130);")
        else:
            self.ui.label_imageCenterline.setText('Not Available')
            self.ui.label_imageCenterline.setStyleSheet("color: rgb(255, 55, 120);")
        
        if self.is_tracker_cl:
            self.ui.label_trackerCenterline.setText('Available')
            self.ui.label_trackerCenterline.setStyleSheet("color: rgb(100, 255, 130);")
        else:
            self.ui.label_trackerCenterline.setText('Not Available')
            self.ui.label_trackerCenterline.setStyleSheet("color: rgb(255, 55, 120);")

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
                self.registered_points = np.zeros_like(np.array(self.tool_coords))
                pt_tracker = self.coord2points(self.tool_coords)
                # reg = self.s * np.dot(pt_tracker, self.R) + self.t
                reg = np.dot(pt_tracker, self.regMat[0:3,0:3])+self.regMat[:3,3]
                # for ref, tool in zip(self.refCoords, self.toolCoords):
                for ii in range(numPoints):
                    self.registered_points[0:3,3,ii] = reg[ii]
                    self.registered_points[0:3,0:3,ii] = self.tool_coords[0:3,0:3,ii]

                # self.registered_points = self.tool_coords
                # regMat_inv = np.linalg.inv(self.regMat)
                # for i in range(numPoints):
                #     self.registered_points[:,:,i] = np.squeeze(np.matmul(regMat_inv, self.registered_points[:,:,i] ))
                #     # self.registered_points[:,:,i] = np.squeeze(np.matmul(self.patient_cls.XyzToRas, self.registered_points[:,:,i]))
                # # self.registered_points = np.swapaxes(self.toolCoords, 1, 2)
                # # self.registered_pointsregistered_points = np.swapaxes(self.registered_points, 0, 2)

            # self.vtk_widget_3D.register(pt_tracker)

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
                self.draw_points(self.registered_points, draw_start_end=True)
            self.ui.btn_playCam.setEnabled(True)
            self.ui.slider_Frames.setEnabled(True)
            self.ui.checkBox_showPoints.setEnabled(True)
            self.ui.btn_ResetVB.setEnabled(True)

    def show_hide_points(self):
        _sender = self.sender()
        if _sender.isChecked():
            if _sender.objectName() == 'checkBox_showPoints':
                self.draw_points(self.registered_points, draw_start_end=True)
            else:
                self.show_hide_tracker_centerline()
        else:
            self.remove_points()

    def show_hide_image_centerline(self):
        if self.ui.checkBox_showImageCenterline.isChecked():
            self.draw_centerline(self.patient_cls.centerline)
        else:
            self.remove_centerline()

    def coord2points(self, coords):
        if coords.shape == (4,4):
            points = coords[:,3][:-1]
        else:
            numPoints = coords.shape[-1]
            # numPoints = len(coords)
            points = np.zeros([numPoints, 3])
            for i in range(numPoints):
                points[i,:] = coords[:,:,i][:,3][:-1]
        return points

    def show_hide_tracker_centerline(self):
        if self.ui.checkBox_showTrackerCenterline.isChecked():
            self.registered_centerline = np.zeros_like(np.array(self.tracker_cls.centerline))
            numPoints = np.array(self.tracker_cls.centerline).shape[-1]
            pt_tracker = self.coord2points(self.tracker_cls.centerline)
            # reg = self.s * np.dot(pt_tracker, self.R) + self.t
            reg = np.dot(pt_tracker, self.regMat[0:3,0:3])+self.regMat[:3,3]
            # for ref, tool in zip(self.refCoords, self.toolCoords):
            for ii in range(numPoints):
                self.registered_centerline[0:3,3,ii] = reg[ii]
            self.draw_points(self.registered_centerline)
            # self.draw_points(self.tracker_cls.centerline)
        else:
            self.remove_points()

    def register_centerlines(self):
        from ui.UiWindows import RegWindow
        regWindow = RegWindow(self)
        regWindow.setData(self.patient_cls.centerline, self.tracker_cls.centerline)
        res = regWindow.exec()
        if (res == QDialog.Accepted) and (np.array(regWindow.reg_mat).any()):
            self.regMat = regWindow.reg_mat
            self.R = regWindow.R
            self.t = regWindow.t
            self.s = regWindow.scale
            print(self.regMat)
            self.save_regmat()
            self.is_registered = True
            self.update_patient()
            self.ui.checkBox_showTrackerCenterline.setChecked(False)
            self.ui.checkBox_showTrackerCenterline.setChecked(True)

    def save_regmat(self):
        try:
            regmat_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_matrix.npy')
            if os.path.exists(regmat_path):
                os.remove(regmat_path)
            R_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_R.npy')
            if os.path.exists(R_path):
                os.remove(R_path)
            t_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_t.npy')
            if os.path.exists(t_path):
                os.remove(t_path)
            s_path = os.path.join(self.patient_cls.patients_dir, self.curr_patient, 'registration_s.npy')
            if os.path.exists(s_path):
                os.remove(s_path)
            np.save(regmat_path, self.regMat)
            np.save(R_path, self.R)
            np.save(t_path, self.t)
            np.save(s_path, self.s)
        except:
            QMessageBox.critical(self, 'Centerline NOT Saved', 'There was a problem saving the centerline!')

    def draw_points(self, points, draw_start_end=False):
        self.vtk_widget_3D.draw_points(points)
        # if draw_start_end:
        #     self.vtk_widget_3D.add_start_point(points[:,:,0]) # start point
        #     self.vtk_widget_3D.add_end_point(points[:,:,-1]) # end point

        self.vtk_widget_3D_2.draw_points(points)
        # if draw_start_end:
        #     self.vtk_widget_3D_2.add_start_point(points[:,:,0]) # start point
        #     self.vtk_widget_3D_2.add_end_point(points[:,:,-1]) # end point
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
        if (np.isnan(tool_mat).any()):
            return
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

        # if self.vtk_widget_2D.cross != None:
        #     self.vtk_widget_2D.remove_cross()
        #     if (self.tracker_cls.tracker_connected):
        #         self.show_tool_on_views(self.registered_tool)
        #     else:
        #         self.show_tool_on_views(self.cam_pos)

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
        self.vtk_widget_3D_2.remove_cross()
        self.vtk_widget_2D.remove_cross()
        self.registered_points = []
        self.registered_centerline = []
        self.ref_coords = []
        self.tool_coords == []

    def extract_centerline(self):
        if self.centerline_cls != None:
            del self.centerline_cls
        self.centerline_cls = Centerline(self.patient_cls.image_path)

        tmp_centerline = self.centerline_cls.extract()
        if tmp_centerline != []:
            self.patient_cls.centerline = tmp_centerline
            self.is_image_cl = True
            self.ui.checkBox_showImageCenterline.show()
            self.ui.checkBox_showImageCenterline.setChecked(True)
            if self.is_image_cl and self.is_tracker_cl:
                    self.ui.btn_registerCenterlines.setEnabled(True)
            self.save_image_centerline()
            self.update_patient()

    def setup(self, size):
        self.ui = MainWin.Ui_MainWin()
        self.ui.setupUi(self)
        # sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.resize(sizeObject.width(), sizeObject.height())
        # self.resize(size.width(), size.height())

        self.ui.btn_NewPatient.clicked.connect(self.new_patient)
        self.ui.btn_LoadPatient.clicked.connect(self.load_patient)
        self.ui.btn_DeletePatient.clicked.connect(self.delete_patient)
        self.ui.btn_ImportPatient.clicked.connect(self.import_patient)
        self.ui.btn_ClearPatients.clicked.connect(self.clear_patients)

        self.ui.Slider_2D.valueChanged.connect(self.slider_changed)

        self.ui.btn_LoadToolPoints.clicked.connect(self.read_tool_points)
        self.ui.checkBox_showPoints.stateChanged.connect(self.show_hide_points)
        self.ui.checkBox_showImageCenterline.stateChanged.connect(self.show_hide_image_centerline)
        self.ui.checkBox_showTrackerCenterline.stateChanged.connect(self.show_hide_points)
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

        self.ui.btn_extractCenterline.clicked.connect(self.extract_centerline)
        self.ui.btn_loadImageCenterline.clicked.connect(self.load_image_centerline)
        self.ui.btn_recordCoords.clicked.connect(self.coords_record)
        self.ui.btn_loadtrackerCenterline.clicked.connect(self.load_tracker_centerline)
        self.ui.btn_registerCenterlines.clicked.connect(self.register_centerlines)

        self.ui.stackedWidget.setCurrentIndex(0)

        self.vtk_widget_3D = QVtkViewer3D(self.ui.vtk_panel_3D_1, size, 'Virtual', False)
        self.vtk_widget_3D_2 = QVtkViewer3D(self.ui.vtk_panel_3D_2, size, 'Normal', False)
        self.vtk_widget_3D_max = QVtkViewer3D(self.ui.vtk_panel_3D_max, size, '3D', True)

        layout_3D = QVBoxLayout()
        layout_3D.addWidget(self.vtk_widget_3D, 0, Qt.AlignCenter)
        self.ui.vtk_panel_3D_1.setLayout(layout_3D)

        layout_3D_2 = QVBoxLayout()
        layout_3D_2.addWidget(self.vtk_widget_3D_2, 0, Qt.AlignCenter)
        self.ui.vtk_panel_3D_2.setLayout(layout_3D_2)

        layout_3D_max = QVBoxLayout()
        layout_3D_max.addWidget(self.vtk_widget_3D_max, 0, Qt.AlignCenter)
        self.ui.vtk_panel_3D_max.setLayout(layout_3D_max)

        self.toolsWindow = ToolsWindow(self)
        self.regMatWindow = RegMatWindow(self)
        self.newPatientWindow = NewPatientWindow(self)

        self.set_ui_elements_enabled(False)
        self.ui.btn_LoadPatient.hide()
        self.ui.btn_DeletePatient.hide()
        self.ui.checkBox_showImageCenterline.hide()
        self.ui.checkBox_showTrackerCenterline.hide()
        self.ui.toolBar.hide()
        self.ui.label_bronchoscopeStatus.hide()

        self.ui.tabWidget.setCurrentIndex(0)

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
        self.vtk_widget_2D = QVtkViewer2D(self.ui.vtk_panel_2D, size, viewType, False)

        layout_2D = QVBoxLayout()
        layout_2D.addWidget(self.vtk_widget_2D, 0, Qt.AlignCenter)
        self.ui.vtk_panel_2D.setLayout(layout_2D)

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
    size.setHeight(size.height()-110)
    main_win = MainWindow(size)
    main_win.showMaximized()
    # main_win.show()
    # main_win.initialize()

    # if main_win.tracker_connected == True:
    #     main_win.disconnect_tracker()
    sys.exit(app.exec())
