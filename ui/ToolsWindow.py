# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ToolsWindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ToolsWindow(object):
    def setupUi(self, ToolsWindow):
        ToolsWindow.setObjectName("ToolsWindow")
        ToolsWindow.resize(561, 355)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 106, 106))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(88, 88, 88))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(47, 47, 47))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 106, 106))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(88, 88, 88))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(47, 47, 47))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 106, 106))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(88, 88, 88))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(47, 47, 47))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 35, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        ToolsWindow.setPalette(palette)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ToolsWindow)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(ToolsWindow)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_33 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_33.setFont(font)
        self.label_33.setObjectName("label_33")
        self.verticalLayout_4.addWidget(self.label_33)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.r13_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r13_tool.setFont(font)
        self.r13_tool.setObjectName("r13_tool")
        self.gridLayout.addWidget(self.r13_tool, 0, 2, 1, 1)
        self.r11_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r11_tool.setFont(font)
        self.r11_tool.setObjectName("r11_tool")
        self.gridLayout.addWidget(self.r11_tool, 0, 0, 1, 1)
        self.r12_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r12_tool.setFont(font)
        self.r12_tool.setObjectName("r12_tool")
        self.gridLayout.addWidget(self.r12_tool, 0, 1, 1, 1)
        self.t1_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.t1_tool.setFont(font)
        self.t1_tool.setStyleSheet("color: rgb(85, 255, 255);")
        self.t1_tool.setObjectName("t1_tool")
        self.gridLayout.addWidget(self.t1_tool, 0, 3, 1, 1)
        self.r21_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r21_tool.setFont(font)
        self.r21_tool.setObjectName("r21_tool")
        self.gridLayout.addWidget(self.r21_tool, 1, 0, 1, 1)
        self.r23_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r23_tool.setFont(font)
        self.r23_tool.setObjectName("r23_tool")
        self.gridLayout.addWidget(self.r23_tool, 1, 2, 1, 1)
        self.r32_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r32_tool.setFont(font)
        self.r32_tool.setObjectName("r32_tool")
        self.gridLayout.addWidget(self.r32_tool, 2, 1, 1, 1)
        self.r33_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r33_tool.setFont(font)
        self.r33_tool.setObjectName("r33_tool")
        self.gridLayout.addWidget(self.r33_tool, 2, 2, 1, 1)
        self.r22_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r22_tool.setFont(font)
        self.r22_tool.setObjectName("r22_tool")
        self.gridLayout.addWidget(self.r22_tool, 1, 1, 1, 1)
        self.t2_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.t2_tool.setFont(font)
        self.t2_tool.setStyleSheet("color: rgb(85, 255, 255);")
        self.t2_tool.setObjectName("t2_tool")
        self.gridLayout.addWidget(self.t2_tool, 1, 3, 1, 1)
        self.t3_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.t3_tool.setFont(font)
        self.t3_tool.setStyleSheet("color: rgb(85, 255, 255);")
        self.t3_tool.setObjectName("t3_tool")
        self.gridLayout.addWidget(self.t3_tool, 2, 3, 1, 1)
        self.r31_tool = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r31_tool.setFont(font)
        self.r31_tool.setObjectName("r31_tool")
        self.gridLayout.addWidget(self.r31_tool, 2, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_13.setFont(font)
        self.label_13.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 3, 0, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_16.setFont(font)
        self.label_16.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 3, 3, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_15.setFont(font)
        self.label_15.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 3, 2, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_14.setFont(font)
        self.label_14.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 3, 1, 1, 1)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.verticalLayout_4.addLayout(self.gridLayout)
        self.verticalLayout_4.setStretch(1, 6)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_34 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_34.setFont(font)
        self.label_34.setObjectName("label_34")
        self.verticalLayout_3.addWidget(self.label_34)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.r12_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r12_ref.setFont(font)
        self.r12_ref.setObjectName("r12_ref")
        self.gridLayout_2.addWidget(self.r12_ref, 0, 1, 1, 1)
        self.r23_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r23_ref.setFont(font)
        self.r23_ref.setObjectName("r23_ref")
        self.gridLayout_2.addWidget(self.r23_ref, 1, 2, 1, 1)
        self.t2_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.t2_ref.setFont(font)
        self.t2_ref.setStyleSheet("color: rgb(85, 255, 255);")
        self.t2_ref.setObjectName("t2_ref")
        self.gridLayout_2.addWidget(self.t2_ref, 1, 3, 1, 1)
        self.r32_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r32_ref.setFont(font)
        self.r32_ref.setObjectName("r32_ref")
        self.gridLayout_2.addWidget(self.r32_ref, 2, 1, 1, 1)
        self.r11_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r11_ref.setFont(font)
        self.r11_ref.setObjectName("r11_ref")
        self.gridLayout_2.addWidget(self.r11_ref, 0, 0, 1, 1)
        self.r21_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r21_ref.setFont(font)
        self.r21_ref.setObjectName("r21_ref")
        self.gridLayout_2.addWidget(self.r21_ref, 1, 0, 1, 1)
        self.r33_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r33_ref.setFont(font)
        self.r33_ref.setObjectName("r33_ref")
        self.gridLayout_2.addWidget(self.r33_ref, 2, 2, 1, 1)
        self.t3_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.t3_ref.setFont(font)
        self.t3_ref.setStyleSheet("color: rgb(85, 255, 255);")
        self.t3_ref.setObjectName("t3_ref")
        self.gridLayout_2.addWidget(self.t3_ref, 2, 3, 1, 1)
        self.r22_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r22_ref.setFont(font)
        self.r22_ref.setObjectName("r22_ref")
        self.gridLayout_2.addWidget(self.r22_ref, 1, 1, 1, 1)
        self.r31_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r31_ref.setFont(font)
        self.r31_ref.setObjectName("r31_ref")
        self.gridLayout_2.addWidget(self.r31_ref, 2, 0, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_27.setFont(font)
        self.label_27.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_27.setObjectName("label_27")
        self.gridLayout_2.addWidget(self.label_27, 3, 0, 1, 1)
        self.label_30 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_30.setFont(font)
        self.label_30.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_30.setObjectName("label_30")
        self.gridLayout_2.addWidget(self.label_30, 3, 3, 1, 1)
        self.t1_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.t1_ref.setFont(font)
        self.t1_ref.setStyleSheet("color: rgb(85, 255, 255);")
        self.t1_ref.setObjectName("t1_ref")
        self.gridLayout_2.addWidget(self.t1_ref, 0, 3, 1, 1)
        self.label_28 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_28.setFont(font)
        self.label_28.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_28.setObjectName("label_28")
        self.gridLayout_2.addWidget(self.label_28, 3, 1, 1, 1)
        self.r13_ref = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.r13_ref.setFont(font)
        self.r13_ref.setObjectName("r13_ref")
        self.gridLayout_2.addWidget(self.r13_ref, 0, 2, 1, 1)
        self.label_29 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_29.setFont(font)
        self.label_29.setStyleSheet("color: rgb(158, 158, 158);")
        self.label_29.setObjectName("label_29")
        self.gridLayout_2.addWidget(self.label_29, 3, 2, 1, 1)
        self.gridLayout_2.setRowStretch(0, 1)
        self.gridLayout_2.setRowStretch(1, 1)
        self.gridLayout_2.setRowStretch(2, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.verticalLayout_3.setStretch(1, 6)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QtWidgets.QDialogButtonBox(ToolsWindow)
        self.buttonBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBox.setStyleSheet("background-color: rgb(65, 65, 65);\n"
"color: rgb(236, 236, 236);")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(ToolsWindow)
        self.buttonBox.accepted.connect(ToolsWindow.accept)
        self.buttonBox.rejected.connect(ToolsWindow.reject)
        QtCore.QMetaObject.connectSlotsByName(ToolsWindow)

    def retranslateUi(self, ToolsWindow):
        _translate = QtCore.QCoreApplication.translate
        ToolsWindow.setWindowTitle(_translate("ToolsWindow", "Tool/Ref Coordinates"))
        self.label_33.setText(_translate("ToolsWindow", "Tool"))
        self.r13_tool.setText(_translate("ToolsWindow", "-"))
        self.r11_tool.setText(_translate("ToolsWindow", "-"))
        self.r12_tool.setText(_translate("ToolsWindow", "-"))
        self.t1_tool.setText(_translate("ToolsWindow", "-"))
        self.r21_tool.setText(_translate("ToolsWindow", "-"))
        self.r23_tool.setText(_translate("ToolsWindow", "-"))
        self.r32_tool.setText(_translate("ToolsWindow", "-"))
        self.r33_tool.setText(_translate("ToolsWindow", "-"))
        self.r22_tool.setText(_translate("ToolsWindow", "-"))
        self.t2_tool.setText(_translate("ToolsWindow", "-"))
        self.t3_tool.setText(_translate("ToolsWindow", "-"))
        self.r31_tool.setText(_translate("ToolsWindow", "-"))
        self.label_13.setText(_translate("ToolsWindow", "0"))
        self.label_16.setText(_translate("ToolsWindow", "1"))
        self.label_15.setText(_translate("ToolsWindow", "0"))
        self.label_14.setText(_translate("ToolsWindow", "0"))
        self.label_34.setText(_translate("ToolsWindow", "Reference"))
        self.r12_ref.setText(_translate("ToolsWindow", "-"))
        self.r23_ref.setText(_translate("ToolsWindow", "-"))
        self.t2_ref.setText(_translate("ToolsWindow", "-"))
        self.r32_ref.setText(_translate("ToolsWindow", "-"))
        self.r11_ref.setText(_translate("ToolsWindow", "-"))
        self.r21_ref.setText(_translate("ToolsWindow", "-"))
        self.r33_ref.setText(_translate("ToolsWindow", "-"))
        self.t3_ref.setText(_translate("ToolsWindow", "-"))
        self.r22_ref.setText(_translate("ToolsWindow", "-"))
        self.r31_ref.setText(_translate("ToolsWindow", "-"))
        self.label_27.setText(_translate("ToolsWindow", "0"))
        self.label_30.setText(_translate("ToolsWindow", "1"))
        self.t1_ref.setText(_translate("ToolsWindow", "-"))
        self.label_28.setText(_translate("ToolsWindow", "0"))
        self.r13_ref.setText(_translate("ToolsWindow", "-"))
        self.label_29.setText(_translate("ToolsWindow", "0"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ToolsWindow = QtWidgets.QDialog()
    ui = Ui_ToolsWindow()
    ui.setupUi(ToolsWindow)
    ToolsWindow.show()
    sys.exit(app.exec_())
