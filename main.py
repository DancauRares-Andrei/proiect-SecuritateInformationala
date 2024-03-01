import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from db import *
from main_window_ui import Ui_Dialog 

class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.init_list_widget_cheie()
        self.ui.listWidget_framework.addItems(["OpenSSL","LibreSSL","Themis","GnuTLS"])
        self.ui.pushButton_stergere_cheie.clicked.connect(self.pushButton_stergere_cheie_clicked)
        self.ui.pushButton_add_cheie.clicked.connect(self.open_key_input_window)
        self.ui.pushButton_actualizare_cheie.clicked.connect(self.update_key_input_window)
    def pushButton_stergere_cheie_clicked(self):
        selected_item = self.ui.listWidget_chei.currentItem()
        if selected_item:
            if " " in selected_item.text():
                cheieCript,cheieDecript=selected_item.text().split(" ")
                cheie=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieDecript))
                cheie.delete_instance()
                self.init_list_widget_cheie()
            else:
                cheieCript=selected_item.text()
                cheie=Chei.get((Chei.CheieCriptare==cheieCript) & (Chei.CheieDecriptare==cheieCript))
                cheie.delete_instance()
                self.init_list_widget_cheie()
            QMessageBox.information(None, "Ștergere efectuată!", "Cheie ștearsă cu succes! ")
        else:
             QMessageBox.warning(self, "Avertisment", "Nu ați selectat niciun element!", QMessageBox.Ok)    
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
                if not " " in key1 and " " not in key2:
                    if " " not in cheie_veche and key1!=key2:
                        QMessageBox.warning(self, "Avertisment", "Nu pot înlocui o cheie simetrică cu o pereche de chei asimetrice!", QMessageBox.Ok)
                    elif " " in cheie_veche and key1==key2:
                        QMessageBox.warning(self, "Avertisment", "Este de preferat să nu se înlocuiască o pereche de chei asimentrice cu o cheie simetrică!", QMessageBox.Ok)
                    else:
                        if " " in selected_item.text():
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
            if not " " in key1 and " " not in key2:
                cheie=Chei.create(
                CheieCriptare=key1,
                CheieDecriptare=key2
                )
                self.init_list_widget_cheie()
                QMessageBox.information(self, "Chei introduse", f"S-a adăugat cu succes la baza de date!", QMessageBox.Ok)              
            else:
                QMessageBox.warning(self, "Avertisment", "Cheile nu pot conține spații!", QMessageBox.Ok)    
        else:
            QMessageBox.warning(self, "Avertisment", "Nu ați introdus ambele chei", QMessageBox.Ok)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

