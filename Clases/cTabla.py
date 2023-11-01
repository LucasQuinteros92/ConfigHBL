
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QFont
class Tabla(QTableWidget):
    def __init__(self,tabla : QTableWidget): 
        super().__init__()
        
        self.tabla = tabla
        
        self.tabla.horizontalHeader().stretchLastSection()
        #self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        #self.tabla.itemChanged.connect(self.changeItem)
    def addItem(self,nombre,valor = "",bold = False):
        key = QTableWidgetItem(nombre.rstrip())
        valor = QTableWidgetItem(valor.rstrip())
        key.setFlags(Qt.ItemFlag.ItemIsEnabled)
        
        font = QFont('Arial', 11)
        if bold :
            
            font.setBold(True)
            font.setWeight(75)
            
        key.setFont(font)
        valor.setFont(font)    
            
        row = self.tabla.rowCount() 
        self.tabla.insertRow(row)
        
        self.tabla.setItem(row,0,key)
        self.tabla.setItem(row,1,valor)
        
    def changeItem(self,nombre,valor):
        pass
    def borrar(self):
        self.tabla.setRowCount(0)
    def buscarItem(self,nombre,seccion):
        rows = self.tabla.rowCount()
        for row in range(rows):
            if seccion != "":
                if seccion == self.tabla.item(row,0).text().strip():
                    index = row
                    for rowi in range(index,rows):
                        if nombre == self.tabla.item(rowi,0).text().strip():
                            return [self.tabla.item(rowi,0).text().strip(),
                                    self.tabla.item(rowi,1).text().strip()]
            else:
                for row in range(rows):
                    if nombre == self.tabla.item(row,0).text().strip():
                        return [self.tabla.item(row,0).text().strip(),
                                self.tabla.item(row,1).text().strip()]
                
        return None