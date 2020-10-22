# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 16:05:45 2020

@author: Saeed
"""

import os
import threading
import numpy as np
import vtk
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QDialog, QMessageBox
from .patients_db import PatientsDB


class Patients():
    def __init__(self, tableWidget_Patients, newPatientWindow, patients_dir):
        super().__init__()
        self.XyzToRas = []
        self.tableWidget_Patients = tableWidget_Patients
        self.newPatientWindow = newPatientWindow
        self.patients_dir = patients_dir
        self.db = PatientsDB()

    def getPatientsFromDB(self):
        self.tableWidget_Patients.setEditTriggers(QAbstractItemView.NoEditTriggers)
        if (not os.path.exists(self.patients_dir)):
            os.mkdir(self.patients_dir)
        self.db_connection = self.db.db_createConnection(os.path.join(self.patients_dir, 'patients.db'))
        patients = self.db.db_getPatients(self.db_connection)
        print(len(patients))
        for p in patients:
            self.addPatientRow([p[1], p[2]])

    def addPatientRow(self, row_data):
        row = self.tableWidget_Patients.rowCount()
        self.tableWidget_Patients.setRowCount(row+1)
        col = 0
        for item in row_data:
            cell = QTableWidgetItem(str(item))
            self.tableWidget_Patients.setItem(row, col, cell)
            col += 1
    
    def newPatient(self):
        p_num = self.tableWidget_Patients.rowCount()
        p_name = f'Patient_{p_num+1}'
        self.newPatientWindow.prepare(p_name)
        res = self.newPatientWindow.exec()
        if (res == QDialog.Accepted):
            _name, _date, _image = self.newPatientWindow.getData()
            self.db.db_addPatient(self.db_connection, [_name, _date, _image, 0, 0, 0])
            self.addPatientRow([_name, _date])
            thread_img = threading.Thread(target=self.loadImage(os.path.join(self.patients_dir, _name, _image+'.nii.gz')))
            thread_img.start()

    def loadImage(self, fileName):
        extension = os.path.splitext(fileName)[1].lower()
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
            _QMatrix = reader.GetQFormMatrix()
            # self.origin = (0, 0, 0)
            self.origin = (-_QMatrix.GetElement(0,3), -_QMatrix.GetElement(1,3), _QMatrix.GetElement(2,3))
            imageInfo = vtk.vtkImageChangeInformation()
            imageInfo.SetOutputOrigin(self.origin)
            imageInfo.SetInputConnection(reader.GetOutputPort())
            self.imgReader = imageInfo
        else:
            # origin = (140, 140, -58)
            # imageInfo = vtk.vtkImageChangeInformation()
            # imageInfo.SetOutputOrigin(self.origin)
            # imageInfo.SetInputConnection(reader.GetOutputPort())
            # self.showImages(imageInfo, self.dims)
            self.imgReader = reader
        
    def loadPatient(self, selected_patient):
        patient_in_db = self.db.db_getPatient(self.db_connection, selected_patient)
        selected_image = patient_in_db[0][3] + '.nii.gz'
        thread_img = threading.Thread(target=self.loadImage(os.path.join(self.patients_dir, selected_patient, selected_image)))
        thread_img.start()
        self.tableWidget_Patients.clearSelection()

    def removePatientDir(self, patient_dir):
        pdir = os.path.join(self.patients_dir, patient_dir)
        if os.path.exists(pdir):
            for root, dirs, files in os.walk(pdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(pdir)

    def deletePatient(self, selected_patient):
        removed = False
        try:
            self.db.db_deletePatient(self.db_connection, selected_patient)
            self.removePatientDir(selected_patient)
            removed = True
        except:
            pass
        return removed

    def clearPatients(self):
        self.db.db_deleteAllPatients(self.db_connection)
        for d in os.listdir(self.patients_dir):
            if os.path.isdir(os.path.join(self.patients_dir, d)):
                self.removePatientDir(d)
        # Clear table Method1
        self.tableWidget_Patients.setRowCount(0)
        # # Clear table Method2
        # self.ui.tableWidget_Patients.clearContents()
        # self.ui.tableWidget_Patients.model().removeRows(0, self.ui.tableWidget_Patients.rowCount())
        