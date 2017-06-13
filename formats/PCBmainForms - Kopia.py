# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          *
#*   EaglePCB_2_FreeCAD                                                     *
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
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui

from math import sin, cos, sqrt
import Draft
import Part
#import re
import os
import sys
#from dataBase import dataBase
import __builtin__
from PCBconf import *
from PCBpartManaging import partsManaging
from PCBobjects import partObject, viewProviderPartObject, partObject_E, viewProviderPartObject_E

__currentPath__ = os.path.dirname(os.path.abspath(__file__))

try:
    sys.path.append(__currentPath__ + "/command")
    from PCBmakeGroup import makeUnigueGroup
except:
    sys.path.append(__currentPath__ + "/../command")
    from PCBmakeGroup import makeUnigueGroup


class dialogMAIN_FORM(QtGui.QDialog):
    def __init__(self, filename=None, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle(u"PCB settings")
        self.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        #
        self.plytkaPCB = QtGui.QCheckBox(u"Board")
        self.plytkaPCB.setDisabled(True)
        self.plytkaPCB.setChecked(True)
        #######
        self.gruboscPlytki = QtGui.QDoubleSpinBox(self)
        self.gruboscPlytki.setSingleStep(0.1)
        self.gruboscPlytki.setValue(1.6)
        self.gruboscPlytki.setSuffix(u" mm")
        #######
        self.plytkaPCB_otwory = QtGui.QCheckBox(u"Holes")
        self.plytkaPCB_otwory.setChecked(True)
        #######
        #self.plytkaPCB_PADS = QtGui.QCheckBox(u"Vias")
        #self.plytkaPCB_PADS.setChecked(True)
        #######
        self.plytkaPCB_plikER = QtGui.QCheckBox(u"Generate report with unknown parts")
        self.plytkaPCB_plikER.setChecked(False)
        #######
        self.plytkaPCB_elementy = QtGui.QCheckBox(u"Parts")
        self.plytkaPCB_elementy.setChecked(True)
        #######
        self.plytkaPCB_elementyKolory = QtGui.QCheckBox(u"Colorize elements")
        self.plytkaPCB_elementyKolory.setChecked(True)
        #######
        #######
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_plikER.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_plikER.setEnabled)
        
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_elementyKolory.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_elementyKolory.setEnabled)
        #######
        #######
        #przyciski
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton(u"Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton(u"Accept", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        self.spisWarstw = tabela()
        self.spisWarstw.setColumnCount(5)
        self.spisWarstw.setHorizontalHeaderLabels(["", u"ID", "", "", u"Name"])
        self.spisWarstw.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().resizeSection(0, 25)
        self.spisWarstw.horizontalHeader().resizeSection(1, 35)
        self.spisWarstw.horizontalHeader().resizeSection(2, 35)
        self.spisWarstw.horizontalHeader().resizeSection(3, 55)
        #######
        lay = QtGui.QGridLayout()
        lay.addWidget(self.spisWarstw, 0, 0, 7, 1)
        lay.addWidget(QtGui.QLabel(u"PCB Thickness"), 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        lay.addWidget(self.gruboscPlytki, 0, 2, 1, 1)
        lay.addWidget(self.plytkaPCB, 1, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_otwory, 2, 1, 1, 2)
        #lay.addWidget(self.plytkaPCB_PADS, 3, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_elementy, 3, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_elementyKolory, 4, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_plikER, 5, 1, 1, 2)
        lay.addItem(QtGui.QSpacerItem(10, 20), 6, 1, 1, 2)
        lay.addWidget(buttons, 8, 0, 1, 3, QtCore.Qt.AlignRight)
        lay.setRowStretch(6, 10)
        lay.setColumnMinimumWidth(0, 250)
        lay.setColumnMinimumWidth(1, 120)
        self.setLayout(lay)
        
    def spisWarstwAddRow(self, ID, layerColor, layerTransparent, layerName):
        self.spisWarstw.insertRow(self.spisWarstw.rowCount())
        
        check = QtGui.QCheckBox()
        check.setStyleSheet("QCheckBox {margin:7px;}")
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 0, check)
        #
        num = QtGui.QTableWidgetItem(str(ID))
        num.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.spisWarstw.setItem(self.spisWarstw.rowCount() - 1, 1, num)
        #
        if layerColor:
            color = kolorWarstwy()
            color.setColor(layerColor)
            color.setToolTip(u"Click to change color")
        else:
            color = QtGui.QLabel("")
        
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 2, color)
        #
        if layerTransparent:
            transparent = transpSpinBox()
            transparent.setValue(layerTransparent)
        else:
            transparent = QtGui.QLabel("")
        
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 3, transparent)
        #
        name = QtGui.QTableWidgetItem(layerName)
        name.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        name.setToolTip(u"Click to change name")
        self.spisWarstw.setItem(self.spisWarstw.rowCount() - 1, 4, name)


