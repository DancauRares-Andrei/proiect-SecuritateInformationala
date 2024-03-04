import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog
import subprocess
import hashlib
import shutil
import os, time
import psutil
from db import *
from main_window_ui import Ui_Dialog 

OPENSSL_SYM = ["AES128", "AES192", "AES256"]
LIBRESSL_SYM = ["AES128", "AES256", "Camellia128"]
THEMIS_SYM = ["AES128", "ChaCha20", "Salsa20"]
GNUTLS_SYM = ["AES128", "Camellia128", "3DES"]

OPENSSL_ASYM = ["RSA4096","DSA1024", "ECDSA"]
LIBRESSL_ASYM = ["RSA4096", "DSA2048", "ECDSA"]
THEMIS_ASYM = ["RSA4096", "ECDSA", "ECDH"]
GNUTLS_ASYM = ["RSA4096", "ECDSA", "ECDH"]

def asimetrica(cheie):
    if " " in cheie:
        return True
    else:
        return False
def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
def algoritm_asimetric(nume):
    if nume in OPENSSL_ASYM or nume in LIBRESSL_ASYM or nume in THEMIS_ASYM or nume in GNUTLS_ASYM:
        return True
    else:
        return False 
def copiaza_continut(fisier_sursa, fisier_destinatie):
    shutil.copy(fisier_sursa, fisier_destinatie)
    os.remove(fisier_sursa)
