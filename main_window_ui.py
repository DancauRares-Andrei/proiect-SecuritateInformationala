# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Interface.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1081, 510)
        self.label_cheie = QtWidgets.QLabel(Dialog)
        self.label_cheie.setGeometry(QtCore.QRect(30, 10, 161, 20))
        self.label_cheie.setObjectName("label_cheie")
        self.pushButton_evaluare_performante = QtWidgets.QPushButton(Dialog)
        self.pushButton_evaluare_performante.setGeometry(QtCore.QRect(720, 480, 341, 28))
        self.pushButton_evaluare_performante.setObjectName("pushButton_evaluare_performante")
        self.listWidget_framework = QtWidgets.QListWidget(Dialog)
        self.listWidget_framework.setGeometry(QtCore.QRect(810, 30, 181, 91))
        self.listWidget_framework.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.SelectedClicked)
        self.listWidget_framework.setProperty("showDropIndicator", False)
        self.listWidget_framework.setObjectName("listWidget_framework")
        self.labelAlgo = QtWidgets.QLabel(Dialog)
        self.labelAlgo.setGeometry(QtCore.QRect(530, 10, 131, 16))
        self.labelAlgo.setObjectName("labelAlgo")
        self.label_fisier = QtWidgets.QLabel(Dialog)
        self.label_fisier.setGeometry(QtCore.QRect(10, 250, 131, 16))
        self.label_fisier.setObjectName("label_fisier")
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(280, 60, 232, 141))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_add_cheie = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_add_cheie.setObjectName("pushButton_add_cheie")
        self.verticalLayout.addWidget(self.pushButton_add_cheie)
        self.pushButton_actualizare_cheie = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_actualizare_cheie.setObjectName("pushButton_actualizare_cheie")
        self.verticalLayout.addWidget(self.pushButton_actualizare_cheie)
        self.pushButton_stergere_cheie = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_stergere_cheie.setObjectName("pushButton_stergere_cheie")
        self.verticalLayout.addWidget(self.pushButton_stergere_cheie)
        self.listWidget_chei = QtWidgets.QListWidget(Dialog)
        self.listWidget_chei.setGeometry(QtCore.QRect(20, 40, 256, 192))
        self.listWidget_chei.setObjectName("listWidget_chei")
        self.listWidget_algoritmi = QtWidgets.QListWidget(Dialog)
        self.listWidget_algoritmi.setGeometry(QtCore.QRect(530, 40, 256, 192))
        self.listWidget_algoritmi.setObjectName("listWidget_algoritmi")
        self.listWidget_fisiere = QtWidgets.QListWidget(Dialog)
        self.listWidget_fisiere.setGeometry(QtCore.QRect(10, 280, 771, 192))
        self.listWidget_fisiere.setObjectName("listWidget_fisiere")
        self.label_framework = QtWidgets.QLabel(Dialog)
        self.label_framework.setGeometry(QtCore.QRect(810, 10, 171, 20))
        self.label_framework.setObjectName("label_framework")
        self.layoutWidget1 = QtWidgets.QWidget(Dialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(790, 290, 210, 128))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButton_criptare = QtWidgets.QPushButton(self.layoutWidget1)
        self.pushButton_criptare.setObjectName("pushButton_criptare")
        self.verticalLayout_2.addWidget(self.pushButton_criptare)
        self.pushButton_stergere_fisier = QtWidgets.QPushButton(self.layoutWidget1)
        self.pushButton_stergere_fisier.setObjectName("pushButton_stergere_fisier")
        self.verticalLayout_2.addWidget(self.pushButton_stergere_fisier)
        self.pushButton_decriptare = QtWidgets.QPushButton(self.layoutWidget1)
        self.pushButton_decriptare.setObjectName("pushButton_decriptare")
        self.verticalLayout_2.addWidget(self.pushButton_decriptare)
        self.layoutWidget2 = QtWidgets.QWidget(Dialog)
        self.layoutWidget2.setGeometry(QtCore.QRect(790, 130, 250, 113))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton_adaugare_algoritm = QtWidgets.QPushButton(self.layoutWidget2)
        self.pushButton_adaugare_algoritm.setObjectName("pushButton_adaugare_algoritm")
        self.verticalLayout_3.addWidget(self.pushButton_adaugare_algoritm)
        self.pushButton_modificare_algoritm = QtWidgets.QPushButton(self.layoutWidget2)
        self.pushButton_modificare_algoritm.setObjectName("pushButton_modificare_algoritm")
        self.verticalLayout_3.addWidget(self.pushButton_modificare_algoritm)
        self.pushButton_stergere_algoritm = QtWidgets.QPushButton(self.layoutWidget2)
        self.pushButton_stergere_algoritm.setObjectName("pushButton_stergere_algoritm")
        self.verticalLayout_3.addWidget(self.pushButton_stergere_algoritm)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.pushButton_add_cheie, self.pushButton_stergere_cheie)
        Dialog.setTabOrder(self.pushButton_stergere_cheie, self.pushButton_criptare)
        Dialog.setTabOrder(self.pushButton_criptare, self.listWidget_framework)
        Dialog.setTabOrder(self.listWidget_framework, self.pushButton_evaluare_performante)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "ProiectSI"))
        self.label_cheie.setText(_translate("Dialog", "Chei/Perechi disponibile:"))
        self.pushButton_evaluare_performante.setText(_translate("Dialog", "Comparare performanță framework-uri pentru AES256"))
        self.labelAlgo.setText(_translate("Dialog", "Algoritmi disponibili:"))
        self.label_fisier.setText(_translate("Dialog", "Fișiere gestionate:"))
        self.pushButton_add_cheie.setText(_translate("Dialog", "Adăugare cheie/pereche"))
        self.pushButton_actualizare_cheie.setText(_translate("Dialog", "Actualizare cheie/pereche selectată"))
        self.pushButton_stergere_cheie.setText(_translate("Dialog", "Ștergere cheie/pereche selectată\n"
" din baza de date"))
        self.label_framework.setText(_translate("Dialog", "Framework-uri disponibile:"))
        self.pushButton_criptare.setText(_translate("Dialog", "Criptare fișier"))
        self.pushButton_stergere_fisier.setText(_translate("Dialog", "Eliminare fișier selectat din \n"
"baza de date(fără o nouă\n"
"criptare/decriptare)"))
        self.pushButton_decriptare.setText(_translate("Dialog", "Decriptare fișier selectat"))
        self.pushButton_adaugare_algoritm.setText(_translate("Dialog", "Adăugare algoritm nou suportat cu\n"
"framework-ul și cheia selectate"))
        self.pushButton_modificare_algoritm.setText(_translate("Dialog", "Modificare parametri algoritm selectat"))
        self.pushButton_stergere_algoritm.setText(_translate("Dialog", "Ștergere algoritm selectat"))
