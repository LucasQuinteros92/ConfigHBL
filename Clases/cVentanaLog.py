

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal
from Paginas.Ui_log import Ui_Form

from Clases.cConexion import Conexion
from Clases.cConfig import Config
import time
class Log(QWidget):
    signalClose = pyqtSignal(str)
    def __init__(self,ssh,logname) -> None:
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ssh : Conexion = ssh
        self.logname = logname
        self.ssh.newMessage_handler = self.cargarItem
        
    def open(self):
        self.ui.logConsola.addItem(self.logname)
        self.show()
        self.ssh.comandoSSH2("tail -f -n 10 /home/pi/Desktop/Pruebas/PruebaWiegand/log/"+ self.logname)
        #self.ssh.comandoSSH("tail -f /home/pi/Desktop/Pruebas/PruebaWiegand/log/"+ self.logname)
        
    def cargarItem(self,item : str):
        item = QListWidgetItem(item)
        self.ui.logConsola.addItem(item)
        self.ui.logConsola.scrollToBottom()
        
    def closeEvent(self,event) -> None:
        self.signalClose.emit(self.logname)
        self.ssh.desconectarSSH()
        