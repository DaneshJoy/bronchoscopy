# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RegWin.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RegWin(object):
    def setupUi(self, RegWin):
        RegWin.setObjectName("RegWin")
        RegWin.setWindowModality(QtCore.Qt.NonModal)
        RegWin.resize(877, 644)
        RegWin.setStyleSheet("background-color: rgb(65, 65, 65);")
        self.verticalLayout = QtWidgets.QVBoxLayout(RegWin)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_main = QtWidgets.QFrame(RegWin)
        self.frame_main.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_main.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_main.setObjectName("frame_main")
        self.verticalLayout.addWidget(self.frame_main)
        self.progressBar = QtWidgets.QProgressBar(RegWin)
        self.progressBar.setMinimumSize(QtCore.QSize(0, 30))
        self.progressBar.setMaximum(0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.btn_start = QtWidgets.QPushButton(RegWin)
        self.btn_start.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.btn_start.setFont(font)
        self.btn_start.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_start.setStyleSheet("color: rgb(110, 255, 251);")
        self.btn_start.setObjectName("btn_start")
        self.verticalLayout.addWidget(self.btn_start)
        self.buttonBox = QtWidgets.QDialogButtonBox(RegWin)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBox.setStyleSheet("color: rgb(170, 255, 255);")
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(0, 2)
        self.verticalLayout.setStretch(1, 2)
        self.verticalLayout.setStretch(2, 3)
        self.verticalLayout.setStretch(3, 1)

        self.retranslateUi(RegWin)
        self.buttonBox.accepted.connect(RegWin.accept)
        self.buttonBox.rejected.connect(RegWin.reject)
        QtCore.QMetaObject.connectSlotsByName(RegWin)

    def retranslateUi(self, RegWin):
        _translate = QtCore.QCoreApplication.translate
        RegWin.setWindowTitle(_translate("RegWin", "Registration"))
        self.btn_start.setText(_translate("RegWin", "Start"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    RegWin = QtWidgets.QDialog()
    ui = Ui_RegWin()
    ui.setupUi(RegWin)
    RegWin.show()
    sys.exit(app.exec_())
