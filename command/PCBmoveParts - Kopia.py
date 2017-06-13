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
import Part
import os
import sys
#import re

#from math import sin, cos, sqrt
#import __builtin__
from PCBconf import *
from PCBobjects import partObject, viewProviderPartObject, partObject_E, viewProviderPartObject_E
from PCBpartManaging import partsManaging
from PCBboard import getPCBheight

if FreeCAD.GuiUp:
    #import FreeCADGui
    from PySide import QtCore, QtGui

from PCBmakeGroup import makeUnigueGroup


class moveWizardWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.listaBibliotek = QtGui.QComboBox()
        #
        self.positionX = QtGui.QDoubleSpinBox()
        self.positionX.setSingleStep(0.1)
        self.positionY = QtGui.QDoubleSpinBox()
        self.positionY.setSingleStep(0.1)
        self.positionZ = QtGui.QDoubleSpinBox()
        self.positionZ.setSingleStep(0.1)
        self.rotationRX = QtGui.QDoubleSpinBox()
        self.rotationRX.setSingleStep(0.1)
        self.rotationRX.setRange(-360, 360)
        self.rotationRY = QtGui.QDoubleSpinBox()
        self.rotationRY.setSingleStep(0.1)
        self.rotationRY.setRange(-360, 360)
        self.rotationRZ = QtGui.QDoubleSpinBox()
        self.rotationRZ.setSingleStep(0.1)
        self.rotationRZ.setRange(-360, 360)
        #
        lay = QtGui.QGridLayout()
        lay.addWidget(QtGui.QLabel('Library'), 0, 0, 1, 1)
        lay.addWidget(self.listaBibliotek, 0, 1, 1, 3)
        lay.addWidget(QtGui.QLabel('X:'), 1, 0, 1, 1)
        lay.addWidget(self.positionX, 1, 1, 1, 1)
        lay.addWidget(QtGui.QLabel('Y:'), 2, 0, 1, 1)
        lay.addWidget(self.positionY, 2, 1, 1, 1)
        lay.addWidget(QtGui.QLabel('Z:'), 3, 0, 1, 1)
        lay.addWidget(self.positionZ, 3, 1, 1, 1)
        lay.addWidget(QtGui.QLabel('RX:'), 1, 2, 1, 1)
        lay.addWidget(self.rotationRX, 1, 3, 1, 1)
        lay.addWidget(QtGui.QLabel('RY:'), 2, 2, 1, 1)
        lay.addWidget(self.rotationRY, 2, 3, 1, 1)
        lay.addWidget(QtGui.QLabel('RZ:'), 3, 2, 1, 1)
        lay.addWidget(self.rotationRZ, 3, 3, 1, 1)
        
        lay.setRowStretch(3, 5)
        self.setLayout(lay)
        #
        self.readLibs()

    def readLibs(self):
        ''' read all available libs from conf file '''
        for i, j in databaseList.items():
            if j['path'].strip() != "":
                if j['name'].strip() != "":
                    dbName = j['name'].strip()
                else:
                    dbName = i.strip()
                
                self.listaBibliotek.addItem(dbName)
                self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, i, QtCore.Qt.UserRole)
        self.listaBibliotek.setCurrentIndex(0)


class moveParts(partsManaging):
    ''' move 3d models of packages '''
    def __init__(self, updateModel, parent=None):
        self.form = moveWizardWidget()
        self.form.setWindowTitle('Move model')
        self.updateModel = updateModel
        self.updateModelPlacement = self.updateModel.Placement

    def open(self):
        ''' load all packages types to list '''
        self.form.positionX.setValue(self.updateModel.Placement.Base.x)
        self.form.positionY.setValue(self.updateModel.Placement.Base.y)
        self.form.positionZ.setValue(self.updateModel.Placement.Base.z)
        
        #[rx, ry, rz, angle] = self.getObjRot(self.updateModel)
        #[rx, ry, rz] = self.quaternionToEuler(rx, ry, rz, angle)
        
        #self.form.rotationRX.setValue(rx)
        #self.form.rotationRY.setValue(ry)
        #self.form.rotationRZ.setValue(rz)
        #
        self.form.connect(self.form.positionX, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.positionY, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.positionZ, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.rotationRX, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.rotationRY, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.rotationRZ, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
    
    def changePos(self, val):
        
        FreeCAD.Console.PrintWarning(str(self.updateModel.Proxy.Type) +"\n")
        
        
        rot = self.toQuaternion(self.form.rotationRY.value() * 3.14 / 180., self.form.rotationRZ.value() * 3.14 / 180. + self.updateModel.Proxy.orygPos[2] * 3.14 / 180., self.form.rotationRX.value() * 3.14 / 180.)
        pos = FreeCAD.Base.Vector(self.form.positionX.value(), self.form.positionY.value(), self.form.positionZ.value())
        #center = FreeCAD.Base.Vector(self.reset[0], self.reset[1])
        center = FreeCAD.Base.Vector(0, 0)
        self.updateModel.Placement = FreeCAD.Base.Placement(pos, rot, center)

    def resetObj(self):
        self.updateModel.Placement = self.updateModelPlacement
        
    def reject(self):
        self.resetObj()
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
        
        FreeCAD.ActiveDocument.recompute()
        return True
