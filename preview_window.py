# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preview_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1115, 632)
        font = QtGui.QFont()
        font.setFamily("更纱黑体 UI HC Medium")
        Form.setFont(font)
        self.reclist_textbrowser = QtWidgets.QTextBrowser(Form)
        self.reclist_textbrowser.setGeometry(QtCore.QRect(30, 90, 331, 441))
        self.reclist_textbrowser.setObjectName("reclist_textbrowser")
        self.oto_textbrowser = QtWidgets.QTextBrowser(Form)
        self.oto_textbrowser.setGeometry(QtCore.QRect(400, 90, 681, 441))
        self.oto_textbrowser.setObjectName("oto_textbrowser")
        self.reclist_label = QtWidgets.QLabel(Form)
        self.reclist_label.setGeometry(QtCore.QRect(30, 30, 131, 61))
        font = QtGui.QFont()
        font.setFamily("更纱黑体 UI HC Medium")
        font.setPointSize(20)
        self.reclist_label.setFont(font)
        self.reclist_label.setAcceptDrops(False)
        self.reclist_label.setObjectName("reclist_label")
        self.oto_label = QtWidgets.QLabel(Form)
        self.oto_label.setGeometry(QtCore.QRect(400, 30, 91, 61))
        font = QtGui.QFont()
        font.setFamily("更纱黑体 UI HC Medium")
        font.setPointSize(20)
        self.oto_label.setFont(font)
        self.oto_label.setAcceptDrops(False)
        self.oto_label.setObjectName("oto_label")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(980, 570, 101, 41))
        font = QtGui.QFont()
        font.setFamily("更纱黑体 UI HC Medium")
        font.setPointSize(12)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.info_label = QtWidgets.QLabel(Form)
        self.info_label.setGeometry(QtCore.QRect(30, 570, 791, 41))
        font = QtGui.QFont()
        font.setFamily("更纱黑体 UI HC Medium")
        font.setPointSize(10)
        self.info_label.setFont(font)
        self.info_label.setText("")
        self.info_label.setObjectName("info_label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.reclist_label.setText(_translate("Form", "Reclist"))
        self.oto_label.setText(_translate("Form", "oto"))
        self.pushButton_2.setText(_translate("Form", "确认生成"))