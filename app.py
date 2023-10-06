
import sys,os, time
from flask import Flask, request, jsonify, g
from random import randint
import serial,serial.tools.list_ports
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton,
    QWidget, QGridLayout, QTextEdit, QGroupBox, QHBoxLayout, QComboBox, QLabel)
from PySide2.QtGui import QIcon, QScreen
import time
import random
import requests


application = Flask(__name__)

__prgm__ = 'Serial Monitor'
__version__ = '0.0.2'

def find_USB_device(USB_DEV_NAME=None):
    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    usb_port_list = [p[0] for p in myports]
    usb_device_list = [p[1] for p in myports]
    if USB_DEV_NAME is None:
        return myports
    else:
        USB_DEV_NAME=str(USB_DEV_NAME).replace("'","").replace("b","")
        for device in usb_device_list:
            if USB_DEV_NAME in device:
                print(device)
                usb_id = device[device.index("COM"):device.index("COM")+4]
            
                print("{} port is {}".format(USB_DEV_NAME,usb_id))
                return usb_id
                
class GroupClass(QGroupBox):
    def __init__(self,widget,title="Connection Configuration"):
        super().__init__(widget)
        self.widget=widget
        self.title=title
        self.sep="-"
        self.id=-1
        self.name=''
        self.portlist=find_USB_device()
        self.items=[p[0] for p in self.portlist]#["COM1","COM2"]
        self.serial=None
        #self.motionDict={"POSITION BASED":" Describe motion based on position","VELOCITY BASED":" Describe motion based on velocity", "LOOP":" Describe loop motion", "PINGPONG":" Describe pingpong motion", "INTERACTIF":" Describe interactive motion"}
        self.init()
        
    def init(self):
        self.setTitle(self.title)
        
        self.selectlbl = QLabel("Select port:")
        #label
        self.typeBox=QComboBox()
        self.typeBox.addItems(self.items)#database getMotionType()
        self.typeBox.setCurrentIndex(self.typeBox.count()-1)
        
        #btn
        button = QPushButton("Connect")
        button.clicked.connect(self.connect)
        #hbox.addWidget(button)
        sendBtn = QPushButton("send")
        sendBtn.clicked.connect(self.sendData)
        #hbox.addWidget(button)
        
        titlelbl=  QLabel("Enter")
        self.title = QLineEdit("")
        desclbl=QLabel("Console")
        self.desc = QTextEdit("")
        
        #self.add=QPushButton("Ajouter/Modifier")
        #self.add.clicked.connect(self.addItem)
        #self.rem=QPushButton("Supprimer")
        #self.rem.clicked.connect(self.remItem)
            
        self.fields=QGridLayout()
        self.fields.addWidget(self.selectlbl,0,0,1,1)
        self.fields.addWidget(self.typeBox,0,1,1,1)
        self.fields.addWidget(button,0,2,1,1)
        
        #self.fields.addWidget(titlelbl,1,0,1,1)
        #self.fields.addWidget(self.title,1,1,1,1)
        #self.fields.addWidget(sendBtn,1,2,1,1)
        self.fields.addWidget(desclbl,2,0,1,1)
        self.fields.addWidget(self.desc,3,1,1,1)
        #self.fields.addWidget(self.add,2,2,1,1)
        #self.fields.addWidget(self.rem,3,2,1,1)
        self.setLayout(self.fields)
    
    def connect(self):
        
        self.desc.setText("")
        self.desc.setText(">> trying to connect to port %s ..." % self.typeBox.currentText())
        #with serial.Serial(self.typeBox.currentText(), 115200, timeout=1) as self.serial:
        if self.serial is None:
            self.serial=serial.Serial(self.typeBox.currentText(), 115200, timeout=1)
            time.sleep(0.05)
            # Se hace un test para conseguir el peso máximo del bloque
            rango_inicial = 82
            rango_final = 90
            specific_number = 89
            test_waiting = 0
            while test_waiting == 0:
                for weight in range(rango_inicial, rango_final):
                    increment = random.uniform(0, 1)
                    # Verificar si el número es igual al número específico
                    answer = weight + increment
                    self.desc.setText("{} kg\n".format(str(answer)))
                    if answer >= specific_number:
                        self.desc.setText("Peso: {} kg\n".format(str(answer)))
                        # send weight to endpoint
                        endpoint = "https://hackaton-app-adb544603f0d.herokuapp.com/measure_weight?weight=%s" % str(round(answer, 4))
                        print(endpoint, 'ENDPOINT')
                        requests.get(endpoint)
                        # end proccess
                        test_waiting = 1
                        break
                    time.sleep(0.2)
        else:
            self.desc.setText(">> {} already Opened!\n".format(self.typeBox.currentText()))
            
    def sendData(self):
        if self.serial.isOpen():
            if self.title.text() != "":
                self.serial.write(self.title.text().encode())
                answer=self.readData()
                if(self.title.text().encode()=="scan"):
                    print("scanning results -> "+answer.find("0x"))
                else:
                    print(answer.find("0x"))
                self.desc.setText(self.desc.toPlainText()+"\n"+answer)
                    
    def readData(self):
        #self.serial.flush() # it is buffering. required to get the data out *now*
        answer=""
        #print(self.serial.inWaiting(), 'SERIAL WAITING')
        test_waiting = 0
        while test_waiting == 0: #self.serial.readable() and
            rango_inicial = 82
            rango_final = 90
            specific_number = 89

            for number_found in range(rango_inicial, rango_final):
                increment = random.uniform(0, 1)
                # Verificar si el número es igual al número específico
                answer = number_found + increment
                self.desc.setText("{} kg\n".format(str(answer)))
                if answer >= specific_number:
                    self.desc.setText("Peso: {} kg\n".format(str(answer)))
                    test_waiting = 1
                    break  # Detener el proceso si se alcanza el número específico
                time.sleep(0.2)

            #answer += "\n"+str(self.serial.readline()).replace("\\r","").replace("\\n","").replace("'","").replace("b","")
            #print(self.serial.inWaiting())
        #self.desc.setText(self.desc.toPlainText()+"\n"+answer)
        return answer    
    
            
class SerialInterface(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.width=650
        self.height=350
        
        self.resize(self.width, self.height)
        self.setWindowTitle(__prgm__)
        
        #center window on screen
        qr = self.frameGeometry()
        cp = QScreen().availableGeometry().center()
        qr.moveCenter(cp)
        
        
        #init layout
        centralwidget = QWidget(self)
        centralLayout=QHBoxLayout(centralwidget)
        self.setCentralWidget(centralwidget)
        
        #add connect group
        self.connectgrp=GroupClass(self)
        centralLayout.addWidget(self.connectgrp)
        
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    frame = SerialInterface()
    frame.show()
    sys.exit(app.exec_())
