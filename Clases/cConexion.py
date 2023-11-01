import paramiko
import time
import re
import select
from threading import Thread,Event
import queue
class Conexion():
    def __init__(self, newMessage_handler = None):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.connected = False
        self.__running = True
        self.t = Thread(target=self.__run,daemon=False)
        self.t.start()
        self.q = queue.Queue() 
        self.messages = []
        self.newMessage_event = Event()
        self.newMessage_handler = newMessage_handler
    def __run(self):
        while self.__running:
            try:
                cmd = self.q.get(timeout=2)
                stdin, stdout, stderr = self.client.exec_command(cmd)
                stdin.close()
                
                #stdout.channel.settimeout(2)
                
                for line in iter(stdout.readline, ""):
                        #line = stdout.readline()
                        print(line, end="")
                        if self.newMessage_handler is not None:

                            self.newMessage_handler(line)
                        if "HBL READY" in line:
                            break
                
                    
            except Exception as e: 
                pass
        print("out")
    
    def stop(self):
        self.__running = False
    def conectarSSH(self,hostname,password):
        try: 
            self.client.connect(hostname,username="pi",password=password,timeout=1)
            self.sftp = self.client.open_sftp()
            self.connected = True
            return("Conectado a : "+ hostname)
        except paramiko.AuthenticationException:
            return("Authentication failed when connecting to "+ hostname)
            
        except paramiko.SSHException as e:
            return("Could not connect :"+ str(e))
        except Exception as e:
            return("Error:"+ str(e))

    def comandoSSH(self,comando,output = True):
        res = None
        exit = True
        #session = self.client.get_transport().open_session()
        try:
            if self.connected:
                stdin, stdout, stderr = self.client.exec_command(comando)                    
                res = stdout.read().decode() 
                        
        except paramiko.SSHException as e:
            res = "Error executing comando: "+comando+" "+ str(e)
        
        return res
    def desconectarSSH(self):
        
        self.client.close()
    
    def descargarSSH(self,archivo,destino):
        self.sftp.get(archivo,destino)
        
    def cargarSSH(self,archivo,destino):
        self.sftp.put(archivo,destino)
        
    def comandoSSH2(self,cmd):
        self.q.put(cmd)
        
        