# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\PyHub\json-viewer\ui_res\json_win.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.json_view = QtWidgets.QTreeWidget(self.centralwidget)
        self.json_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.json_view.setObjectName("json_view")
        self.verticalLayout.addWidget(self.json_view)
        self.test_btn = QtWidgets.QPushButton(self.centralwidget)
        self.test_btn.setObjectName("test_btn")
        self.verticalLayout.addWidget(self.test_btn)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.json_view.headerItem().setText(0, _translate("MainWindow", "key"))
        self.json_view.headerItem().setText(1, _translate("MainWindow", "value"))
        self.json_view.headerItem().setText(2, _translate("MainWindow", "type"))
        self.json_view.headerItem().setText(3, _translate("MainWindow", "uid"))
        self.test_btn.setText(_translate("MainWindow", "Dump"))
