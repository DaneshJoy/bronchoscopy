# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RegMatWin.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RegMatWin(object):
    def setupUi(self, RegMatWin):
        RegMatWin.setObjectName("RegMatWin")
        RegMatWin.setWindowModality(QtCore.Qt.NonModal)
        RegMatWin.resize(500, 300)
        RegMatWin.setMinimumSize(QtCore.QSize(500, 300))
        RegMatWin.setMaximumSize(QtCore.QSize(500, 300))
        RegMatWin.setStyleSheet("background-color: rgb(65, 65, 65);")
        self.verticalLayout = QtWidgets.QVBoxLayout(RegMatWin)
        self.verticalLayout.setObjectName("verticalLayout")
        self.table_regMat = QtWidgets.QTableWidget(RegMatWin)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table_regMat.sizePolicy().hasHeightForWidth())
        self.table_regMat.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.table_regMat.setFont(font)
        self.table_regMat.setStyleSheet("color: rgb(170, 255, 255);")
        self.table_regMat.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.table_regMat.setFrameShadow(QtWidgets.QFrame.Plain)
        self.table_regMat.setLineWidth(1)
        self.table_regMat.setMidLineWidth(0)
        self.table_regMat.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_regMat.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_regMat.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table_regMat.setAutoScroll(True)
        self.table_regMat.setAlternatingRowColors(False)
        self.table_regMat.setGridStyle(QtCore.Qt.SolidLine)
        self.table_regMat.setObjectName("table_regMat")
        self.table_regMat.setColumnCount(4)
        self.table_regMat.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(0, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(1, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(1, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(2, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(2, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(3, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(3, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(3, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_regMat.setItem(3, 3, item)
        self.table_regMat.horizontalHeader().setVisible(False)
        self.table_regMat.horizontalHeader().setDefaultSectionSize(117)
        self.table_regMat.horizontalHeader().setMinimumSectionSize(10)
        self.table_regMat.verticalHeader().setVisible(False)
        self.table_regMat.verticalHeader().setDefaultSectionSize(60)
        self.table_regMat.verticalHeader().setMinimumSectionSize(10)
        self.verticalLayout.addWidget(self.table_regMat)
        self.buttonBox = QtWidgets.QDialogButtonBox(RegMatWin)
        self.buttonBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBox.setStyleSheet("color: rgb(170, 255, 255);")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(RegMatWin)
        self.buttonBox.accepted.connect(RegMatWin.accept)
        self.buttonBox.rejected.connect(RegMatWin.reject)
        QtCore.QMetaObject.connectSlotsByName(RegMatWin)

    def retranslateUi(self, RegMatWin):
        _translate = QtCore.QCoreApplication.translate
        RegMatWin.setWindowTitle(_translate("RegMatWin", "RegMat"))
        __sortingEnabled = self.table_regMat.isSortingEnabled()
        self.table_regMat.setSortingEnabled(False)
        item = self.table_regMat.item(0, 0)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(0, 1)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(0, 2)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(0, 3)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(1, 0)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(1, 1)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(1, 2)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(1, 3)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(2, 0)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(2, 1)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(2, 2)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(2, 3)
        item.setText(_translate("RegMatWin", "-"))
        item = self.table_regMat.item(3, 0)
        item.setText(_translate("RegMatWin", "0"))
        item = self.table_regMat.item(3, 1)
        item.setText(_translate("RegMatWin", "0"))
        item = self.table_regMat.item(3, 2)
        item.setText(_translate("RegMatWin", "0"))
        item = self.table_regMat.item(3, 3)
        item.setText(_translate("RegMatWin", "1"))
        self.table_regMat.setSortingEnabled(__sortingEnabled)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    RegMatWin = QtWidgets.QDialog()
    ui = Ui_RegMatWin()
    ui.setupUi(RegMatWin)
    RegMatWin.show()
    sys.exit(app.exec_())
