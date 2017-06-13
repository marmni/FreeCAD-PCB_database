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
import Part
import os
import sys

from PCBconf import *
from PCBobjects import partObject, viewProviderPartObject, partObject_E, viewProviderPartObject_E
from PCBpartManaging import partsManaging
from PCBfunctions import getPCBsize
import unicodedata

if FreeCAD.GuiUp:
    #import FreeCADGui
    from PySide import QtCore, QtGui

from PCBgroups import createGroup_Parts
from PCBannotations import createAnnotation


class updateObjectTable(QtGui.QListWidget):
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        
        self.setFrameShape(QtGui.QFrame.NoFrame)
    
    def DeSelectAllObj(self, value):
        for i in range(self.count()):
            self.item(i).setCheckState(value)


class updateWizardWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.listaBibliotek = QtGui.QComboBox()
        
        libraryFrame = QtGui.QGroupBox(u'Library:')
        libraryFrameLay = QtGui.QHBoxLayout(libraryFrame)
        libraryFrameLay.addWidget(self.listaBibliotek)
        #
        self.listaElementow = updateObjectTable()

        przSelectAllT = QtGui.QPushButton('')
        przSelectAllT.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllT.setFlat(True)
        przSelectAllT.setIcon(QtGui.QIcon(":/data/img/checkbox_checked_16x16.png"))
        przSelectAllT.setToolTip('Select all')
        self.connect(przSelectAllT, QtCore.SIGNAL('pressed ()'), self.selectAllObj)
        
        przSelectAllTF = QtGui.QPushButton('')
        przSelectAllTF.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllTF.setFlat(True)
        przSelectAllTF.setIcon(QtGui.QIcon(":/data/img/checkbox_unchecked_16x16.PNG"))
        przSelectAllTF.setToolTip('Deselect all')
        self.connect(przSelectAllTF, QtCore.SIGNAL('pressed ()'), self.unselectAllObj)
        
        self.adjustParts = QtGui.QCheckBox(u'Adjust part name/value')
        
        #self.loadModelColors = QtGui.QCheckBox(u'Colorize elements')
        #self.loadModelColors.setChecked(True)
        
        packagesFrame = QtGui.QGroupBox(u'Packages:')
        packagesFrameLay = QtGui.QGridLayout(packagesFrame)
        packagesFrameLay.addWidget(przSelectAllT, 0, 0, 1, 1)
        packagesFrameLay.addWidget(przSelectAllTF, 1, 0, 1, 1)
        packagesFrameLay.addWidget(self.listaElementow, 0, 1, 3, 1)
        #
        lay = QtGui.QVBoxLayout()
        lay.addWidget(libraryFrame)
        lay.addWidget(packagesFrame)
        lay.addWidget(self.adjustParts)
        #lay.addWidget(self.loadModelColors)
        lay.setStretch(1, 10)
        self.setLayout(lay)
        #
        self.readLibs()

    def selectAllObj(self):
        ''' select all object on list '''
        self.listaElementow.DeSelectAllObj(QtCore.Qt.Checked)
    
    def unselectAllObj(self):
        ''' deselect all object on list '''
        self.listaElementow.DeSelectAllObj(QtCore.Qt.Unchecked)
    
    def readLibs(self):
        ''' read all available libs from conf file '''
        for i, j in supSoftware.items():
            if j['pathToBase'].strip() != "":
                if j['name'].strip() != "":
                    dbName = j['name'].strip()
                else:
                    dbName = i.strip()
                
                self.listaBibliotek.addItem(dbName)
                self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, i.lower(), QtCore.Qt.UserRole)
        self.listaBibliotek.setCurrentIndex(0)


