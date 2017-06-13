# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          *
#*   Printed Circuit Board Workbench for FreeCAD             PCB            *
#*   Flexible Printed Circuit Board Workbench for FreeCAD    FPCB           *
#*   Copyright (c) 2013, 2014, 2015                                         *
#*   marmni <marmni@onet.eu>                                                *
#*                                                                          *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU Lesser General Public License (LGPL)     *
#*   as published by the Free Software Foundation; either version 2 of      *
#*   the License, or (at your option) any later version.                    *
#*   for detail see the LICENCE text file.                                  *
#*                                                                          *
#*   This program is distributed in the hope that it will be useful,        *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
#*   GNU Library General Public License for more details.                   *
#*                                                                          *
#*   You should have received a copy of the GNU Library General Public      *
#*   License along with this program; if not, write to the Free Software    *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307   *
#*   USA                                                                    *
#*                                                                          *
#****************************************************************************

import FreeCAD
import os
import codecs
from PCBconf import exportListHoles
from PySide import QtCore, QtGui


#***********************************************************************
#*                               GUI
#***********************************************************************
class exportHoles_Gui(QtGui.QWizard):
    ''' export bill of materials to one of supported formats '''
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        
        self.setWindowTitle(u"Export hole locations")
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/data/img/drill-icon.png"))
        self.exportType = eval(exportListHoles["csv"]['class'])
        ###
        self.addPage(self.formatPliku())
        self.addPage(self.ustawienia())
        #
        self.listaFormatow.setCurrentRow(0)
        self.button(QtGui.QWizard.FinishButton).clicked.connect(self.export)

    def export(self):
        ''' export holes to file '''
        FreeCAD.Console.PrintWarning('Exporting file\n')
        try:
            self.exportType.groupList = self.pelnaListaElementow.isChecked()
            self.exportType.export(str(self.pathToFile.text()))
            
            FreeCAD.Console.PrintWarning('End \n')
        except Exception, e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
            FreeCAD.Console.PrintWarning('STOP \n')

    def zmianaProgramu(self):
        ''' change program - update program info '''
        program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
        
        self.exportType = eval(exportListHoles[program]['class'])
        self.exportType.parent = self
        self.nazwaProgramu.setText(u'<b>Desc.: </b> ' + exportListHoles[program]['desc'])
        self.formatPliku.setText(u'<b>Format: </b> ' + exportListHoles[program]['format'])
        self.ikonaProgramu.setPixmap(QtGui.QPixmap(exportListHoles[program]['icon']))
        self.pathToFile.setText(QtCore.QDir.homePath() + '/untitled.' + exportListHoles[program]['format'].split('.')[1])
        
        if not 'group' in exportListHoles[program]['exportLayers']:
            self.pelnaListaElementow.setChecked(False)
            self.pelnaListaElementow.setDisabled(True)

    def formatPliku(self):
        ''' choose output file format '''
        page = QtGui.QWizardPage()
        page.setSubTitle(u"<span style='font-weight:bold;font-size:13px;'>File format</span>")
        #
        self.nazwaProgramu = QtGui.QLabel()
        self.formatPliku = QtGui.QLabel()

        self.ikonaProgramu = QtGui.QLabel()
        self.ikonaProgramu.setFixedSize(120, 120)
        self.ikonaProgramu.setAlignment(QtCore.Qt.AlignCenter)
        #
        self.listaFormatow = QtGui.QListWidget()
        for i, j in exportListHoles.items():
            a = QtGui.QListWidgetItem(j['name'])
            a.setData(QtCore.Qt.UserRole, i)
            
            self.listaFormatow.addItem(a)
        QtCore.QObject.connect(self.listaFormatow, QtCore.SIGNAL("currentRowChanged (int)"), self.zmianaProgramu)
        #
        lay = QtGui.QGridLayout(page)
        lay.addWidget(self.listaFormatow, 0, 0, 4, 1)
        lay.addWidget(self.ikonaProgramu, 0, 1, 1, 1, QtCore.Qt.AlignCenter)
        lay.addWidget(self.nazwaProgramu, 1, 1, 1, 1)
        lay.addWidget(self.formatPliku, 2, 1, 1, 1)
        lay.setHorizontalSpacing(20)
        return page
        
    def ustawienia(self):
        ''' settings '''
        page = QtGui.QWizardPage()
        page.setSubTitle(u"<span style='font-weight:bold;font-size:13px;'>Settings</span>")
        #
        self.pathToFile = QtGui.QLineEdit('')
        self.pathToFile.setReadOnly(True)
        
        zmianaSciezki = QtGui.QPushButton('...')
        zmianaSciezki.setToolTip(u'Change path')
        QtCore.QObject.connect(zmianaSciezki, QtCore.SIGNAL("pressed ()"), self.zmianaSciezkiF)
        #
        self.pelnaListaElementow = QtGui.QCheckBox('Group holes by diameter')
        #
        lay = QtGui.QGridLayout(page)
        lay.addWidget(QtGui.QLabel(u'Path: '), 0, 0, 1, 1)
        lay.addWidget(self.pathToFile, 0, 1, 1, 1)
        lay.addWidget(zmianaSciezki, 0, 2, 1, 1)
        lay.addWidget(self.pelnaListaElementow, 1, 0, 3, 1)
        lay.setColumnStretch(1, 5)
        return page

    def zmianaSciezkiF(self):
        ''' change output file path '''
        fileName = QtGui.QFileDialog().getSaveFileName(None, 'Export BOM', QtCore.QDir.homePath(), exportListHoles[self.exportType.programName]['format'])
        if fileName[0]:
            fileName = fileName[0]
            program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
                
            if not fileName.endswith('.{0}'.format(exportListHoles[program]['format'].split('.')[1])):
                fileName += '.{0}'.format(exportListHoles[program]['format'].split('.')[1])
            
            self.pathToFile.setText(fileName)