class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.init_list_widget_cheie()
        self.init_list_widget_framework()
        self.init_list_widget_algo()
        self.init_list_widget_file()
        self.ui.pushButton_stergere_cheie.clicked.connect(self.pushButton_stergere_cheie_clicked)
        self.ui.pushButton_add_cheie.clicked.connect(self.open_key_input_window)
        self.ui.pushButton_actualizare_cheie.clicked.connect(self.update_key_input_window)
        self.ui.pushButton_adaugare_algoritm.clicked.connect(self.add_algo_input_window)
        self.ui.pushButton_stergere_algoritm.clicked.connect(self.pushButton_stergere_algoritm_clicked)
        self.ui.pushButton_modificare_algoritm.clicked.connect(self.update_algo_input_window)
        self.ui.pushButton_criptare.clicked.connect(self.encrypt_file)
        self.ui.pushButton_decriptare.clicked.connect(self.decrypt_file)
        self.ui.pushButton_stergere_fisier.clicked.connect(self.pushButton_stergere_fisier_clicked)
        self.ui.pushButton_evaluare_performante.clicked.connect(self.pushButton_evaluare_performante_clicked)
    def pushButton_stergere_cheie_clicked(self):
        try:
            selected_item = self.ui.listWidget_chei.currentItem()
            if selected_item:
                if asimetrica(selected_item.text()):
                    cheieCript,cheieDecript=selected_item.text().split(" ")
                    cheie=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                    cheie.delete_instance()
                    self.init_list_widget_cheie()
                    self.init_list_widget_algo()
                else:
                    cheieCript=selected_item.text()
                    cheie=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieCript))
                    cheie.delete_instance()
                    self.init_list_widget_cheie()
                    self.init_list_widget_algo()
                QMessageBox.information(None, "Ștergere efectuată!", "Cheie ștearsă cu succes! ")
            else:
                 QMessageBox.warning(self, "Avertisment", "Nu ați selectat niciun element!", QMessageBox.Ok)   
        except IntegrityError:
            QMessageBox.warning(self, "Avertisment", "Nu pot șterge cheia pentru că are asociați algoritmi!", QMessageBox.Ok) 
    def init_list_widget_cheie(self):
        self.ui.listWidget_chei.clear()
        values = [] 
        chei=Chei.select()
        for cheie in chei:
            if(cheie.CheieCriptare==cheie.CheieDecriptare):
                values.append(cheie.CheieCriptare)
            else:
                values.append(cheie.CheieCriptare+" "+cheie.CheieDecriptare)
        self.ui.listWidget_chei.addItems(values)
    def update_key_input_window(self):
        selected_item = self.ui.listWidget_chei.currentItem()
        if selected_item:
            cheie_veche=selected_item.text()
            key1, ok1 = QInputDialog.getText(self, 'Introducere noua cheie de criptare', 'Introduceți noua cheie de criptare:')
            key2, ok2 = QInputDialog.getText(self, 'Introducere cheie decriptare', 'Introduceți cheia de decriptare(identică cu precedenta dacă se dorește cheie simetrică):')
            
            if ok1 and ok2:
                if not " " in key1 and " " not in key2:#Verificarea existentei spatiilor in chei
                    if asimetrica(cheie_veche)==False and key1!=key2:
                        QMessageBox.warning(self, "Avertisment", "Nu pot înlocui o cheie simetrică cu o pereche de chei asimetrice!", QMessageBox.Ok)
                    elif asimetrica(cheie_veche) and key1==key2:
                        QMessageBox.warning(self, "Avertisment", "Este de preferat să nu se înlocuiască o pereche de chei asimentrice cu o cheie simetrică!", QMessageBox.Ok)
                    else:
                        if asimetrica(cheie_veche):
                            cheieCript,cheieDecript=cheie_veche.split(" ")
                            cheie=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                            cheie.CheieCriptare=key1
                            cheie.CheieDecriptare=key2
                            cheie.save()
                        else:
                            cheie=Chei.get((Chei.CheieCriptare==cheie_veche) & (Chei.CheieDecriptare==cheie_veche))
                            cheie.CheieCriptare=key1
                            cheie.CheieDecriptare=key2
                            cheie.save()
                        self.init_list_widget_cheie()
                        self.init_list_widget_algo()    
                        QMessageBox.information(self, "Chei introduse", f"S-a modificat cu succes cheia!", QMessageBox.Ok)              
                else:
                    QMessageBox.warning(self, "Avertisment", "Cheile nu pot conține spații!", QMessageBox.Ok)    
            else:
                QMessageBox.warning(self, "Avertisment", "Nu ați introdus ambele chei!", QMessageBox.Ok)
        else:
             QMessageBox.warning(self, "Avertisment", "Nu ați selectat niciun element!", QMessageBox.Ok)        
    def open_key_input_window(self):
        key1, ok1 = QInputDialog.getText(self, 'Introducere cheie criptare', 'Introduceți cheia de criptare:')
        key2, ok2 = QInputDialog.getText(self, 'Introducere cheie decriptare', 'Introduceți cheia de decriptare(identică cu precedenta dacă se dorește cheie simetrică):')
        
        if ok1 and ok2:
            if not " " in key1 and " " not in key2:#Verificarea existentei spatiilor in chei
                cheie=Chei.create(
                CheieCriptare=key1,
                CheieDecriptare=key2
                )
                self.init_list_widget_cheie()
                QMessageBox.information(self, "Chei introduse", f"S-a adăugat cu succes la baza de date!", QMessageBox.Ok)              
            else:
                QMessageBox.warning(self, "Avertisment", "Cheile nu pot conține spații!", QMessageBox.Ok)    
        else:
            QMessageBox.warning(self, "Avertisment", "Nu ați introdus ambele chei!", QMessageBox.Ok)
    def init_list_widget_framework(self):
        values = [] 
        frameworks=Frameworkuri.select()
        for framework in frameworks:
            values.append(framework.Nume)
        self.ui.listWidget_framework.addItems(values)
    def add_algo_input_window(self):
        framework=self.ui.listWidget_framework.currentItem()
        cheie=self.ui.listWidget_chei.currentItem()
        if framework and cheie:
            framework=framework.text()
            cheie=cheie.text()
            nume, ok1 = QInputDialog.getText(self, 'Numele algoritmului de criptare', 'Introduceți numele algoritmului de criptare:')
            if ok1:
                if framework=="OpenSSL":
                    if nume.upper() in OPENSSL_SYM and asimetrica(cheie)==False:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                        QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                    elif nume.upper() in OPENSSL_ASYM and asimetrica(cheie)==True:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheieCript,cheieDecript=cheie.split(" ")
                        cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                    else:
                         QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)
                elif framework=="LibreSSL":
                    if nume.upper() in LIBRESSL_SYM and asimetrica(cheie)==False:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                        QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                    elif nume.upper() in LIBRESSL_ASYM and asimetrica(cheie)==True:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheieCript,cheieDecript=cheie.split(" ")
                        cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                    else:
                         QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                elif framework=="Themis":
                    if nume.upper() in THEMIS_SYM and asimetrica(cheie)==False:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                        QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                    elif nume.upper() in THEMIS_ASYM and asimetrica(cheie)==True:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheieCript,cheieDecript=cheie.split(" ")
                        cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                    else:
                         QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                elif framework=="GnuTLS":
                    if nume.upper() in GNUTLS_SYM and asimetrica(cheie)==False:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                        QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                    elif nume.upper() in GNUTLS_ASYM and asimetrica(cheie)==True:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheieCript,cheieDecript=cheie.split(" ")
                        cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                    else:
                         QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                         
                else:
                    QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok) 
        else:
            QMessageBox.warning(self, "Avertisment", "Trebuie selectat un framework și o cheie!", QMessageBox.Ok)
    def init_list_widget_algo(self):
        self.ui.listWidget_algoritmi.clear()
        values = [] 
        algos=Algoritmi.select()
        for algo in algos:
            current_val=algo.Nume+" "+algo.FrameworkID.Nume+" "
            if(algo.CheieID.CheieCriptare==algo.CheieID.CheieDecriptare):
                current_val+=algo.CheieID.CheieCriptare
            else:
                current_val+=algo.CheieID.CheieCriptare+" "+algo.CheieID.CheieDecriptare
            values.append(current_val)
        self.ui.listWidget_algoritmi.addItems(values)   
    def pushButton_stergere_algoritm_clicked(self):
        try:
            selected_item = self.ui.listWidget_algoritmi.currentItem()
            if selected_item:
                componente=selected_item.text().split(" ")
                if len(componente)==4:
                    cheie_e=Chei.get((Chei.CheieCriptare==componente[2]) & (Chei.CheieDecriptare==componente[3]))
                    framework_e=Frameworkuri.get(Frameworkuri.Nume==componente[1])
                    algo_e=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == componente[0]))
                    algo_e.delete_instance()
                    self.init_list_widget_algo()
                else:
                    cheie_e=Chei.get((Chei.CheieCriptare==componente[2]) & (Chei.CheieDecriptare==componente[2]))
                    framework_e=Frameworkuri.get(Frameworkuri.Nume==componente[1])
                    algo_e=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == componente[0]))
                    algo_e.delete_instance()
                    self.init_list_widget_algo()
                QMessageBox.information(None, "Ștergere efectuată!", "Algoritm șters cu succes! ")
            else:
                 QMessageBox.warning(self, "Avertisment", "Nu ați selectat niciun algoritm!", QMessageBox.Ok)   
        except IntegrityError:
            QMessageBox.warning(self, "Avertisment", "Nu pot șterge algoritmul pentru că are asociate fișiere!", QMessageBox.Ok)
    def update_algo_input_window(self):
        selected_item = self.ui.listWidget_algoritmi.currentItem()
        if selected_item:
            componente=selected_item.text().split(" ")
            framework_vechi=componente[1]
            cheie_criptare_veche=componente[2]
            if len(componente)==4:
                cheie_decriptare_veche=componente[3]
            else:
                cheie_decriptare_veche=componente[2]           
            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework_vechi)
            cheie_e=Chei.get((Chei.CheieCriptare == cheie_criptare_veche)&(Chei.CheieDecriptare == cheie_decriptare_veche))
            algoritm_vechi=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == componente[0]))
            framework=self.ui.listWidget_framework.currentItem()
            cheie=self.ui.listWidget_chei.currentItem()
            if framework and cheie:
                framework=framework.text()
                cheie=cheie.text()
                nume, ok1 = QInputDialog.getText(self, 'Numele algoritmului de criptare', 'Introduceți noul nume al algoritmului de criptare:')
                if ok1:
                    if framework=="OpenSSL":
                        if nume.upper() in OPENSSL_SYM and asimetrica(cheie)==False:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                            QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                        elif nume.upper() in OPENSSL_ASYM and asimetrica(cheie)==True:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheieCript,cheieDecript=cheie.split(" ")
                            cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                        else:
                             QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)
                    elif framework=="LibreSSL":
                        if nume.upper() in LIBRESSL_SYM and asimetrica(cheie)==False:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                            QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                        elif nume.upper() in LIBRESSL_ASYM and asimetrica(cheie)==True:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheieCript,cheieDecript=cheie.split(" ")
                            cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                        else:
                             QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                    elif framework=="Themis":
                        if nume.upper() in THEMIS_SYM and asimetrica(cheie)==False:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                            QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                        elif nume.upper() in THEMIS_ASYM and asimetrica(cheie)==True:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheieCript,cheieDecript=cheie.split(" ")
                            cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                        else:
                             QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                    elif framework=="GnuTLS":
                        if nume.upper() in GNUTLS_SYM and asimetrica(cheie)==False:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                            QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                        elif nume.upper() in GNUTLS_ASYM and asimetrica(cheie)==True:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheieCript,cheieDecript=cheie.split(" ")
                            cheie_e=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                        else:
                             QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                             
                    else:
                        QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok) 
            else:
                QMessageBox.warning(self, "Avertisment", "Trebuie selectat un framework și o cheie!", QMessageBox.Ok)  
        else:
             QMessageBox.warning(self, "Avertisment", "Nu a fost selectat niciun algoritm de modificat!", QMessageBox.Ok)  
    def encrypt_file(self):
        selected_item = self.ui.listWidget_algoritmi.currentItem()
        if selected_item:
            componente=selected_item.text().split(" ")
            nume=componente[0]
            framework=componente[1]
            cheie_criptare=componente[2]
            if len(componente)==4:
                cheie_decriptare=componente[3]
            else:
                cheie_decriptare=componente[2]           
            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
            cheie_e=Chei.get((Chei.CheieCriptare == cheie_criptare)&(Chei.CheieDecriptare == cheie_decriptare))
            algoritm_e=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == componente[0]))
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                file_hash=calculate_md5(file_path)
                if framework=="OpenSSL":
                    if nume=="AES128":
                        openssl_command = [
                            "openssl", "enc", "-aes128", "-pbkdf2",
                            "-in", file_path,
                            "-out", file_path+'.temp',
                            "-pass", "pass:"+cheie_criptare
                        ]
                    elif nume=="AES192":
                        openssl_command = [
                            "openssl", "enc", "-aes192", "-pbkdf2",
                            "-in", file_path,
                            "-out", file_path+'.temp',
                            "-pass", "pass:"+cheie_criptare
                        ]
                    elif nume=="AES256":
                        openssl_command = [
                            "openssl", "enc", "-aes256", "-pbkdf2",
                            "-in", file_path,
                            "-out", file_path+'.temp',
                            "-pass", "pass:"+cheie_criptare
                        ]
                    start_time = time.time()
                    completed_process = subprocess.run(openssl_command, check=True)
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000 
                    if completed_process.returncode != 0:
                        QMessageBox.warning(self, "Avertisment", f"A apărut o eroare la criptarea fișierului! Cod:{completed_process.returncode}", QMessageBox.Ok)
                        return
                    copiaza_continut(file_path+'.temp',file_path)
                    file_e=Fisiere.create(
                    AlgoritmID = algoritm_e,
                    Cale = file_path,
                    Criptat = True,
                    Timp = duration_ms,
                    Hash = str(file_hash),
                    UsedRAM = str(psutil.Process().memory_info().rss / (1024 * 1024))+"MB"
                    )
                    self.init_list_widget_file()         
        else:
             QMessageBox.warning(self, "Avertisment", "Nu a fost selectat niciun algoritm de criptare!", QMessageBox.Ok)
    def init_list_widget_file(self):
        self.ui.listWidget_fisiere.clear()
        values = [] 
        fisiere=Fisiere.select()
        for fisier in fisiere:
            current_val=fisier.Cale.split("/")[-1]+" "+fisier.AlgoritmID.Nume+" "+fisier.AlgoritmID.FrameworkID.Nume+" "
            if(fisier.AlgoritmID.CheieID.CheieCriptare==fisier.AlgoritmID.CheieID.CheieDecriptare):
                current_val+=fisier.AlgoritmID.CheieID.CheieCriptare+" "
            else:
                current_val+=fisier.AlgoritmID.CheieID.CheieCriptare+" "+fisier.AlgoritmID.CheieID.CheieDecriptare+" "
            current_val+=str(fisier.Criptat)+" "+str(fisier.Timp)+"ms MD5:"+fisier.Hash+" "+fisier.UsedRAM+" "+fisier.Cale
            values.append(current_val)
        self.ui.listWidget_fisiere.addItems(values)
    def pushButton_stergere_fisier_clicked(self):
        selected_item = self.ui.listWidget_fisiere.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Avertisment", "Nu a fost selectat niciun fișier de șters!", QMessageBox.Ok)
            return
        componente=selected_item.text().split(" ")
        nume_algoritm=componente[1]
        framework=componente[2]
        cheie_criptare=componente[3]
        if algoritm_asimetric(nume_algoritm):
            cheie_decriptare=componente[4]
            criptat=True if componente[5]=="True" else False
            timp=int(componente[6][:-3])
            hash_file=componente[7][4:]
            used_ram=componente[8]
            file_path=" ".join(componente[9:])
        else:
            cheie_decriptare=componente[3]
            criptat=True if componente[4]=="True" else False
            timp=int(componente[5][:-2])
            hash_file=componente[6][4:]
            used_ram=componente[7]
            file_path=" ".join(componente[8:])
        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
        cheie_e=Chei.get((Chei.CheieCriptare == cheie_criptare)&(Chei.CheieDecriptare == cheie_decriptare))
        algoritm_e=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == nume_algoritm))
        fisier_e=Fisiere.get((Fisiere.AlgoritmID==algoritm_e) & (Fisiere.Cale==file_path) & (Fisiere.Criptat==criptat) & (Fisiere.Timp==timp) & (Fisiere.Hash==hash_file) & (Fisiere.UsedRAM==used_ram))
        fisier_e.delete_instance()
        self.init_list_widget_file()
    def decrypt_file(self):
        try:
            selected_item = self.ui.listWidget_fisiere.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Avertisment", "Nu a fost selectat niciun fișier de șters!", QMessageBox.Ok)
                return
            componente=selected_item.text().split(" ")
            nume_algoritm=componente[1]
            framework=componente[2]
            cheie_criptare=componente[3]
            if algoritm_asimetric(nume_algoritm):
                cheie_decriptare=componente[4]
                criptat=True if componente[5]=="True" else False
                timp=int(componente[6][:-3])
                hash_file=componente[7][4:]
                used_ram=componente[8]
                file_path=" ".join(componente[9:])
            else:
                cheie_decriptare=componente[3]
                criptat=True if componente[4]=="True" else False
                timp=int(componente[5][:-2])
                hash_file=componente[6][4:]
                used_ram=componente[7]
                file_path=" ".join(componente[8:])
            if criptat==False:
                QMessageBox.warning(self, "Avertisment", "Fișierul este deja decriptat!", QMessageBox.Ok)
                return
            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
            cheie_e=Chei.get((Chei.CheieCriptare == cheie_criptare)&(Chei.CheieDecriptare == cheie_decriptare))
            algoritm_e=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == nume_algoritm))
            fisier_e=Fisiere.get((Fisiere.AlgoritmID==algoritm_e) & (Fisiere.Cale==file_path) & (Fisiere.Criptat==criptat) & (Fisiere.Timp==timp) & (Fisiere.Hash==hash_file) & (Fisiere.UsedRAM==used_ram))
            if framework=="OpenSSL":
                if nume_algoritm=="AES128":
                    openssl_command = [
                        "openssl", "enc", "-aes128", "-pbkdf2","-d",
                        "-in", file_path,
                        "-out", file_path+'.temp',
                        "-pass", "pass:"+cheie_criptare
                    ]
                elif nume_algoritm=="AES192":
                    openssl_command = [
                        "openssl", "enc", "-aes192", "-pbkdf2","-d",
                        "-in", file_path,
                        "-out", file_path+'.temp',
                        "-pass", "pass:"+cheie_criptare
                    ]
                elif nume_algoritm=="AES256":
                    openssl_command = [
                        "openssl", "enc", "-aes256", "-pbkdf2","-d",
                        "-in", file_path,
                        "-out", file_path+'.temp',
                        "-pass", "pass:"+cheie_criptare
                    ]
                start_time = time.time()
                completed_process = subprocess.run(openssl_command, check=True)
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                if completed_process.returncode != 0:
                    QMessageBox.warning(self, "Avertisment", f"A apărut o eroare la decriptarea fișierului! Cod:{completed_process.returncode}", QMessageBox.Ok)
                    return
                copiaza_continut(file_path+'.temp',file_path)
                fisier_e.Criptat=False
                fisier_e.Timp=duration_ms
                fisier_e.UsedRAM=str(psutil.Process().memory_info().rss / (1024 * 1024))+"MB"
                fisier_e.save()
                self.init_list_widget_file()
        except Fisiere.DoesNotExist:
                QMessageBox.warning(self, "Avertisment", "Nu am putut decripta(fisier negasit)!", QMessageBox.Ok)    
    def pushButton_evaluare_performante_clicked(self):
        pass                    
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

