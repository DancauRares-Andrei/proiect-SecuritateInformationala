import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog, QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import subprocess
import hashlib
import shutil
import os, time
import psutil
import matplotlib.pyplot as plt
from db import *
from main_window_ui import Ui_Dialog 

OPENSSL_SYM = ["AES128", "AES192", "AES256"]
CCRYPT_SYM = ["AES256"]
MCRYPT_SYM = ["AES256", "CAST128", "CAST256"]#AES256=rijdael-256
#RSA512->OpenSSL
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

def copiaza_continut(fisier_sursa, fisier_destinatie):
    shutil.copy(fisier_sursa, fisier_destinatie)
    os.remove(fisier_sursa)
def evaluare_performanta(fisiere):
    timp=0
    ram_consumat=0
    dim_fisiere=0
    for fisier in fisiere:
        timp+=float(fisier.Timp)
        ram_consumat+=float(fisier.UsedRAM[:-2])
        dim_fisiere+=float(fisier.DimFisier[:-2])
    timp/=dim_fisiere#timp in ms normalizat la dimensiunea fisierelor
    ram_consumat/=dim_fisiere#MB RAM consumati normalizat la dimensiunea fisierelor
    return round(timp,4),round(ram_consumat,4)
class GraphWindow(QDialog):
    def __init__(self,fig,parent=None):
        super().__init__(parent)
        self.setWindowTitle('Grafice Performanță')
        layout = QVBoxLayout()
        
        # Adăugare grafic timp
        fig.tight_layout()
        canvas1 = FigureCanvas(fig)
        layout.addWidget(canvas1)

        self.setLayout(layout)
        self.resize(1280, 1000)
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
        self.ui.pushButton_criptare.clicked.connect(self.pushButton_criptare_clicked)
        self.ui.pushButton_decriptare.clicked.connect(self.pushButton_decriptare_clicked)
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
            
            if ok1 and ok2 and key1!="" and key2!="":
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
        
        if ok1 and ok2 and key1!="" and key2!="":
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
                    elif nume.upper()=="RSA512" and asimetrica(cheie)==True:
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
                elif framework=="Ccrypt":
                    if nume.upper() in CCRYPT_SYM and asimetrica(cheie)==False:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                        QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                    else:
                         QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                elif framework=="Mcrypt":
                    if nume.upper() in MCRYPT_SYM and asimetrica(cheie)==False:
                        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                        cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                        algo=Algoritmi.create(
                        Nume = nume,
                        CheieID = cheie_e,
                        FrameworkID = framework_e
                        )
                        self.init_list_widget_algo()
                        QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
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
                        elif nume.upper()=="RSA512" and asimetrica(cheie)==True:
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
                    elif framework=="Ccrypt":
                        if nume.upper() in CCRYPT_SYM and asimetrica(cheie)==False:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                            QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                        else:
                             QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)         
                    elif framework=="Mcrypt":
                        if nume.upper() in MCRYPT_SYM and asimetrica(cheie)==False:
                            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
                            cheie_e=Chei.get((Chei.CheieCriptare == cheie)&(Chei.CheieDecriptare == cheie))
                            algoritm_vechi.FrameworkID=framework_e
                            algoritm_vechi.CheieID=cheie_e
                            algoritm_vechi.Nume=nume
                            algoritm_vechi.save()
                            self.init_list_widget_algo()
                            QMessageBox.information(self, "Chei introduse", f"S-a adaugat algoritmul cu succes!", QMessageBox.Ok) 
                        else:
                             QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok)                                          
                    else:
                        QMessageBox.warning(self, "Avertisment", "Algoritm nesuportat sau nepotrivire între algoritm și cheie!", QMessageBox.Ok) 
            else:
                QMessageBox.warning(self, "Avertisment", "Trebuie selectat un framework și o cheie!", QMessageBox.Ok)  
        else:
             QMessageBox.warning(self, "Avertisment", "Nu a fost selectat niciun algoritm de modificat!", QMessageBox.Ok)  
    def pushButton_criptare_clicked(self):
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
                try:
                    fisier_existent=Fisiere.get((Fisiere.Cale==file_path)&(Fisiere.Criptat==True))
                    QMessageBox.warning(self, "Avertisment", f"Un fișier nu poate fi criptat de mai multe ori!", QMessageBox.Ok)
                    return
                except Fisiere.DoesNotExist:
                    pass
                file_hash=calculate_md5(file_path)
                file_stats = os.stat(file_path)
                dim_file_kb=file_stats.st_size / 1024
                if framework=="OpenSSL":
                    if nume=="AES128":
                        encrypt_command = [
                            "openssl", "enc", "-aes128", "-pbkdf2",
                            "-in", file_path,
                            "-out", file_path+'.temp',
                            "-pass", "pass:"+cheie_criptare
                        ]
                    elif nume=="AES192":
                        encrypt_command = [
                            "openssl", "enc", "-aes192", "-pbkdf2",
                            "-in", file_path,
                            "-out", file_path+'.temp',
                            "-pass", "pass:"+cheie_criptare
                        ]
                    elif nume=="AES256":
                        encrypt_command = [
                            "openssl", "enc", "-aes256", "-pbkdf2",
                            "-in", file_path,
                            "-out", file_path+'.temp',
                            "-pass", "pass:"+cheie_criptare
                        ]
                    elif nume=="RSA512":
                         with open(file_path+".cheie_pub", "w") as file_pubkey:
                            file_pubkey.write("-----BEGIN PUBLIC KEY-----\n")
                            file_pubkey.write(cheie_criptare+"\n")
                            file_pubkey.write("-----END PUBLIC KEY-----\n")
                         encrypt_command = [
                            "openssl", "pkeyutl", "-encrypt", "-inkey",
                            file_path+".cheie_pub","-pubin",
                            "-in",file_path,
                            "-out", file_path+'.temp',
                        ]
                elif framework=="Mcrypt":
                    if nume == "AES256":
                        encrypt_command = [
                            "mcrypt", "-m", "cbc","-k" , cheie_criptare, "-a","rijndael-256" ,file_path,"--flush","-q"
                        ]
                    elif nume == "CAST128":
                        encrypt_command = [
                            "mcrypt", "-m", "cbc","-k" , cheie_criptare, "-a","cast-128" ,file_path,"--flush","-q"
                        ]
                    elif nume == "CAST256":
                        encrypt_command = [
                            "mcrypt", "-m", "cbc","-k" , cheie_criptare, "-a","cast-256" ,file_path,"--flush","-q"
                        ]    
                elif framework=="Ccrypt" and nume=="AES256":
                    encrypt_command = [
                            "ccrypt", "-e", "-K", cheie_criptare,
                            file_path,
                        ]            
                start_time = time.time()
                completed_process = subprocess.run(encrypt_command, check=True)
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000 
                if completed_process.returncode != 0:
                    QMessageBox.warning(self, "Avertisment", f"A apărut o eroare la criptarea fișierului! Cod:{completed_process.returncode}", QMessageBox.Ok)
                    return
                if framework=="OpenSSL":
                    copiaza_continut(file_path+'.temp',file_path)
                    if nume=="RSA512":
                        os.remove(file_path+".cheie_pub")
                elif framework=="Ccrypt":
                    copiaza_continut(file_path+'.cpt',file_path)
                elif framework=="Mcrypt":
                    copiaza_continut(file_path+'.nc',file_path)
                file_e=Fisiere.create(
                AlgoritmID = algoritm_e,
                Cale = file_path,
                Criptat = True,
                Timp = duration_ms,
                Hash = str(file_hash),
                UsedRAM = str(psutil.Process().memory_info().rss / (1024 * 1024))+"MB",
                DimFisier = str(dim_file_kb)+"kB"
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
            current_val+=str(fisier.Criptat)+" "+str(fisier.Timp)+"ms MD5:"+fisier.Hash+" "+fisier.UsedRAM+" "+fisier.Cale+" "+fisier.DimFisier
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
        dim_file=componente[-1]
        if nume_algoritm=="RSA512":
            cheie_decriptare=componente[4]
            criptat=True if componente[5]=="True" else False
            timp=int(componente[6][:-2])
            hash_file=componente[7][4:]
            used_ram=componente[8]
            file_path=" ".join(componente[9:-1])
        else:
            cheie_decriptare=componente[3]
            criptat=True if componente[4]=="True" else False
            timp=int(componente[5][:-2])
            hash_file=componente[6][4:]
            used_ram=componente[7]
            file_path=" ".join(componente[8:-1])
        framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
        cheie_e=Chei.get((Chei.CheieCriptare == cheie_criptare)&(Chei.CheieDecriptare == cheie_decriptare))
        algoritm_e=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == nume_algoritm))
        fisier_e=Fisiere.get((Fisiere.AlgoritmID==algoritm_e) & (Fisiere.Cale==file_path) & (Fisiere.Criptat==criptat) & (Fisiere.Timp==timp) & (Fisiere.Hash==hash_file) & (Fisiere.UsedRAM==used_ram) & (Fisiere.DimFisier == dim_file))
        fisier_e.delete_instance()
        self.init_list_widget_file()
    def pushButton_decriptare_clicked(self):
        try:
            selected_item = self.ui.listWidget_fisiere.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Avertisment", "Nu a fost selectat niciun fișier de șters!", QMessageBox.Ok)
                return
            componente=selected_item.text().split(" ")
            nume_algoritm=componente[1]
            framework=componente[2]
            cheie_criptare=componente[3]
            dim_file=componente[-1]
            if nume_algoritm=="RSA512":
                cheie_decriptare=componente[4]
                criptat=True if componente[5]=="True" else False
                timp=int(componente[6][:-2])
                hash_file=componente[7][4:]
                used_ram=componente[8]
                file_path=" ".join(componente[9:-1])
            else:
                cheie_decriptare=componente[3]
                criptat=True if componente[4]=="True" else False
                timp=int(componente[5][:-2])
                hash_file=componente[6][4:]
                used_ram=componente[7]
                file_path=" ".join(componente[8:-1])
                
            if criptat==False:
                QMessageBox.warning(self, "Avertisment", "Fișierul este deja decriptat!", QMessageBox.Ok)
                return
            framework_e=Frameworkuri.get(Frameworkuri.Nume == framework)
            cheie_e=Chei.get((Chei.CheieCriptare == cheie_criptare)&(Chei.CheieDecriptare == cheie_decriptare))
            algoritm_e=Algoritmi.get((Algoritmi.CheieID==cheie_e) & (Algoritmi.FrameworkID==framework_e) & (Algoritmi.Nume == nume_algoritm))
            fisier_e=Fisiere.get((Fisiere.AlgoritmID==algoritm_e) & (Fisiere.Cale==file_path) & (Fisiere.Criptat==criptat) & (Fisiere.Timp==timp) & (Fisiere.Hash==hash_file) & (Fisiere.UsedRAM==used_ram) & (Fisiere.DimFisier == dim_file))
            if framework=="OpenSSL":
                if nume_algoritm=="AES128":
                    decrypt_command = [
                        "openssl", "enc", "-aes128", "-pbkdf2","-d",
                        "-in", file_path,
                        "-out", file_path+'.temp',
                        "-pass", "pass:"+cheie_criptare
                    ]
                elif nume_algoritm=="AES192":
                    decrypt_command = [
                        "openssl", "enc", "-aes192", "-pbkdf2","-d",
                        "-in", file_path,
                        "-out", file_path+'.temp',
                        "-pass", "pass:"+cheie_criptare
                    ]
                elif nume_algoritm=="AES256":
                    decrypt_command = [
                        "openssl", "enc", "-aes256", "-pbkdf2","-d",
                        "-in", file_path,
                        "-out", file_path+'.temp',
                        "-pass", "pass:"+cheie_criptare
                    ]
                elif nume_algoritm=="RSA512":
                    with open(file_path+".cheie_priv", "w") as file_pubkey:
                            file_pubkey.write("-----BEGIN PRIVATE KEY-----\n")
                            file_pubkey.write(cheie_decriptare+"\n")
                            file_pubkey.write("-----END PRIVATE KEY-----\n")
                    decrypt_command = [
                        "openssl", "pkeyutl", "-decrypt", "-inkey",
                        file_path+".cheie_priv",
                        "-in",file_path,
                        "-out", file_path+'.temp',
                    ] 
            elif framework=="Mcrypt":
                if nume_algoritm=="AES256":
                    decrypt_command = [
                            "mcrypt", "-d", "-m", "cbc","-k" , cheie_criptare, "-a","rijndael-256" ,file_path,"--flush","-q"
                        ]
                elif nume_algoritm == "CAST128":
                    decrypt_command = [
                            "mcrypt", "-d", "-m", "cbc","-k" , cheie_criptare, "-a","cast-128" ,file_path,"--flush","-q"
                        ]
                elif nume_algoritm == "CAST256":
                    decrypt_command = [
                            "mcrypt", "-d", "-m", "cbc","-k" , cheie_criptare, "-a","cast-256" ,file_path,"--flush","-q"
                        ]
            elif framework=="Ccrypt" and nume_algoritm=="AES256":
                decrypt_command = [
                        "ccrypt", "-d", "-K", cheie_criptare,
                        file_path,
                    ]                      
            file_stats = os.stat(file_path)
            dim_file_kb=file_stats.st_size / 1024
            start_time = time.time()
            completed_process = subprocess.run(decrypt_command, check=True)
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            if completed_process.returncode != 0:
                QMessageBox.warning(self, "Avertisment", f"A apărut o eroare la decriptarea fișierului! Cod:{completed_process.returncode}", QMessageBox.Ok)
                return
            if framework=="OpenSSL":
                copiaza_continut(file_path+'.temp',file_path)
            elif framework=="Mcrypt":
                copiaza_continut(file_path+'.dc',file_path)
            fisier_e.Criptat=False
            fisier_e.Timp=duration_ms
            fisier_e.UsedRAM=str(psutil.Process().memory_info().rss / (1024 * 1024))+"MB"
            fisier_e.DimFisier = str(dim_file_kb)+"kB"
            fisier_e.save()
            if framework=="OpenSSL" and nume_algoritm=="RSA512":
                    os.remove(file_path+".cheie_priv")
            self.init_list_widget_file()         
        except Fisiere.DoesNotExist:
                QMessageBox.warning(self, "Avertisment", "Nu am putut decripta(fisier negasit)!", QMessageBox.Ok)    
    def pushButton_evaluare_performante_clicked(self):
        open_ssl_criptate_aes256=list(Fisiere.select().join(Algoritmi).join(Frameworkuri).where((Frameworkuri.Nume=="OpenSSL") & (Fisiere.Criptat==True) & (Algoritmi.Nume=="AES256")))
        if len(open_ssl_criptate_aes256)==0:
            QMessageBox.warning(self, "Avertisment", "Pentru a compara framework-urile, trebuie să existe un fișier criptat cu AES256 și OpenSSL", QMessageBox.Ok)
            return
        open_ssl_decriptate_aes256=list(Fisiere.select().join(Algoritmi).join(Frameworkuri).where((Frameworkuri.Nume=="OpenSSL") & (Fisiere.Criptat==False) & (Algoritmi.Nume=="AES256")))
        if len(open_ssl_decriptate_aes256)==0:
            QMessageBox.warning(self, "Avertisment", "Pentru a compara framework-urile, trebuie să existe un fișier decriptat cu AES256 și OpenSSL", QMessageBox.Ok)
            return
        ccrypt_criptate_aes256=list(Fisiere.select().join(Algoritmi).join(Frameworkuri).where((Frameworkuri.Nume=="Ccrypt") & (Fisiere.Criptat==True) & (Algoritmi.Nume=="AES256")))
        if len(ccrypt_criptate_aes256)==0:
            QMessageBox.warning(self, "Avertisment", "Pentru a compara framework-urile, trebuie să existe un fișier criptat cu AES256 și Ccrypt", QMessageBox.Ok)
            return
        ccrypt_decriptate_aes256=list(Fisiere.select().join(Algoritmi).join(Frameworkuri).where((Frameworkuri.Nume=="Ccrypt") & (Fisiere.Criptat==False) & (Algoritmi.Nume=="AES256")))
        if len(ccrypt_decriptate_aes256)==0:
            QMessageBox.warning(self, "Avertisment", "Pentru a compara framework-urile, trebuie să existe un fișier decriptat cu AES256 și Ccrypt", QMessageBox.Ok)
            return
        mcrypt_criptate_aes256=list(Fisiere.select().join(Algoritmi).join(Frameworkuri).where((Frameworkuri.Nume=="Mcrypt") & (Fisiere.Criptat==True) & (Algoritmi.Nume=="AES256")))
        if len(mcrypt_criptate_aes256)==0:
            QMessageBox.warning(self, "Avertisment", "Pentru a compara framework-urile, trebuie să existe un fișier criptat cu AES256 și Mcrypt", QMessageBox.Ok)
            return
        mcrypt_decriptate_aes256=list(Fisiere.select().join(Algoritmi).join(Frameworkuri).where((Frameworkuri.Nume=="Mcrypt") & (Fisiere.Criptat==False) & (Algoritmi.Nume=="AES256")))
        if len(mcrypt_decriptate_aes256)==0:
            QMessageBox.warning(self, "Avertisment", "Pentru a compara framework-urile, trebuie să existe un fișier decriptat cu AES256 și Mcrypt", QMessageBox.Ok)
            return
        timp_criptare_open_ssl_normalizat, ram_consumat_criptare_open_ssl_normalizat = evaluare_performanta(open_ssl_criptate_aes256)
        timp_decriptare_open_ssl_normalizat, ram_consumat_decriptare_open_ssl_normalizat = evaluare_performanta(open_ssl_decriptate_aes256)
        timp_criptare_ccrypt_normalizat, ram_consumat_criptare_ccrypt_normalizat = evaluare_performanta(ccrypt_criptate_aes256)
        timp_decriptare_ccrypt_normalizat, ram_consumat_decriptare_ccrypt_normalizat = evaluare_performanta(ccrypt_decriptate_aes256)
        timp_criptare_mcrypt_normalizat, ram_consumat_criptare_mcrypt_normalizat = evaluare_performanta(mcrypt_criptate_aes256)
        timp_decriptare_mcrypt_normalizat, ram_consumat_decriptare_mcrypt_normalizat= evaluare_performanta(mcrypt_decriptate_aes256)       
        frameworks = ['OpenSSL', 'ccrypt', 'mcrypt']
        timp_criptare = [timp_criptare_open_ssl_normalizat, timp_criptare_ccrypt_normalizat, timp_criptare_mcrypt_normalizat]
        timp_decriptare = [timp_decriptare_open_ssl_normalizat, timp_decriptare_ccrypt_normalizat, timp_decriptare_mcrypt_normalizat]
        ram_consumat_criptare = [ram_consumat_criptare_open_ssl_normalizat, ram_consumat_criptare_ccrypt_normalizat, ram_consumat_criptare_mcrypt_normalizat]
        ram_consumat_decriptare = [ram_consumat_decriptare_open_ssl_normalizat, ram_consumat_decriptare_ccrypt_normalizat, ram_consumat_decriptare_mcrypt_normalizat]
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        axs[0, 0].bar(frameworks, timp_criptare, color='blue')
        axs[0, 0].set_xlabel('Framework-uri')
        axs[0, 0].set_ylabel('Timp normalizat (ms/kB)')
        axs[0, 0].set_title('Timpul de criptare AES256 normalizat')
        axs[0, 1].bar(frameworks, timp_decriptare, color='orange')
        axs[0, 1].set_xlabel('Framework-uri')
        axs[0, 1].set_ylabel('Timp normalizat (ms/kB)')
        axs[0, 1].set_title('Timpul de decriptare AES256 normalizat')
        axs[1, 0].bar(frameworks, ram_consumat_criptare, color='green')
        axs[1, 0].set_xlabel('Framework-uri')
        axs[1, 0].set_ylabel('Memorie consumată normalizată (MB RAM/kB spațiu)')
        axs[1, 0].set_title('Memoria consumată în timpul criptării AES256 normalizată')
        axs[1, 1].bar(frameworks, ram_consumat_decriptare, color='red')
        axs[1, 1].set_xlabel('Framework-uri')
        axs[1, 1].set_ylabel('Memorie consumată normalizată (MB RAM/kB spațiu)')
        axs[1, 1].set_title('Memoria consumată în timpul decriptării AES256 normalizată')      
        graph_window = GraphWindow(fig,self)
        graph_window.show()
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
