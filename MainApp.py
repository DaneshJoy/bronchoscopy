# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 01:09:45 2019

@author: Saeed
"""

import os
import sys
import vtk
from PyQt5.Qt import QApplication, QMainWindow
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog

from QVtkViewer import QVtkViewer3D, QVtkViewer2D


class MainWindow(QMainWindow):
    def __init__(self, data, size):
        super().__init__()
        self.vtk_widget_3D = None
        self.vtk_widget_axial = None
        self.vtk_widget_coronal = None
        self.vtk_widget_sagittal = None
        self.ui = None
        self.setup(data, size)

        self.ui.actionOpen.triggered.connect(self.openFileDialog)

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Medical Image", "", "Meta (*.mhd);;Nifti (*.nii;*.nii.gz);;All Files (*)", options=options)
        # QMessageBox.information(self, 'Test Message', fileName)
        reader = vtk.vtkMetaImageReader()
        reader.SetFileName(fileName)
        reader.Update()
        self.vtk_widget_3D.showImage(reader)
        self.vtk_widget_axial.showImage(reader, 'axial')
        self.vtk_widget_coronal.showImage(reader, 'coronal')
        self.vtk_widget_sagittal.showImage(reader, 'sagittal')

        # self.vtk_widget_3D.start()
        # self.vtk_widget_axial.start()
        # self.vtk_widget_coronal.start()
        # self.vtk_widget_sagittal.start()

        # self.vtk_widget_3D.update()
        # self.vtk_widget_axial.update()
        # self.vtk_widget_coronal.update()
        # self.vtk_widget_sagittal.update()

    def setup(self, data, size):
        import MainWindow
        # reader = vtk.vtkMetaImageReader()
        # reader.SetFileName(data)
        # reader.Update()
        self.ui = MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        # sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.resize(sizeObject.width(), sizeObject.height())
        # self.resize(size.width(), size.height())
        self.vtk_widget_3D = QVtkViewer3D(self.ui.vtk_panel_3D)
        self.vtk_widget_axial = QVtkViewer2D(self.ui.vtk_panel_axial)
        self.vtk_widget_coronal = QVtkViewer2D(self.ui.vtk_panel_coronal)
        self.vtk_widget_sagittal = QVtkViewer2D(self.ui.vtk_panel_sagittal)

        # self.ui.vtk_layout = QtWidgets.QVBoxLayout()
        # self.ui.vtk_layout.addWidget(self.vtk_widget_3D)
        # self.ui.vtk_layout.setContentsMargins(0, 0, 0, 0)
        # self.vtk_widget_3D.setLayout(self.ui.vtk_layout)

    def initialize(self):
        pass
        # self.vtk_widget_3D.start()
        # self.vtk_widget_axial.start()
        # self.vtk_widget_coronal.start()
        # self.vtk_widget_sagittal.start()

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    # ReCompile Ui
    with open("MainWindow.ui") as ui_file:
        with open("MainWindow.py", "w") as py_ui_file:
            uic.compileUi(ui_file, py_ui_file, execute=True)

    app = QApplication([])
    screen = app.primaryScreen()
    size = screen.availableGeometry()  # size.height(), size.width()
    main_win = MainWindow("FullHead.mhd", size)
    main_win.showMaximized()
    # main_win.show()
    # main_win.initialize()
    sys.exit(app.exec())