#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class exportHoles:
    def __init__(self):
        self.groupList = False
        self.exportHeaders = ['Diameter', 'X', 'Y']
    
    def fileExtension(self, path):
        extension = exportListHoles[self.programName]['format'].split('.')[1]
        if not path.endswith(extension):
            path += '.{0}'.format(extension)
        
        return path
    
    def getHoles(self):
        ''' get param from all packages from current document '''
        holes = {}
        
        try:
            pcbHoles = FreeCAD.ActiveDocument.Board.Holes
            
            for i in pcbHoles.Geometry:
                if str(i.__class__) == "<type 'Part.GeomCircle'>":
                    D = i.Radius * 2.0
                    X = i.Center[0]
                    Y = i.Center[1]
                    
                    if not D in holes.keys():
                        holes[D] = []
                    
                    holes[D].append([X, Y])
        except:
            pass
        
        return holes


class html(exportHoles):
    ''' Export BOM to *.html '''
    def __init__(self, parent=None):
        exportHoles.__init__(self)
        
        self.programName = 'html'
        
    def addTitle(self):
        self.files.write('<tr><th>' + ('</th><th>').join(self.exportHeaders) + '</th></tr>\n')
    
    def fileHeader(self):
        self.files.write("""<html>
    <head>
        <style tyle="text/css">
            body {cursor: default !important;}
            table {margin: 0 auto;}
            table td, table th {padding:5px 10px;}
            table tr:nth-child(odd) {background:#E6E6DC;}
            table tr:nth-child(1) {background:#00628B !important; font-weight: bold.}
            table tr:hover {background:#81A594;}
            .stopka {font-weight:bold; font-size: 12px; background: #fff; padding: 5px;}
        </style>
    </head>
    <body>
        <p><h1>Hole locations</h1></p>
        <p>
            <table>
         """)
        
    def fileFooter(self):
        self.files.write("""
            </table>
        </p>
        <div class='stopka'></div>
    </body>
</html>""")
    
    def export(self, fileName):
        '''export(filePath): save holes to html file
            filePath -> strig
            filePath = path/fileName.html'''
        fileName = self.fileExtension(fileName)
        self.files = codecs.open(fileName, "w", "utf-8")
        self.fileHeader()
        self.addTitle()
        #
        self.exportHoles(self.getHoles())
        #
        self.fileFooter()
        self.files.close()
    
    def exportHoles(self, elem):
        for i in elem.keys():
            if self.groupList:
                self.files.write("<tr><td>{0}</td><td></td><td></td></tr>\n".format(i))
            for j in elem[i]:
                if self.groupList:
                    self.files.write("<tr><td></td><td>{0}</td><td>{1}</td></tr>\n".format(j[0], j[1]))
                else:
                    self.files.write("<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>\n".format(i, j[0], j[1]))