class transpSpinBox(QtGui.QSpinBox):
    def __init__(self, parent=None):
        QtGui.QSpinBox.__init__(self, parent)
        
        self.setRange(0, 100)
        self.setSuffix("%")
        self.setStyleSheet('''
            QSpinBox
            {
              border:0px;
            }
        ''')


class tabela(QtGui.QTableWidget):
    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self, parent)

        self.setSortingEnabled(False)
        #self.setGridStyle(Qt.NoPen)
        self.setShowGrid(False)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setStyleSheet('''
            QTableWidget QHeaderView
            {
                border:0px;
            }
            QTableWidget
            {
                border: 1px solid #9EB6CE;
                border-top:0px;
            }
            QTableWidget QHeaderView::section
            {
                color:#4C4161;
                font-size:12px;
                border:1px solid #9EB6CE;
                border-left:0px;
                padding:5px 0;
            }
        ''')


class kolorWarstwy(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.setStyleSheet('''
            QPushButton
            {
                border: 1px solid #000;
                background-color: rgb(255, 0, 0);
                margin: 1px;
            }
        ''')
        self.setFlat(True)
        #self.setFixedSize(20, 20)
        self.kolor = [0., 0., 0.]
        #
        self.connect(self, QtCore.SIGNAL("released ()"), self.pickColor)
        
    def setColor(self, nowyKolorRGB):
        self.kolor = nowyKolorRGB
        self.setStyleSheet('''
            QPushButton
            {
                border: 1px solid #000;
                background-color: rgb(%i, %i, %i);
                margin: 1px;
            }
        ''' % (nowyKolorRGB[0],
               nowyKolorRGB[1],
               nowyKolorRGB[2]))
    
    def pickColor(self):
        pick = QtGui.QColorDialog(QtGui.QColor(self.kolor[0], self.kolor[1], self.kolor[2]))
        if pick.exec_():
            [R, G, B, A] = pick.selectedColor().getRgb()
            self.setColor([R, G, B])

    def getColor(self):
        R = float(self.kolor[0] / 255.)
        G = float(self.kolor[1] / 255.)
        B = float(self.kolor[2] / 255.)
        return (R, G, B)


class mainPCB(partsManaging):
    def __init__(self, parent=None):
        self.projektBRD = None
        
    def arc3point(self, stopAngle, startAngle, radius, cx, cy):
        d = stopAngle - startAngle
        offset = 0
        if d < 0.0:
            offset = 3.14
        x3 = cos(((startAngle + stopAngle) / 2.) + offset) * radius + cx
        y3 = -sin(((startAngle + stopAngle) / 2.) + offset) * radius + cy
        
        return [x3, y3]

    def generateOctagon(self, x, y, diameter):
        pP = diameter / 2.
        zP = diameter / (2 + (sqrt(2)))
        aP = diameter * (sqrt(2) - 1)
        
        return [[x - pP + zP, y - pP, 0, x - pP + zP + aP, y - pP, 0],
                [x - pP + zP + aP, y - pP, 0, x + pP, y - pP + zP, 0],
                [x + pP, y - pP + zP, 0, x + pP, y - pP + zP + aP, 0],
                [x + pP, y - pP + zP + aP, 0, x + pP - zP, y + pP, 0],
                [x + pP - zP, y + pP, 0, x + pP - zP - aP, y + pP, 0],
                [x + pP - zP - aP, y + pP, 0, x - pP, y + pP - zP, 0],
                [x - pP, y + pP - zP, 0, x - pP, y + pP - zP - aP, 0],
                [x - pP, y + pP - zP - aP, 0, x - pP + zP, y - pP, 0]]
                
    #def regenerateOctagon(self, pp):
        #return [
                #[pp[0][0], pp[0][1], 0, pp[1][0], pp[1][1], 0],
                #[pp[1][0], pp[1][1], 0, pp[2][0], pp[2][1], 0],
                #[pp[2][0], pp[2][1], 0, pp[3][0], pp[3][1], 0],
                #[pp[3][0], pp[3][1], 0, pp[4][0], pp[4][1], 0],
                #[pp[4][0], pp[4][1], 0, pp[5][0], pp[5][1], 0],
                #[pp[5][0], pp[5][1], 0, pp[6][0], pp[6][1], 0],
                #[pp[6][0], pp[6][1], 0, pp[7][0], pp[7][1], 0],
                #[pp[7][0], pp[7][1], 0, pp[0][0], pp[0][1], 0]
                #]
        
    def obrocPunkt(self, punkt, srodek, sinKAT, cosKAT):
        x1R = (punkt[0] * cosKAT) - (punkt[1] * sinKAT) + srodek[0]
        y1R = (punkt[0] * sinKAT) + (punkt[1] * cosKAT) + srodek[1]
        return [x1R, y1R]
        
    def obrocPunkt2(self, punkt, srodek, sinKAT, cosKAT):
        x1R = ((punkt[0] - srodek[0]) * cosKAT) - sinKAT * (punkt[1] - srodek[1]) + srodek[0]
        y1R = ((punkt[0] - srodek[0]) * sinKAT) + cosKAT * (punkt[1] - srodek[1]) + srodek[1]
        return [x1R, y1R]
        
    def generateBRD(self, doc, groupBRD, gruboscPlytki, dane):
        pass
        
    def odbijWspolrzedne(self, punkt, srodek):
        return srodek + (srodek - punkt)
        
    def generateHoles(self, doc, dane):
        for i in dane:
            x = float("%4.3f" % i[0])
            y = float("%4.3f" % i[1])
            r = float("%4.3f" % i[2])

            doc.Sketch_PCB.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        doc.recompute()
    
    def brakujaceElementy(self, PCB_ER, filename):
        ############### ZAPIS DO PLIKU - LISTA BRAKUJACYCH ELEMENTOW
        if PCB_ER and len(PCB_ER):
            if os.path.exists(filename) and os.path.isfile(filename):
                (path, docname) = os.path.splitext(os.path.basename(filename))
                plik = __builtin__.open("{0}.err".format(filename), "w")
                a = []
                a = [i for i in PCB_ER if str(i) not in a and not a.append(str(i))]
                PCB_ER = list(a)
                
                FreeCAD.Console.PrintWarning("**************************\n")
                for i in PCB_ER:
                    line = "Object not found: {0} {2} [Package: {1}, Library: {3}]\n".format(i[0], i[1], i[2], i[3])
                    plik.writelines(line)
                    FreeCAD.Console.PrintWarning(line)
                FreeCAD.Console.PrintWarning("**************************\n")
                plik.close()
            else:
                FreeCAD.Console.PrintWarning("Access Denied. The Specified Path does not exist, or there could be permission problem.")
        else:
            try:
                os.remove("{0}.err".format(filename))
            except:
                pass
        ##############

    def addMeasure(self, doc, layerGRP, wymiary, layerName, gruboscPlytki, layerColor):
        grp = doc.addObject("App::DocumentObjectGroup", layerName)
        for i in wymiary:
            x1 = i[0]
            y1 = i[1]
            x2 = i[2]
            y2 = i[3]
            x3 = i[4]
            y3 = i[5]
            
            dim = Draft.makeDimension(FreeCAD.Vector(x1, y1, gruboscPlytki), FreeCAD.Vector(x2, y2, gruboscPlytki), FreeCAD.Vector(x3, y3, gruboscPlytki))
            dim.ViewObject.LineColor = layerColor
            dim.ViewObject.LineWidth = 1.00
            dim.ViewObject.ExtLines = 0.00
            dim.ViewObject.FontSize = 4.00
            grp.addObject(dim)
        layerGRP.addObject(grp)
        doc.recompute()
        
    def dodatkoweWarstwyGenPad(self, doc, ser, numLayer, layerName, layerHeight, layerReversed, layerColor, layerTransparent):
        # pad
        #ser.Visibility = False
        FreeCADGui.activeDocument().getObject(ser.Label).Visibility = False
        #doc.recompute()
        if numLayer == -1:
            ser2 = doc.addObject("PartDesign::Pad", layerName)
        else:
            ser2 = doc.addObject("PartDesign::Pad", layerName + "_{0}".format(numLayer))
        ser2.Sketch = ser
        ser2.Length = layerHeight
        #doc.tKeepout.Reversed = 0
        #doc.tKeepout.Midplane = 0
        #doc.Pad_PCB.Length2 = 100.0
        ser2.Type = 0
        ser2.UpToFace = None
        ser2.Midplane = False
        ser2.Reversed = layerReversed
        ser2.ViewObject.ShapeColor = layerColor
        ser2.ViewObject.Transparency = layerTransparent
        ser2.ViewObject.DisplayMode = "Shaded"
        # FreeCADGui.activeDocument().getObject(layerName).ShapeColor = layerColor
        #
        return ser2

    def addParts(self, PCB_EL, doc, groupBRD, gruboscPlytki, koloroweElemnty):
        if len(PCB_EL):
            PCB_ER = []
            
            #grp = doc.addObject("App::DocumentObjectGroup", "Parts")
            grp = makeUnigueGroup('Parts', 'partsGroup')
            # allSocked - definicja zachowania przy dodawaniu podstawki dla wszystkich obeiktow
            #   -1 - brak podstawek
            #    0 - zapytaj o dodanie podstawki (def)
            #    1 - dodaj podstawki dla wszystkich obiektow
            allSocked = 0
            
            for i in PCB_EL:
                filePath = self.partExist(i[1])
                z_pos = gruboscPlytki
                
                if filePath[0]:
                    packageData = self.__SQL__.getValues(filePath[2])
                    filePath = filePath[1]
                    
                    #partName = param.bibliotekaDane[i[1]][0]
                    #model0 = Part.Shape().read(os.path.join(partPaths, "{0}.igs".format(partName)) )
                    #model0.translate(FreeCAD.Vector(i[3] + param.bibliotekaDane[i[1]][1], i[4] + param.bibliotekaDane[i[1]][2], 2 + param.bibliotekaDane[i[1]][3]))
                    #model0.rotate(FreeCAD.Vector(i[3] + param.bibliotekaDane[i[1]][1], i[4] + param.bibliotekaDane[i[1]][2], 2), FreeCAD.Vector(0, 0, 1), i[5])
                    #Part.show(s)
                    ######### wartosc Z
                    rotateY = (float(packageData["ry"]) * 3.14) / 180
                    if i[6] == 'BOTTOM':
                        rotateY += 3.14
                        z_pos = 0
                    
                    #################################################################
                    ######### DODANIE PODSTAWKI
                    # dodajPodstawke - definicja zachowania dla danego obiektu
                    #   0 - brak podstawki
                    #   1 - dodanie podstawki
                    dodajPodstawke = False
                    if int(packageData["add_socket"]) and allSocked == 0:
                        dial = QtGui.QMessageBox()
                        dial.setText(u"Add socket to part {0} (Package: {1}, Library: {2})?".format(i[0], i[1], i[7]))
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

                    if (dodajPodstawke or allSocked == 1) and int(packageData["add_socket"]):
                        if self.__SQL__.has_section(packageData["add_socket_id"]):  # sprawdzamy czy podana podstawka istnieje
                            danePodstawki = self.__SQL__.getValues(packageData["add_socket_id"])
                            
                            if i[6] == 'BOTTOM':
                                z_pos -= float(danePodstawki["socket_height"])
                            else:
                                z_pos += float(danePodstawki["socket_height"])
                            PCB_EL.append([danePodstawki["name"], danePodstawki["name"], "", i[3], i[4], i[5], i[6], ""])
                        else:
                            PCB_ER.append([danePodstawki["name"], danePodstawki["name"], "", ""])
                    ################################################################
                    ################################################################
                    # DODANIE OBIEKTU NA PLANSZE
                    #partName = param.bibliotekaDane[i[1]][0]
                    #step_model = doc.addObject("Part::Feature", "{0} ({1})".format(i[0], i[1]))
                    #step_model.Shape = Part.read(filePath)
                    #step_model.Label = "{0} ({1})".format(i[0], i[1])
                    
                    step_model = doc.addObject("Part::FeaturePython", "{0} ({1})".format(i[0], i[1]))
                    step_model.Shape = Part.read(filePath)
                    obj = partObject(step_model, i[3], i[4], i[5])
                    
                    step_model.Label = "{0}".format(i[0])
                    step_model.Package = "{0}".format(i[1])
                    step_model.Value = "{0}".format(i[2])
                    step_model.Side = "{0}".format(i[6])
                    
                    viewProviderPartObject(step_model.ViewObject)
                    ####
                    rotateX = float(packageData["rx"]) * 3.14 / 180.
                    rotateZ = (i[5] + float(packageData["rz"])) * 3.14 / 180.
                    #step_model.Placement = FreeCAD.Base.Placement(FreeCAD.Base.Vector(i[3] + float(packageData["x"]), i[4] + float(packageData["y"]), z_pos + float(packageData["z"])), self.toQuaternion(rotateY, rotateZ, rotateX))
                    if i[6] == 'BOTTOM':
                        pos_1 = FreeCAD.Base.Vector(i[3] + float(packageData["x"]), i[4] + float(packageData["y"]), z_pos - float(packageData["z"]))
                    else:
                        pos_1 = FreeCAD.Base.Vector(i[3] + float(packageData["x"]), i[4] + float(packageData["y"]), z_pos + float(packageData["z"]))
                    center = FreeCAD.Base.Vector(-float(packageData["x"]), -float(packageData["y"]), 0)
                    if float(packageData["ry"]) >= 90 or float(packageData["ry"]) <= -90:
                        rot_1 = self.toQuaternion(rotateX, rotateZ + 3.14, rotateY)
                    else:
                        rot_1 = self.toQuaternion(rotateY, rotateZ, rotateX)
                    step_model.Placement = FreeCAD.Base.Placement(pos_1, rot_1, center)
                    doc.recompute()
                    #step_model.Placement.Base.x = i[3] + float(packageData["x"])
                    #step_model.Placement.Base.y = i[4] + float(packageData["y"])
                    #step_model.Placement.Base.z = z_pos + float(packageData["z"])
                    #doc.recompute()
                    ################################################################
                    ################################################################
                    #KOLORY DLA ELEMENTOW
                    if koloroweElemnty:
                        step_model = self.getColorFromIGS(filePath, step_model)
                    ########
                    grp.addObject(step_model)
                else:
                    rotateY = (1 * 3.14) / 180
                    if i[6] == 'BOTTOM':
                        rotateY += 3.14
                        z_pos = 0
                    
                    # DODANIE OBIEKTU NA PLANSZE
                    step_model = doc.addObject("Part::FeaturePython", "{0} ({1})".format(i[0], i[1]))
                    obj = partObject_E(step_model, i[3], i[4], i[5])
                    
                    step_model.Label = "{0}".format(i[0])
                    step_model.Package = "{0}".format(i[1])
                    step_model.Value = "{0}".format(i[2])
                    step_model.Side = "{0}".format(i[6])
                    
                    viewProviderPartObject_E(step_model.ViewObject)
                    ####
                    rotateX = 1 * 3.14 / 180.
                    rotateZ = (i[5] + 0) * 3.14 / 180.
                    #step_model.Placement = FreeCAD.Base.Placement(FreeCAD.Base.Vector(i[3] + float(packageData["x"]), i[4] + float(packageData["y"]), z_pos + float(packageData["z"])), self.toQuaternion(rotateY, rotateZ, rotateX))
                    if i[6] == 'BOTTOM':
                        pos_1 = FreeCAD.Base.Vector(i[3], i[4], z_pos)
                    else:
                        pos_1 = FreeCAD.Base.Vector(i[3], i[4], z_pos)
                    center = FreeCAD.Base.Vector(0, 0, 0)
                    #if float(packageData["ry"]) >= 90 or float(packageData["ry"]) <= -90:
                        #rot_1 = self.toQuaternion(rotateX, rotateZ + 3.14, rotateY)
                    #else:
                    rot_1 = self.toQuaternion(rotateY, rotateZ, rotateX)
                    step_model.Placement = FreeCAD.Base.Placement(pos_1, rot_1, center)
                    doc.recompute()
                    ################################################################
                    grp.addObject(step_model)
                    #
                    PCB_ER.append([i[0], i[1], i[2], i[7]])  # lista brakujacych elementow
            return PCB_ER
