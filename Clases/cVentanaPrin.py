
import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Paginas.Ui_mainwindow import Ui_MainWindow
from Clases.cTabla import Tabla
from Clases.cConexion import Conexion
from Clases.cConfig import Config
from Clases.cVentanaLog import Log
import json
import os
import subprocess

class VentanaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ssh = Conexion()
        self.config = Config()
        self.ui.setupUi(self)
        
        self.listLog = []
        self.fileName = "C:\\Users\\User\\Desktop\\ConfigHBL\\hbl.json"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkStatusHBL)
        
        
        self.tabla = Tabla(self.ui.JSONtableWidget)
        
        self.ui.conectarHBLButton.clicked.connect(self.conectarHBL)
        self.ui.desconectarHBLButton.clicked.connect(self.desconectarHBL)
        self.ui.startHblButton.clicked.connect(self.startHBL)
        self.ui.stopHblButton.clicked.connect(self.stopHBL)
        self.ui.examinarAction.triggered.connect(self.buscarArchivo)
        
        self.ui.ipHBLLineEdit.setText("172.30.2.53")
        
        self.ui.guardarCambiosPushButton.clicked.connect(self.guardarCambios)
        
        self.changeStatus("Desconectado")
        
    def reportar(self, mensaje):
        q = QMessageBox()
        q.setText(mensaje)
        q.setIcon(QMessageBox.Icon.Information)
        q.setWindowTitle("JSONViewer")
        q.exec()
        
    def startHBL(self):
        #res = self.ssh.comandoSSH2(f"cd {self.config.HBLfolder};sudo sh start.sh &")
        res = self.ssh.comandoSSH2(f"""cd;cd {self.config.HBLfolder};nohup sudo sh start.sh >foo.log 2>&1 </dev/null &""")
        #self.ssh.comandoSSH2(f"""cd;cd {self.config.HBLfolder}; tail -f foo.log""")
        self.ui.statusTag.setText("Cargando")
        self.timer.start(5000)
        
        
    def stopHBL(self):
        #res = self.ssh.comandoSSH2(f"sudo killall python3")
        res = self.ssh.comandoSSH2(f"cd;cd {self.config.HBLfolder};sudo sh stop.sh;sleep 3;sudo sh stop.sh")
        self.ui.statusTag.setText("Cargando")
        self.timer.start(5000)
        
    
    def changeStatus(self, status):
        if status == "Corriendo":
            self.ui.startHblButton.setDisabled(True)
            self.ui.stopHblButton.setDisabled(False)
            self.ui.statusTag.setText(status)
        elif status == "Cargando":
            self.ui.startHblButton.setDisabled(True)
            self.ui.stopHblButton.setDisabled(True)
            self.ui.statusTag.setText(status)
        elif status == "Detenido":
            self.ui.startHblButton.setDisabled(False)
            self.ui.stopHblButton.setDisabled(True)
            self.ui.statusTag.setText(status)
        elif status == "Conectado":
            self.ui.conectarHBLButton.setDisabled(True)
            self.ui.desconectarHBLButton.setDisabled(False)
            self.ui.guardarCambiosPushButton.setDisabled(False)
        elif status == "Desconectado":
            self.ui.conectarHBLButton.setDisabled(False)
            self.ui.desconectarHBLButton.setDisabled(True)
            self.ui.startHblButton.setDisabled(True)
            self.ui.stopHblButton.setDisabled(True)
            self.ui.statusTag.setText(status)
            self.ui.guardarCambiosPushButton.setDisabled(True)
        
    def conectarHBL(self):
        res = self.ssh.conectarSSH(self.ui.ipHBLLineEdit.text(),
                                   self.ui.pwdHBLLineEdit.text())
        
        self.reportar(res)
        if "Error" not in res:
            self.changeStatus("Conectado")
            self.checkStatusHBL()
            self.getLogs()
            self.descargarJSON()
            #self.mostrarArchivo(self.readJsonFile(self.fileName))
            #os.system("start /wait cmd")
            #print(res)
    def descargarJSON(self):
        try:
            self.ssh.descargarSSH(self.config.HBLfolder+"/modulos/hbl.json", 
                                  os.getcwd()+"\\hbl.json")
            self.mostrarArchivo(self.readJsonFile(os.getcwd() + '\\hbl.json' ))
            self.ui.JSONtableWidget.resizeColumnsToContents()
            
        except Exception as e:
            print(str(e))
            
    def getLogs(self):
        res = self.ssh.comandoSSH(f"cd {self.config.HBLfolder}/log; ls")
        res = res.split("\n")
        self.generarBotones(res)
        #print(res)
        
    def openLog(self,sender):
        
        sender = self.sender()
        if isinstance(sender ,QPushButton):
            ssh = Conexion()
            ssh.conectarSSH(self.ui.ipHBLLineEdit.text(),
                            self.ui.pwdHBLLineEdit.text())
            log = Log(ssh,sender.text())
            log.signalClose.connect(self.closeLog)
            log.open()
            self.listLog.append(log)
            
    def closeLog(self,logname):
        for i in range(self.listLog.__len__()):
            if self.listLog[i].logname == logname:
                pos = i
        self.listLog.pop(pos)

    def generarBoton(self,name,destino):
        button = QPushButton(name)
        button.clicked.connect(self.openLog)
        destino.addWidget(button)
        
    def generarBotones(self,lista):

        for nombre in lista:
            if nombre.strip():
                self.generarBoton(nombre,self.ui.gridLayoutButtons)
        
    def desconectarHBL(self):
        self.ssh.desconectarSSH()
        self.tabla.borrar()
        for i in  reversed(range(self.ui.gridLayoutButtons.count()) ):
            item = self.ui.gridLayoutButtons.itemAt(i)
            if item is not None:
                widget = item.widget()
                
                if widget is not None:
                    self.ui.gridLayoutButtons.removeWidget(widget)
        self.changeStatus("Desconectado")
    
    
    
    def closeEvent(self, event) -> None:
        self.ssh.stop()
        
    def checkStatusHBL(self):
        self.timer.stop()
        
        res = self.ssh.comandoSSH("ps -fA | grep python").split("\n")
        self.changeStatus("Detenido")
        for line in res:  
            if "python3"in line and "main.py" in line:
                self.changeStatus("Corriendo")

        
    def readJsonFile(self,filePath):
        
        with open(filePath) as file:
            JSONdict = json.load(file)
        
        return JSONdict
    
    def buscarArchivo(self):
        self.tabla.borrar()
        self.fileName, _ = QFileDialog.getOpenFileName(self,"a",r"", "JsonFiles (*.json)")
        if self.fileName:
            jsonDict = self.readJsonFile(self.fileName)
            self.mostrarArchivo(jsonDict)
        
    def mostrarArchivo(self,jsonDict : dict, tabs = 0):
        espacio = "    "
        for key in jsonDict.keys():
            if isinstance(jsonDict[key],dict):
                self.tabla.addItem(espacio*tabs+key ,bold=True)
                self.mostrarArchivo(jsonDict[key], tabs+1)
            else:
                self.tabla.addItem(espacio*tabs+key, jsonDict[key].__str__())
            
    def guardarCambios(self):
       
        jsonDict = self.readJsonFile(self.fileName)
        self.realizarCambiosEnDiccionario(jsonDict)
        with open(self.fileName,"w") as f:
            f.write(json.dumps(jsonDict,indent=5))
            
        self.tabla.borrar()
        self.mostrarArchivo(self.readJsonFile(self.fileName))
        try:
            self.ssh.cargarSSH(os.getcwd() + "\\hbl.json",self.config.HBLfolder + "/modulos/hbl.json" )
        except Exception as e:
            print(str(e))
            
    def realizarCambiosEnDiccionario(self, jsonDict : dict, nombreDict = ""):
        for key in jsonDict.keys():
            if isinstance(jsonDict[key],dict):
                
                self.realizarCambiosEnDiccionario(jsonDict[key],key)
            else:
                self.modificarValorSegunTabla(key,nombreDict,jsonDict)
                
    
    def modificarValorSegunTabla(self,key,nombreDict,jsonDict : dict):

        nombreEnTabla ,valorEnTabla = self.tabla.buscarItem(key,nombreDict)

        if valorEnTabla.__str__() != jsonDict[key].__str__():
            try:
                jsonDict[key] = type(jsonDict[key])(valorEnTabla)
                
            except Exception as e:
                self.popUp(f"La variable {nombreEnTabla} : tiene un tipo incorrecto \n deberia ser un {type(jsonDict[key])} {str(e)}")
            
    def popUp(self, mensaje):
        dlg = QMessageBox()
        #dlg.windowIcon(path)
        dlg.setIcon(QMessageBox.Icon.Critical)
        dlg.setWindowTitle("Error")
        dlg.setText(mensaje)
        
        dlg.exec()