class txt(exportHoles):
    ''' Export BOM to *.txt '''
    def __init__(self, parent=None):
        exportHoles.__init__(self)
        
        self.programName = 'txt'
    
    def addTitle(self, num):
        return self.exportHeaders[num]
        
    def export(self, fileName):
        '''export(filePath): save holes to txt file
            filePath -> strig
            filePath = path/fileName.txt'''
        fileName = self.fileExtension(fileName)
        self.files = codecs.open(fileName, "w", "utf-8")
        #
        self.exportHoles(self.getHoles())
        #
        self.files.close()

    def exportHoles(self, elem):
        #  get param.
        kolumny = [0, 0, 0]
        for i in elem.keys():
            if len(str(i)) > kolumny[0]:  # diameter
                kolumny[0] = len(str(i))
            
            for j in elem[i]:
                if len(str(j[0])) > kolumny[1]:    # x
                    kolumny[1] = len(str(j[0]))
                if len(str(j[1])) > kolumny[2]:    # y
                    kolumny[2] = len(str(j[1]))
        # headers
        self.files.write(self.addTitle(0).ljust(kolumny[0] + 10))
        self.files.write(self.addTitle(1).ljust(kolumny[1] + 10))
        self.files.write(self.addTitle(2).ljust(kolumny[2] + 10))
        self.files.write("\n")
        # write param. to file
        for i in elem.keys():  # package
            if self.groupList:
                self.files.write(str(i).ljust(kolumny[0] + 10))
                self.files.write("\n")
            
            for j in elem[i]:  # value
                if self.groupList:
                    self.files.write(str(' ').ljust(kolumny[0] + 10))
                else:
                    self.files.write(str(i).ljust(kolumny[0] + 10))
                self.files.write(str(j[0]).ljust(kolumny[1] + 10))
                self.files.write(str(j[1]).ljust(kolumny[2] + 10))
                self.files.write("\n")


class csv(exportHoles):
    ''' Export holes to *.csv '''
    def __init__(self, parent=None):
        exportHoles.__init__(self)
        
        self.programName = 'csv'
        
    def addTitle(self):
        self.files.write((';').join(self.exportHeaders) + '\n')
        
    def export(self, fileName):
        '''export(filePath): save holes to csv file
            filePath -> strig
            filePath = path/fileName.csv'''
        fileName = self.fileExtension(fileName)
        self.files = codecs.open(fileName, "w", "utf-8")
        self.addTitle()
        #
        self.exportHoles(self.getHoles())
        #
        self.files.close()
        
    def exportHoles(self, elem):
        for i in elem.keys():
            if self.groupList:
                self.files.write("{0};;\n".format(i))
            for j in elem[i]:
                if self.groupList:
                    self.files.write(";{0};{1}\n".format(j[0], j[1]))
                else:
                    self.files.write("{0};{1};{2}\n".format(i, j[0], j[1]))


class drl(exportHoles):
    ''' Export holes to *.csv '''
    def __init__(self, parent=None):
        exportHoles.__init__(self)
        
        self.programName = 'drl'

    def export(self, fileName):
        pass
