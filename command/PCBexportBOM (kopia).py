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
from PCBconf import exportList
from PySide import QtCore, QtGui


#***********************************************************************
#*                               GUI
#***********************************************************************
class exportBOM_Gui(QtGui.QWizard):
    ''' export bill of materials to one of supported formats '''
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        
        self.setWindowTitle(u"Export BOM")
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/data/img/exportBOM.png"))
        self.exportType = eval(exportList["csv"]['class'])
        ###
        self.addPage(self.formatPliku())
        self.addPage(self.ustawienia())
        #
        self.listaFormatow.setCurrentRow(0)
        self.button(QtGui.QWizard.FinishButton).clicked.connect(self.export)

    def export(self):
        ''' export bom to file '''
        FreeCAD.Console.PrintWarning('Exporting file\n')
        try:
            self.exportType.fullList = self.pelnaListaElementow.isChecked()
            self.exportType.export(str(self.pathToFile.text()))
            
            FreeCAD.Console.PrintWarning('End \n')
        except:
            FreeCAD.Console.PrintWarning('STOP \n')
        
    def zmianaProgramu(self):
        ''' change program - update program info '''
        program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
        
        self.exportType = eval(exportList[program]['class'])
        
        self.nazwaProgramu.setText(u'<b>Desc.: </b> ' + exportList[program]['desc'])
        self.formatPliku.setText(u'<b>Format: </b> ' + exportList[program]['format'])
        self.ikonaProgramu.setPixmap(QtGui.QPixmap(exportList[program]['icon']))
        self.pathToFile.setText(QtCore.QDir.homePath() + '/untitled.' + exportList[program]['format'].split('.')[1])

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
        for i, j in exportList.items():
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
        self.pelnaListaElementow = QtGui.QCheckBox('Full list')
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
        fileName = QtGui.QFileDialog().getSaveFileName(None, 'Export BOM', QtCore.QDir.homePath(), exportList[self.exportType.programName]['format'])
        if fileName[0]:
            fileName = fileName[0]
            program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
                
            if not fileName.endswith('.{0}'.format(exportList[program]['format'].split('.')[1])):
                fileName += '.{0}'.format(exportList[program]['format'].split('.')[1])
            
            self.pathToFile.setText(fileName)


#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class exportBOM:
    def __init__(self):
        self.fullList = False
        self.exportHeaders = ['ID', 'Package', 'Value', 'Quantity', 'X', 'Y', 'Rotation', 'Side']
    
    def fileExtension(self, path):
        extension = exportList[self.programName]['format'].split('.')[1]
        if not path.endswith(extension):
            path += '.{0}'.format(extension)
        
        return path
    
    def getParts(self):
        ''' get param from all packages from current document '''
        parts = {}
        
        doc = FreeCAD.activeDocument()
        if len(doc.Objects):
            for elem in doc.Objects:
                if hasattr(elem, "Proxy") and hasattr(elem.Proxy, "Type") and elem.Proxy.Type == 'partsGroup':  # objects
                    for i in elem.OutList:
                        if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:
                            if not i.Package in parts.keys():
                                parts[i.Package] = {}
                            if not '_'.join(i.PartValue.ViewObject.Text) in parts[i.Package].keys():
                                parts[i.Package]['_'.join(i.PartValue.ViewObject.Text)] = {}
                            parts[i.Package]['_'.join(i.PartValue.ViewObject.Text)]['_'.join(i.PartName.ViewObject.Text)] = {'side': i.Side, 'x': doc.getObject(i.Name).X.Value, 'y': doc.getObject(i.Name).Y.Value, 'z': doc.getObject(i.Name).Placement.Base.z, 'rot': doc.getObject(i.Name).Rot.Value}
        return parts


class html(exportBOM):
    ''' Export BOM to *.html '''
    def __init__(self, parent=None):
        exportBOM.__init__(self)
        
        self.programName = 'html'
        
    def addTitle(self):
        if not self.fullList:
            self.files.write('<tr><th>' + ('</th><th>').join(self.exportHeaders[:4]) + '</th></tr>\n')
        else:
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
        <p><h1>Bill of materials</h1></p>
        <p>
            <table>
         """)
        
    def fileFooter(self):
        self.files.write("""
            </table>
        </p>
        <div class='stopka'></div>
    </body>
