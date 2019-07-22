# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 01:09:45 2019

@author: Saeed
"""

import os
import sys
import vtk
from PyQt5.Qt import QApplication, QMainWindow, QColor, Qt
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtGui import QPalette

from QVtkViewer import QVtkViewer3D, QVtkViewer2D


class MainWindow(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.vtk_widget_3D = None
        self.vtk_widget_axial = None
        self.vtk_widget_coronal = None
        self.vtk_widget_sagittal = None
        self.ui = None
        self.setup(size)

        self.ui.actionOpen.triggered.connect(self.openFileDialog)

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Medical Image", "", "Meta (*.mhd);;Nifti (*.nii;*.nii.gz);;All Files (*)", options=options)
        # QMessageBox.information(self, 'Test Message', fileName)
        if fileName:
            reader = vtk.vtkMetaImageReader()
            reader.SetFileName(fileName)
            reader.Update()
            self.vtk_widget_3D.showImage(reader)
            self.vtk_widget_axial.showImage(reader, 'axial')
            self.vtk_widget_coronal.showImage(reader, 'coronal')
            self.vtk_widget_sagittal.showImage(reader, 'sagittal')

    def setup(self, size):
        import MainWindow
        self.ui = MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        # sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.resize(sizeObject.width(), sizeObject.height())
        # self.resize(size.width(), size.height())
        self.vtk_widget_3D = QVtkViewer3D(self.ui.vtk_panel_3D, size)
        self.vtk_widget_axial = QVtkViewer2D(self.ui.vtk_panel_axial, size)
        self.vtk_widget_coronal = QVtkViewer2D(self.ui.vtk_panel_coronal, size)
        self.vtk_widget_sagittal = QVtkViewer2D(self.ui.vtk_panel_sagittal, size)

    def initialize(self):
        pass

if __name__ == "__main__":
    # # ReCompile Ui
    # os.chdir(os.path.dirname(__file__))
    # with open("MainWindow.ui") as ui_file:
    #     with open("MainWindow.py", "w") as py_ui_file:
    #         uic.compileUi(ui_file, py_ui_file, execute=True)

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
