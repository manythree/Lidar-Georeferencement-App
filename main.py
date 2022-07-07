import sys

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QListView, QMainWindow
import pandas as pd
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from PyQt5.uic import loadUi

# GUI FILE
from georeferencement_direct import Ui_MainWindow


class AnotherWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        #loadUi("georeferencement_direct.ui",self)
        self.fileGps = 0
        self.fileScan = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene)

        self.addToolBar(NavigationToolbar(self.ui.MplWidget.canvas, self))


        self.ui.parcourire1.clicked.connect(self.openFileNameDialog_GPS)

        self.ui.parcourire2.clicked.connect(self.openFileNameDialog_SCAN)

        var1=self.fileGps
        var2=self.fileScan
        self.geoRefData=0
        self.ui.run.clicked.connect(lambda: self.fonction_Georeferencement_direct(self.fileGps,self.fileScan))
        self.ui.export_2.clicked.connect(lambda: self.export(self.geoRefData))

    def export(self,data):
        self.dlg = QFileDialog(self)

        fileName = self.dlg.getSaveFileName(self,"save file","",".txt")
        print(fileName)
        df = pd.DataFrame(data)
        np.savetxt(r''+fileName[0]+'.txt', data, fmt='%d')



    def Afficher_figure3D(self,points_Georef):
        self.ui.progressBar.setValue(100)

        x=points_Georef[:,0]
        y=points_Georef[:,1]
        z=points_Georef[:,2]


        self.ui.MplWidget.canvas.axes.clear()
        #self.ui.MplWidget.canvas.scatter(x,y,z)
        self.ui.MplWidget.canvas.axes.plot(x,y,z,marker=".",markersize=0.5,linestyle="None")
        #self.ui.MplWidget.canvas.axes.plot(y)
        #self.ui.MplWidget.canvas.axes.plot(z)
        self.ui.MplWidget.canvas.axes.legend(('X', 'Y', 'Z'),loc='upper right')
        self.ui.MplWidget.canvas.axes.set_title('Mobile Mapping System')
        self.ui.MplWidget.canvas.draw()



        

    def fonction_Georeferencement_direct(self,gpsFile,scanFile):
        self.ui.progressBar.setValue(3)
        if len(gpsFile[0])!=0 or len(scanFile[0])!=0:
            dataGps=np.loadtxt(gpsFile[0], skiprows=1)
           

            datascan = []
            for i in range(len(scanFile[0])):
                newdf2=np.loadtxt(scanFile[0][i], skiprows=0)
                #fScan = pd.read_csv(''+scanFile[0][i]+'', " ")
                #newdf2 = pd.DataFrame(fScan)
                datascan.append(newdf2)
            print(datascan)
            print('\n----------------------length')
            print(len(datascan))
            print('\n----------------------')
            print(datascan[0][1])

            
            Nbr_points = 0
            profileNumber = 0 # les profiles 
             
            N = 0 
            #Determination de nombre des points
            for i in range(len(datascan)):
                N = N + len(datascan[i])
                print(N)
            pts_Georeference = np.zeros((N,3)) #ici ou vont etre stocker les données georeferncé
            
            
            
            for i in range(len(datascan)):#orientation profile 
                self.ui.progressBar.setValue(i)
                print("---1---------------------------------------\n")
                #print(datascan[i][:,1])
                print("---2---------------------------------------\n")
                
                Data =datascan[i][datascan[i][:,1].argsort(),]
                #print(Data)
                
                #les parametre de georeferncement direct initialisation
                bra_levier=np.array([0.14,0.249,-0.076])  #bras de levier
                rotation_scanner=np.array([[0,-1,0],[1,0,0],[0,0,1]]) #Matrice de rotation 
                profile = 0 # Indice de profile
                for j in range(len(Data)):
                        if j<80 :
                            self.ui.progressBar.setValue(j)
                        if Data[j,1]==profile: #La colonne 2 == indice de profile 

                            L = self.rotationX(dataGps[profileNumber+1,7]).dot(self.rotationY(dataGps[profileNumber+1,8])) 

                            
                            rotationGPS=L.dot(self.rotationZ((dataGps[profileNumber+1,9])))
                            x = Data[j,2:5].reshape(-1,1)  
                            y = bra_levier.reshape(-1,1)
                            z = rotation_scanner
                            pts_Georeference[Nbr_points+j,:]=dataGps[profileNumber+1,1:4]+(rotationGPS.dot(y+z.dot(x))).transpose() #Equation finale de georef
                        else:
                            #Incremantation profile
                            profile = profile+1
                            profileNumber=profileNumber+1
                            L = self.rotationX(dataGps[profileNumber+1,7]).dot(self.rotationY(dataGps[profileNumber+1,8]))
                            
                            rotationGPS=L.dot(self.rotationZ((dataGps[profileNumber+1,9])))
                            x = Data[j,2:5].reshape(-1,1)
                            y = bra_levier.reshape(-1,1)
                            z = rotation_scanner
                            pts_Georeference[Nbr_points+j,:]=dataGps[profileNumber+1,1:4]+(rotationGPS.dot(y+z.dot(x))).transpose()
                Nbr_points=Nbr_points+len(Data)
            print("/////////////////////////////////////////////////////////////\n")
            #print(pts_Georeference)
            self.geoRefData=pts_Georeference #on associe les données a un variable globale pour les exporter
            self.Afficher_figure3D(pts_Georeference)
            return pts_Georeference



   #retation selon X 
    def rotationX(self,thetaX):
        rotationX = np.array([[1, 0, 0], [0, np.cos(thetaX*(np.pi/180)), -np.sin(thetaX*(np.pi/180))],
                            [0, np.sin(thetaX*(np.pi/180)), np.cos(thetaX*(np.pi/180))]])
        return rotationX

    #retation selon Y 
    def rotationY(self,thetaY):
        rotationY = np.array([[np.cos(thetaY*(np.pi/180)), 0, np.sin(thetaY*(np.pi/180))], [0, 1, 0],
                            [-np.sin(thetaY*(np.pi/180)), 0, np.cos(thetaY*(np.pi/180))]])
        return rotationY

    #retation selon Z 
    def rotationZ(self,thetaZ):
            rotationZ = np.array([[np.cos(thetaZ*(np.pi/180)), -np.sin(thetaZ*(np.pi/180)), 0], [np.sin(thetaZ*(np.pi/180)),
                                                                    np.cos(thetaZ*(np.pi/180)), 0], [0, 0, 1]])
            return rotationZ
        

        

    #importation des données GPS
    def openFileNameDialog_GPS(self):
        
        self.dlg = QFileDialog(self)

        fileName = self.dlg.getOpenFileName(self, "Chose your files", "", "xyz Files (*.txt)")
        print(fileName)
        self.fileGps=fileName
        self.ui.lineEdit.setText(fileName[0].split('/')[-1])

        return



    #importation des données scanner
    def openFileNameDialog_SCAN(self):
        
        self.dlg = QFileDialog(self)
        fileNames = self.dlg.getOpenFileNames(
            self, "Chose your files", "", "xyz Files (*.xyz)")
        print(fileNames)
        self.fileScan=fileNames
        titles= ""
        for i in range(len(fileNames[0])):
                titles= titles +" | "+fileNames[0][i].split('/')[-1]
        self.ui.lineEdit2.setText(titles)
        """if len(fileNames[0])!=0:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.ui.lineEdit2.setText(str(len(fileNames[0]))+" files are selected")
            scanFile = []
            for i in range(len(fileNames[0])):
                fScan = pd.read_csv(''+fileNames[0][i]+'', " ")
                newdf2 = pd.DataFrame(fScan)
                scanFile.append(newdf2)
        
            #print(scanFile)
            # print(len(fileNames[0]))
            self.dlg.close()
        else:
            self.dlg.close()"""



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        loadUi("mainwindd.ui", self)

        self.pushButton.clicked.connect(self.show_new_window)
        # self.setCentralWidget(self.pushButton)

    def show_new_window(self, checked):
        if self.w is None:
            self.w = AnotherWindow()
        self.w.show()
        self.close()

import res
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