</html>""".format())
    
    def export(self, fileName):
        '''export(filePath): save BOM to html file
            filePath -> strig
            filePath = path/fileName.html'''
        fileName = self.fileExtension(fileName)
        self.files = codecs.open(fileName, "w", "utf-8")
        self.fileHeader()
        self.addTitle()
        #
        self.exportParts(self.getParts())
        #
        self.fileFooter()
        self.files.close()
    
    def exportParts(self, parts):
        for i in parts.keys():
            for j in parts[i].keys():  # value
                if not self.fullList:
                    #files.write("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td style='text-align:center;'>{3}</td></tr>\n".format(i, j, ', '.join(elem[i][j].keys()), len(elem[i][j].keys())))
                    self.files.write("<tr style='text-align:center;'><td style='text-align:left;'>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\n".format(', '.join(parts[i][j].keys()), i, j, len(parts[i][j].keys())))
                else:
                    for k in parts[i][j].keys():
                        self.files.write("<tr style='text-align:center;'><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>\n".format(k, i, j, len(parts[i][j].keys()), parts[i][j][k]['x'], parts[i][j][k]['y'], parts[i][j][k]['rot'], parts[i][j][k]['side']))


class txt(exportBOM):
    ''' Export BOM to *.txt '''
    def __init__(self, parent=None):
        exportBOM.__init__(self)
        
        self.programName = 'txt'
    
    def addTitle(self, num):
        if not self.fullList:
            return self.exportHeaders[num]
        else:
            return self.exportHeaders[num]
    
    def export(self, fileName):
        '''export(filePath): save BOM to txt file
            filePath -> strig
            filePath = path/fileName.txt'''
        fileName = self.fileExtension(fileName)
        self.files = codecs.open(fileName, "w", "utf-8")
        #
        self.exportParts(self.getParts())
        #
        self.files.close()

    def exportParts(self, elem):
        #  get param.
        try:
            kolumny = [0, 0, 0, 0, 0, 0, 0, 0]
            for i in elem.keys():
                if len(i) > kolumny[0]:  # package
                    kolumny[0] = len(i)
                for j in elem[i].keys():
                    if len(j) > kolumny[1]:    # value
                        kolumny[1] = len(j)
                    
                    if not self.fullList:
                        if len(', '.join(elem[i][j].keys())) > kolumny[2]:    # part name
                            kolumny[2] = len(', '.join(elem[i][j].keys()))
                    else:
                        for k in elem[i][j].keys():
                            if len(k) > kolumny[2]:    # part name
                                kolumny[2] = len(k)
                            if len(str(elem[i][j][k]['x'])) > kolumny[4]:
                                kolumny[4] = len(str(elem[i][j][k]['x']))
                            if len(str(elem[i][j][k]['y'])) > kolumny[5]:
                                kolumny[5] = len(str(elem[i][j][k]['y']))
                            if len(str(elem[i][j][k]['rot'])) > kolumny[6]:
                                kolumny[6] = len(str(elem[i][j][k]['rot']))
                            if len(str(elem[i][j][k]['side'])) > kolumny[7]:
                                kolumny[7] = len(str(elem[i][j][k]['side']))
            # headers
            self.files.write(self.addTitle(0).ljust(kolumny[2] + 10))
            self.files.write(self.addTitle(1).ljust(kolumny[0] + 10))
            self.files.write(self.addTitle(2).ljust(kolumny[1] + 10))
            if self.fullList:
                self.files.write(self.addTitle(4).ljust(kolumny[4] + 10))
                self.files.write(self.addTitle(5).ljust(kolumny[5] + 10))
                self.files.write(self.addTitle(6).ljust(kolumny[6] + 10))
                self.files.write(self.addTitle(7).ljust(kolumny[7] + 10))
            self.files.write(self.addTitle(3))
            self.files.write("\n")
            # write param. to file
            for i in elem.keys():  # package
                for j in elem[i].keys():  # value
                    if not self.fullList:
                        self.files.write(', '.join(elem[i][j].keys()).ljust(kolumny[2] + 10))
                        self.files.write(str(i).ljust(kolumny[0] + 10))
                        self.files.write(str(j).ljust(kolumny[1] + 10))
                        self.files.write(str(len(elem[i][j].keys())))
                        self.files.write("\n")
                    else:
                        for k in elem[i][j].keys():
                            self.files.write(str(k).ljust(kolumny[2] + 10))
                            self.files.write(str(i).ljust(kolumny[0] + 10))
                            self.files.write(str(j).ljust(kolumny[1] + 10))
                            self.files.write(str(elem[i][j][k]['x']).ljust(kolumny[4] + 10))
                            self.files.write(str(elem[i][j][k]['y']).ljust(kolumny[5] + 10))
                            self.files.write(str(elem[i][j][k]['rot']).ljust(kolumny[6] + 10))
                            self.files.write(str(elem[i][j][k]['side']).ljust(kolumny[7] + 10))
                            self.files.write(str(len(elem[i][j].keys())))
                            self.files.write("\n")
        except Exception, e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))

class csv(exportBOM):
    ''' Export BOM to *.csv '''
    def __init__(self, parent=None):
        exportBOM.__init__(self)
        
        self.programName = 'csv'
        
    def addTitle(self):
        if not self.fullList:
            self.files.write((';').join(self.exportHeaders[:4]) + '\n')
        else:
            self.files.write((';').join(self.exportHeaders) + '\n')
    
    def export(self, fileName):
        '''export(filePath): save BOM to csv file
            filePath -> strig
            filePath = path/fileName.csv'''
        fileName = self.fileExtension(fileName)
        self.files = codecs.open(fileName, "w", "utf-8")
        self.addTitle()
        #
        self.exportParts(self.getParts())
        #
        self.files.close()
    
    def exportParts(self, parts):
        for i in parts.keys():  # package
            for j in parts[i].keys():  # value
                if not self.fullList:
                    self.files.write("{0};{1};{2};{3}\n".format(', '.join(parts[i][j].keys()), i, j, len(parts[i][j].keys())))
                else:
                    for k in parts[i][j].keys():
                        self.files.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(k, i, j, len(parts[i][j].keys()), parts[i][j][k]['x'], parts[i][j][k]['y'], parts[i][j][k]['rot'], parts[i][j][k]['side']))
