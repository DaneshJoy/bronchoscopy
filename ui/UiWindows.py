# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 23:06:25 2020

@author: Saeed
"""

from PyQt5.Qt import QDialog
from PyQt5.QtWidgets import QTableWidgetItem
import numpy as np
from ui import ToolsWin, RegMatWin


class RegMatWindow(QDialog):
    def __init__(self, parent=None):
        super(RegMatWindow, self).__init__(parent)
    
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
        super(ToolsWindow, self).__init__(parent)

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

    # TODO: On close, set a flag to false

    # def initialize(self):
    #     pass