class updateParts(partsManaging):
    ''' update 3d models of packages '''
    def __init__(self, parent=None, updateModel=None):
        self.form = updateWizardWidget()
        self.form.setWindowTitle('Update model')
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/updateParts.png"))
        self.updateModel = updateModel
        
        self.setDatabase()
    
    def open(self):
        ''' load all packages types to list '''
        packages = []
        for j in FreeCAD.activeDocument().Objects:
            if hasattr(j, "Proxy") and hasattr(j, "Type") and j.Proxy.Type in ["PCBpart", "PCBpart_E"] and not j.Package in packages:
                a = QtGui.QListWidgetItem(j.Package)
                a.setData(QtCore.Qt.UserRole, j.Package)
                a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                if self.updateModel:
                    if self.updateModel == j.Package:
                        a.setCheckState(QtCore.Qt.Checked)
                    else:
                        a.setCheckState(QtCore.Qt.Unchecked)
                else:
                    a.setCheckState(QtCore.Qt.Checked)
                
                self.form.listaElementow.addItem(a)
                packages.append(j.Package)

    def reject(self):
        return True
    
    def needsFullSpace(self):
        return True

    def isAllowedAlterSelection(self):
        return False

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return False

    def helpRequested(self):
        pass

    def accept(self):
        ''' update 3d models of packages '''
        #################################################################
        #        polaczyc z innymi podobnymi czesciami kodu !!!!!       #
        #################################################################
        packages = []
        for i in range(self.form.listaElementow.count()):
            if self.form.listaElementow.item(i).checkState() == 2:
                packages.append(str(self.form.listaElementow.item(i).data(QtCore.Qt.UserRole)))
        #################################################################
        if FreeCAD.activeDocument():
            doc = FreeCAD.activeDocument()
            #elem = []
            if len(doc.Objects):
                gruboscPlytki = getPCBsize()[1]
                #z_pos = gruboscPlytki
                z_pos = 0
                self.databaseType = self.form.listaBibliotek.itemData(self.form.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)
                for j in doc.Objects:
                    if hasattr(j, "Proxy") and hasattr(j, "Type") and j.Proxy.Type in ["PCBpart", "PCBpart_E"] and not j.KeepPosition  and j.Package in packages:
                        #i = [j.Label, j.Package, j.Value, j.X.Value, j.Y.Value, j.Rot.Value, j.Side, '']
                        i = [j.Label, j.Package, False, j.X.Value, j.Y.Value, j.Rot.Value, j.Side, '']
                        allSocked = 0
                        fileData = self.partExist(i[1], u"{0} {1} ({2})".format(i[0], i[2], i[1]))
                        
                        partNameTXT = partNameTXT_label = self.generateNewLabel(i[0])
                        if isinstance(partNameTXT, unicode):
                            partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')

                        if fileData[0]:
                            packageData = self.__SQL__.getValues(fileData[2])
                            filePath = fileData[1]
                            
                            pos_X = fileData[3][2]
                            pos_Y = fileData[3][3]
                            pos_Z = fileData[3][4]
                            pos_RX = fileData[3][5]
                            pos_RY = fileData[3][6]
                            pos_RZ = fileData[3][7]
                            ######### wartosc Z
                            rotateY = pos_RY
                            #if i[6] == 'BOTTOM':
                                #rotateY += 180
                                #z_pos = 0
                            #################################################################
                            ######### DODANIE PODSTAWKI
                            # dodajPodstawke - definicja zachowania dla danego obiektu
                            #   0 - brak podstawki
                            #   1 - dodanie podstawki
                            dodajPodstawke = False
                            if eval(packageData["add_socket"])[0] and allSocked == 0:
                                dial = QtGui.QMessageBox()
                                dial.setText(u"Add socket to part {0} (Package: {1}, Library: {2})?".format(partNameTXT, i[1], i[7]))
                                dial.setWindowTitle("Socket")
                                dial.setIcon(QtGui.QMessageBox.Question)
                                dial.addButton('No', QtGui.QMessageBox.RejectRole)
                                podstawkaTAK = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
                                zawszePodstawki = dial.addButton('Yes for all', QtGui.QMessageBox.YesRole)
                                nigdyPodstawki = dial.addButton('No for all', QtGui.QMessageBox.RejectRole)
                                dial.exec_()
                                
                                if dial.clickedButton() == nigdyPodstawki:
                                    allSocked = -1
                                elif dial.clickedButton() == zawszePodstawki:
                                    allSocked = 1
                                elif dial.clickedButton() == podstawkaTAK:
                                    dodajPodstawke = True
                                else:
                                    dodajPodstawke = False

                            if (dodajPodstawke or allSocked == 1) and eval(packageData["add_socket"])[0]:
                                if self.__SQL__.has_section(eval(packageData["add_socket"])[1]):  # sprawdzamy czy podana podstawka istnieje
                                    danePodstawki = self.__SQL__.getValues(eval(packageData["add_socket"])[1])
                                    
                                    if i[6] == 'BOTTOM':
                                        z_pos -= float(eval(danePodstawki["socket"])[1])
                                    else:
                                        z_pos += float(eval(danePodstawki["socket"])[1])
                                    PCB_EL.append([danePodstawki["name"], danePodstawki["name"], "", i[3], i[4], i[5], i[6], ""])
                                else:
                                    PCB_ER.append([danePodstawki["name"], danePodstawki["name"], "", ""])
                            ################################################################
                            ################################################################
                            # DODANIE OBIEKTU NA PLANSZE
                            if j.Proxy.Type == "PCBpart":
                                step_model = j
                                step_model.Shape = Part.read(filePath)
                                
                                offset_X = step_model.Proxy.offsetX
                                offset_Y = step_model.Proxy.offsetY
                            else:
                                step_model = doc.addObject("Part::FeaturePython", u"{0} ({1})".format(partNameTXT, fileData[3][0]))
                                step_model.Label = partNameTXT_label
                                step_model.Shape = Part.read(filePath)
                                partObject(step_model)
                                step_model.Package = u"{0}".format(fileData[3][0])
                                step_model.Proxy.offsetX = pos_X
                                step_model.Proxy.offsetY = pos_Y
                                
                                offset_X = 0
                                offset_Y = 0
                            ####
                            # rotate object according to (RX, RY, RZ) set by user
                            sX = step_model.Shape.BoundBox.Center.x * (-1) + step_model.Placement.Base.x
                            sY = step_model.Shape.BoundBox.Center.y * (-1) + step_model.Placement.Base.y
                            sZ = step_model.Shape.BoundBox.Center.z * (-1) + step_model.Placement.Base.z + gruboscPlytki / 2.
                            
                            rotateX = pos_RX
                            rotateZ = pos_RZ
                            pla = FreeCAD.Placement(step_model.Placement.Base, FreeCAD.Rotation(rotateX, rotateY, rotateZ), FreeCAD.Base.Vector(sX, sY, sZ))
                            step_model.Placement = pla
                            
                            ## placement object to 0, 0, PCB_size / 2. (X, Y, Z)
                            sX = step_model.Shape.BoundBox.Center.x * (-1) + step_model.Placement.Base.x
                            sY = step_model.Shape.BoundBox.Center.y * (-1) + step_model.Placement.Base.y
                            sZ = step_model.Shape.BoundBox.Center.z * (-1) + step_model.Placement.Base.z + gruboscPlytki / 2.

                            step_model.Placement.Base.x = sX + pos_X - offset_X
                            step_model.Placement.Base.y = sY + pos_Y - offset_Y
                            step_model.Placement.Base.z = sZ
                            
                            # move object to correct Z
                            step_model.Placement.Base.z = step_model.Placement.Base.z + (gruboscPlytki - step_model.Shape.BoundBox.Center.z) + pos_Z + z_pos
                            
                            #
                            if i[6] == 'BOTTOM':
                                # ROT Y - MIRROR
                                shape = step_model.Shape.copy()
                                shape.Placement = step_model.Placement
                                shape.rotate((0, 0, gruboscPlytki / 2.), (0.0, 1.0, 0.0), 180)
                                step_model.Placement = shape.Placement
                                
                                # ROT Z - VALUE FROM EAGLE
                                shape = step_model.Shape.copy()
                                shape.Placement = step_model.Placement
                                shape.rotate((0, 0, 0), (0.0, 0.0, 1.0), -i[5])
                                step_model.Placement = shape.Placement
                            else:
                                # ROT Z - VALUE FROM EAGLE
                                shape = step_model.Shape.copy()
                                shape.Placement = step_model.Placement
                                shape.rotate((0, 0, 0), (0.0, 0.0, 1.0), i[5])
                                step_model.Placement = shape.Placement
                            
                            # placement object to X, Y set in eagle
                            step_model.Placement.Base.x = step_model.Placement.Base.x + i[3]
                            step_model.Placement.Base.y = step_model.Placement.Base.y + i[4]
                            #######
                            #######
                            if j.Proxy.Type == "PCBpart_E":
                                step_model.X = step_model.Shape.BoundBox.Center.x
                                step_model.Y = step_model.Shape.BoundBox.Center.y
                                step_model.Proxy.offsetX = pos_X
                                step_model.Proxy.offsetY = pos_Y
                                step_model.Proxy.oldROT = i[5]
                                step_model.Rot = i[5]
                                
                                ######
                                ######
                                # part name object
                                # [txt, x, y, size, rot, side, align, spin, mirror, font]
                                if j.PartName:
                                    step_model.PartName = j.PartName
                                else:
                                    layerS = createAnnotation()
                                    layerS.Text = u"{0}".format(j.Label)
                                    layerS.defaultName = '{0}_Name'.format(j.Label)
                                    layerS.generate()
                                    
                                    step_model.PartName = layerS.Annotation
                                
                                if self.form.adjustParts.isChecked() and "adjust" in packageData.keys() and "Name" in eval(packageData["adjust"]).keys() and eval(packageData["adjust"])["Name"][0]:
                                    values = eval(packageData["adjust"])["Name"]
                                    
                                    step_model.PartName.Side = step_model.Side
                                    step_model.PartName.Rot = step_model.Rot.Value
                                    step_model.PartName.ViewObject.Align = str(values[7])
                                    step_model.PartName.ViewObject.Size = values[5]
                                    step_model.PartName.ViewObject.Spin = False
                                    
                                    if step_model.Side == "BOTTOM":
                                        x1 = self.odbijWspolrzedne(step_model.X.Value + values[2], step_model.X.Value)
                                        step_model.PartName.ViewObject.Mirror = True
                                        
                                        [xR, yR] = self.obrocPunkt2([x1, step_model.Y.Value + values[3]], [step_model.X.Value, step_model.Y.Value], -step_model.Rot.Value)
                                    else:
                                        step_model.PartName.ViewObject.Mirror = False
                                        
                                        [xR, yR] = self.obrocPunkt2([step_model.X.Value + values[2], step_model.Y.Value + values[3]], [step_model.X.Value, step_model.Y.Value], step_model.Rot.Value)
                                    
                                    step_model.PartName.X = xR
                                    step_model.PartName.Y = yR
                                    step_model.PartName.Z = values[4]
                                    
                                    step_model.PartName.ViewObject.Visibility = eval(values[1])
                                    step_model.PartName.ViewObject.Color = values[6]

                                # part value
                                # [txt, x, y, size, rot, side, align, spin, mirror, font]
                                if j.PartValue:
                                    step_model.PartValue = j.PartValue
                                else:
                                    layerS1 = createAnnotation()
                                    layerS1.defaultName = '{0}_Value'.format(j.Label)
                                    layerS1.Text = u""
                                    layerS1.generate()
                                    
                                    step_model.PartValue = layerS1.Annotation
                                
                                if self.form.adjustParts.isChecked() and "adjust" in packageData.keys() and "Value" in eval(packageData["adjust"]).keys() and eval(packageData["adjust"])["Value"][0]:
                                    values = eval(packageData["adjust"])["Value"]
                                    
                                    step_model.PartValue.Side = step_model.Side
                                    step_model.PartValue.Rot = step_model.Rot.Value
                                    step_model.PartValue.ViewObject.Align = str(values[7])
                                    step_model.PartValue.ViewObject.Size = values[5]
                                    step_model.PartValue.ViewObject.Spin = False
                                    
                                    if step_model.Side == "BOTTOM":
                                        x1 = self.odbijWspolrzedne(step_model.X.Value + values[2], step_model.X.Value)
                                        step_model.PartValue.ViewObject.Mirror = True
                                        
                                        [xR, yR] = self.obrocPunkt2([x1, step_model.Y.Value + values[3]], [step_model.X.Value, step_model.Y.Value], -step_model.Rot.Value)
                                    else:
                                        step_model.PartValue.ViewObject.Mirror = False
                                        
                                        [xR, yR] = self.obrocPunkt2([step_model.X.Value + values[2], step_model.Y.Value + values[3]], [step_model.X.Value, step_model.Y.Value], step_model.Rot.Value)
                                    
                                    step_model.PartValue.X = xR
                                    step_model.PartValue.Y = yR
                                    step_model.PartValue.Z = values[4]
                                    
                                    step_model.PartValue.ViewObject.Visibility = eval(values[1])
                                    step_model.PartValue.ViewObject.Color = values[6]
                                ######
                                viewProviderPartObject(step_model.ViewObject)
                            step_model.Proxy.update_Z = step_model.Placement.Base.z
                            ################################################################
                            ################################################################
                            #KOLORY DLA ELEMENTOW
                            if filePath.upper().endswith('.IGS') or filePath.upper().endswith('IGES'):
                                step_model = self.getColorFromIGS(filePath, step_model)
                            elif filePath.upper().endswith('.STP') or filePath.upper().endswith('STEP'):
                                step_model = self.getColorFromSTP(filePath, step_model)
                            #
                            if j.Proxy.Type == "PCBpart_E":
                                grp = createGroup_Parts()
                                grp.addObject(step_model)
                                #doc.removeObject(j.Name)
                                step_model.Label = partNameTXT_label
                                #FreeCAD.ActiveDocument.recompute()
                                
                        elif j.Proxy.Type == "PCBpart" and not fileData[0]:
                            ## DODANIE OBIEKTU NA PLANSZE
                            step_model = doc.addObject("Part::FeaturePython", u"{0} ({1})".format(partNameTXT, i[1]))
                            obj = partObject_E(step_model)
                            step_model.Label = partNameTXT_label
                            step_model.Package = "{0}".format(i[1])
                            #step_model.Value = "{0}".format(i[2])
                            #####
                            # placement object to X, Y set in eagle
                            step_model.Placement.Base.x = i[3] - j.Proxy.offsetX
                            step_model.Placement.Base.y = i[4] - j.Proxy.offsetX
                            
                            # move object to correct Z
                            step_model.Placement.Base.z = step_model.Placement.Base.z + gruboscPlytki
                            #####
                            step_model.Side = "{0}".format(i[6])
                            step_model.X = i[3] - j.Proxy.offsetX
                            step_model.Y = i[4] - j.Proxy.offsetX
                            step_model.Rot = i[5]
                            step_model.Proxy.update_Z = 0
                            
                            ######
                            ######
                            # part name object
                            # [txt, x, y, size, rot, side, align, spin, mirror, font]
                            if j.PartName:
                                step_model.PartName = j.PartName
                            else:
                                layerS = createAnnotation()
                                layerS.defaultName = '{0}_Name'.format(j.Label)
                                layerS.generate()
                                    
                                step_model.PartName = layerS.Annotation
                                step_model.PartName.ViewObject.Text = [u"{0}".format(j.Label)]
                                step_model.PartName.X = step_model.X - 1
                                step_model.PartName.Y = step_model.Y + 1
                                step_model.PartName.Z = 0
                                step_model.PartName.Side = step_model.Side
                                step_model.PartName.Rot = step_model.Rot
                                step_model.PartName.ViewObject.Text = j.Label
                                step_model.PartName.ViewObject.Align = "bottom-left"
                                step_model.PartName.ViewObject.Size = 1.27
                                step_model.PartName.ViewObject.Spin = False
                                step_model.PartName.ViewObject.Mirror = False
                                step_model.PartName.ViewObject.Visibility = True
                                step_model.PartName.ViewObject.Color = (1., 1., 1.)
                                
                            step_model.PartName.Z = 0
                            # part value
                            # [txt, x, y, size, rot, side, align, spin, mirror, font]
                            if j.PartValue:
                                step_model.PartValue = j.PartValue
                            else:
                                layerS1 = createAnnotation()
                                layerS1.defaultName = '{0}_Value'.format(j.Label)
                                layerS1.generate()
                                
                                step_model.PartValue = layerS1.Annotation
                                step_model.PartValue.ViewObject.Text = [u""]
                                step_model.PartValue.X = step_model.X - 1
                                step_model.PartValue.Y = step_model.Y - 1
                                step_model.PartValue.Side = step_model.Side
                                step_model.PartValue.Rot = step_model.Rot
                                step_model.PartValue.ViewObject.Text = j.Label
                                step_model.PartValue.ViewObject.Align = "bottom-left"
                                step_model.PartValue.ViewObject.Size = 1.27
                                step_model.PartValue.ViewObject.Spin = False
                                step_model.PartValue.ViewObject.Mirror = False
                                step_model.PartValue.ViewObject.Visibility = True
                                step_model.PartValue.ViewObject.Color = (1., 1., 1.)
                                
                            step_model.PartValue.Z = 0
                                
                            viewProviderPartObject_E(step_model.ViewObject)
                            #################################################################
                            grp = createGroup_Parts()
                            grp.addObject(step_model)
                            doc.removeObject(j.Name)
                            step_model.Label = partNameTXT_label
        FreeCAD.ActiveDocument.recompute()
        return True
