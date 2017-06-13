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
from math import sin, cos, degrees
from PCBconf import supSoftware
from xml.dom import minidom
from PySide import QtCore, QtGui
import datetime

__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def precyzjaLiczb(value):
    return "%.2f" % float(value)


class exportPCB(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)

        self.setWindowTitle(u"Export PCB")
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/data/img/exportModel.png"))
        self.exportType = exportPCB_Eagle()
        ###
        self.addPage(self.formatPliku())
        self.addPage(self.exportUstawienia())
        #
        self.listaFormatow.setCurrentRow(0)
        self.button(QtGui.QWizard.FinishButton).clicked.connect(self.exportPliku)

    def exportPliku(self):
        self.wyczytajPCB()
        if self.addHoles.isChecked():
            self.generateHoles()
        if self.addDimensions.isChecked():
            self.wczytajWymiary()
        if self.addAnnotations.isChecked():
            self.getAnnotations()
        self.save()
        
    def zmianaProgramu(self):
        program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
        
        self.exportType = eval(supSoftware[program]['exportClass'])
        self.nazwaProgramu.setText(u'<b>Progam:</b> ' + supSoftware[program]['name'])
        self.formatPliku.setText(u'<b>Format:</b> ' + supSoftware[program]['format'])
        self.ikonaProgramu.setPixmap(QtGui.QPixmap(supSoftware[program]['icon']))
        self.pathToFile.setText(QtCore.QDir.homePath() + '/untitled.' + supSoftware[program]['format'].split('.')[1])
        #
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        
        self.addAnnotations.setCheckState(QtCore.Qt.Unchecked)
        self.addHoles.setCheckState(QtCore.Qt.Unchecked)
        self.addDimensions.setCheckState(QtCore.Qt.Unchecked)
        
        if 'dim' in supSoftware[self.exportType.programName]['exportLayers']:
            if freecadSettings.GetBool("exportDim_{0}".format(self.exportType.programName), False):
                self.addDimensions.setCheckState(QtCore.Qt.Checked)
            self.addDimensions.setDisabled(False)
        else:
            self.addDimensions.setDisabled(True)

        if 'hol' in supSoftware[self.exportType.programName]['exportLayers']:
            if freecadSettings.GetBool("exportHol_{0}".format(self.exportType.programName), False):
                self.addHoles.setCheckState(QtCore.Qt.Checked)
            self.addHoles.setDisabled(False)
        else:
            self.addHoles.setDisabled(True)

        if 'anno' in supSoftware[self.exportType.programName]['exportLayers']:
            if freecadSettings.GetBool("exportAnno_{0}".format(self.exportType.programName), False):
                self.addAnnotations.setCheckState(QtCore.Qt.Checked)
            self.addAnnotations.setDisabled(False)
        else:
            self.addAnnotations.setDisabled(True)

    def formatPliku(self):
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
        for i, j in supSoftware.items():
            if j['export']:
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

    #def warstwyPliku(self):
        #page = QtGui.QWizardPage()
        #page.setSubTitle(u"<span style='font-weight:bold;font-size:13px;'>Layers</span>")
        ##
        #self.listaWarstw = QtGui.QListWidget()
        ##
        #self.opisWarstwy = QtGui.QLabel()
        ##
        #lay = QtGui.QGridLayout(page)
        #lay.addWidget(self.listaWarstw, 0, 0, 1, 1)
        #lay.addWidget(self.opisWarstwy, 0, 1, 1, 1)
        #return page
        
    def exportUstawienia(self):
        page = QtGui.QWizardPage()
        page.setSubTitle(u"<span style='font-weight:bold;font-size:13px;'>Settings</span>")
        #
        self.pathToFile = QtGui.QLineEdit('')
        self.pathToFile.setReadOnly(True)
        #
        zmianaSciezki = QtGui.QPushButton('...')
        zmianaSciezki.setToolTip(u'Change path')
        QtCore.QObject.connect(zmianaSciezki, QtCore.SIGNAL("pressed ()"), self.zmianaSciezkiF)
        #
        self.addHoles = QtGui.QCheckBox(u'Add holes')
        self.addDimensions = QtGui.QCheckBox(u'Add dimensions')
        self.addAnnotations = QtGui.QCheckBox(u'Add annotations')
        #
        lay = QtGui.QGridLayout(page)
        lay.addWidget(QtGui.QLabel(u'Path: '), 0, 0, 1, 1)
        lay.addWidget(self.pathToFile, 0, 1, 1, 1)
        lay.addWidget(zmianaSciezki, 0, 2, 1, 1)
        lay.addItem(QtGui.QSpacerItem(1, 10), 1, 0, 1, 3)
        lay.addWidget(self.addHoles, 2, 0, 1, 3)
        lay.addWidget(self.addDimensions, 3, 0, 1, 3)
        lay.addWidget(self.addAnnotations, 4, 0, 1, 3)
        lay.setColumnStretch(1, 5)
        return page
        
    def zmianaSciezkiF(self):
        fileName = QtGui.QFileDialog().getSaveFileName(None, 'Save as', QtCore.QDir.homePath(), supSoftware[self.exportType.programName]['format'])
        if fileName[0]:
            fileName = fileName[0]
            program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
                
            if not fileName.endswith('.{0}'.format(supSoftware[program]['format'].split('.')[1])):
                fileName += '.{0}'.format(supSoftware[program]['format'].split('.')[1])
                
            self.pathToFile.setText(fileName)

    def wyczytajPCB(self):
        doc = FreeCAD.activeDocument()
        for j in doc.Objects:
            if hasattr(j, "Proxy") and hasattr(j, "Type") and j.Proxy.Type == "PCBboard":
                try:
                    for k in range(len(j.Border.Geometry)):
                        if type(j.Border.Geometry[k]).__name__ == 'GeomLineSegment':
                            self.exportType.addLine([j.Border.Geometry[k].StartPoint.x, j.Border.Geometry[k].StartPoint.y, j.Border.Geometry[k].EndPoint.x, j.Border.Geometry[k].EndPoint.y], self.exportType.borderLayer, 0.01)
                        elif type(j.Border.Geometry[k]).__name__ == 'GeomCircle':
                            self.exportType.addCircle([j.Border.Geometry[k].Radius, j.Border.Geometry[k].Center.x, j.Border.Geometry[k].Center.y], 20, 0.01)
                        elif type(j.Border.Geometry[k]).__name__ == 'GeomArcOfCircle':
                            self.exportType.addArc([j.Border.Geometry[k].Radius, j.Border.Geometry[k].Center.x, j.Border.Geometry[k].Center.y, j.Border.Geometry[k].FirstParameter, j.Border.Geometry[k].LastParameter, j.Border.Geometry[k]], self.exportType.borderLayer, 0.01)
                        else:
                            FreeCAD.Console.PrintWarning(type(j.Border.Geometry[k]).__name__ + "\n")
                    break
                except Exception, e:
                    FreeCAD.Console.PrintWarning(str(e) + "\n")
    
    def getAnnotations(self):
        doc = FreeCAD.activeDocument()
        for j in doc.Objects:
            if hasattr(j, "Proxy") and hasattr(j, "Type") and j.Proxy.Type == "PCBannotation":
                try:
                    annotation = ''
                    for i in j.ViewObject.Text:
                        annotation += u'{0}\n'.format(i)

                    self.exportType.addAnnotations(j.X.Value, j.Y.Value, j.ViewObject.Size.Value, j.Side, annotation.strip(), j.ViewObject.Align, j.Rot.Value, j.ViewObject.Mirror, j.ViewObject.Spin)
                except Exception, e:
                    FreeCAD.Console.PrintWarning(str(e) + "\n")
    
    def generateHoles(self):
        doc = FreeCAD.activeDocument()
        for j in doc.Objects:
            if hasattr(j, "Proxy") and hasattr(j, "Type") and j.Proxy.Type == "PCBboard":
                try:
                    for k in range(len(j.Holes.Geometry)):
                        self.exportType.addHole(j.Holes.Geometry[k].Radius, j.Holes.Geometry[k].Center.x, j.Holes.Geometry[k].Center.y)
                    break
                except Exception, e:
                    FreeCAD.Console.PrintWarning(str(e) + "\n")
    
    def wczytajWymiary(self):
        doc = FreeCAD.activeDocument()
        for i in doc.Objects:
            if hasattr(i, "Proxy") and hasattr(i, "Type") and i.Proxy.Type == "Dimension":
                try:
                    [xS, yS, zS] = [i.Start.x, i.Start.y, i.Start.z]
                    [xE, yE, zE] = [i.End.x, i.End.y, i.End.z]
                    [xM, yM, zM] = [i.Dimline.x, i.Dimline.y, i.Dimline.z]
                    
                    if [xS, yS] != [xE, yE] and zS == zE:
                        self.exportType.addMeasure([xS, yS, zS], [xE, yE, zE], [xM, yM, zM], i.Distance)
                except Exception, e:
                    FreeCAD.Console.PrintWarning(str(e) + "\n")

    def save(self):
        FreeCAD.Console.PrintWarning('Exporting file\n')
        if self.exportType.save(str(self.pathToFile.text())):
            FreeCAD.Console.PrintWarning('End \n')
        else:
            FreeCAD.Console.PrintWarning('STOP \n')


class exportPCB_Eagle:
    ''' Export PCB to *.brd - Eagle '''
    def __init__(self, parent=None):
        self.projektBRD = minidom.parse(__currentPath__ + "/save/untitled.brd")
        self.projektPlain = self.projektBRD.getElementsByTagName('plain')[0]
        
        self.programName = 'eagle'
        self.borderLayer = 20
    
    def addAnnotations(self, x, y, size, layer, annotation, align, rot, mirror, spin):
        # <text x="4.26" y="27.11" size="1.778" layer="25">test</text>
        if layer == 'TOP':
            layer = '25'
        else:
            layer = '26'
        
        annotation = self.projektBRD.createTextNode(annotation)
        
        if mirror == 'Global Y axis':
            mirror = 'M'
        else:
            mirror = ''
        if spin:
            spin = 'S'
        else:
            spin = ''
        rot = "{2}{1}R{0}".format(rot, mirror, spin)
        
        txt = self.projektBRD.createElement("text")
        txt.setAttribute('x', precyzjaLiczb(x))
        txt.setAttribute('y', precyzjaLiczb(y))
        txt.setAttribute('size', precyzjaLiczb(size))
        txt.setAttribute('layer', layer)
        if align != "bottom-left":
            txt.setAttribute('align', align)
        if rot != "R0.0":
            txt.setAttribute('rot', rot)
        txt.appendChild(annotation)
        self.projektPlain.appendChild(txt)
        
    def addArc(self, arc, layer, width):
        # <wire x1="80.01" y1="7.62" x2="86.36" y2="13.97" width="0.4064" layer="20" curve="90"/>
        radius = arc[0]
        xs = arc[1]
        ys = arc[2]
        sA = arc[3]
        eA = arc[4]
        
        x1 = radius * cos(sA) + xs
        y1 = radius * sin(sA) + ys
        x2 = radius * cos(eA) + xs
        y2 = radius * sin(eA) + ys
        curve = degrees(sA - eA) * (-1)
        
        x = self.projektBRD.createElement("wire")
        x.setAttribute('x1', precyzjaLiczb(x1))
        x.setAttribute('y1', precyzjaLiczb(y1))
        x.setAttribute('x2', precyzjaLiczb(x2))
        x.setAttribute('y2', precyzjaLiczb(y2))
        x.setAttribute('curve', precyzjaLiczb(curve))
        x.setAttribute('width', str(width))
        x.setAttribute('layer', str(layer))
        self.projektPlain.appendChild(x)

    def addLine(self, line, layer, width):
        # <wire x1="22.86" y1="21.59" x2="54.61" y2="21.59" width="0" layer="20"/>
        x = self.projektBRD.createElement("wire")

        x.setAttribute('x1', precyzjaLiczb(line[0]))
        x.setAttribute('y1', precyzjaLiczb(line[1]))
        x.setAttribute('x2', precyzjaLiczb(line[2]))
        x.setAttribute('y2', precyzjaLiczb(line[3]))
        x.setAttribute('width', str(width))
        x.setAttribute('layer', str(layer))
        self.projektPlain.appendChild(x)
    
    def addHole(self, r, xs, ys):
        # <hole x="36.83" y="41.91" drill="3.2"/>
        hole = self.projektBRD.createElement("hole")
        hole.setAttribute('x', precyzjaLiczb(xs))
        hole.setAttribute('y', precyzjaLiczb(ys))
        hole.setAttribute('drill', str(r * 2))
        self.projektPlain.appendChild(hole)

    def addCircle(self, circle, layer, width):
        # <circle x="16.51" y="26.67" radius="5.6796125" width="0" layer="20"/>
        x = self.projektBRD.createElement("circle")
        x.setAttribute('x', precyzjaLiczb(circle[1]))
        x.setAttribute('y', precyzjaLiczb(circle[2]))
        x.setAttribute('radius', str(circle[0]))
        x.setAttribute('width', str(width))
        x.setAttribute('layer', str(layer))
        self.projektPlain.appendChild(x)
        #FreeCAD.Console.PrintWarning(self.projektBRD.toxml())
        
    def addMeasure(self, Start, End, Dimline, Len):
        measure = self.projektBRD.createElement("dimension")
        measure.setAttribute('x1', precyzjaLiczb(Start[0]))
        measure.setAttribute('y1', precyzjaLiczb(Start[1]))
        measure.setAttribute('x2', precyzjaLiczb(End[0]))
        measure.setAttribute('y2', precyzjaLiczb(End[1]))
        measure.setAttribute('x3', precyzjaLiczb(Dimline[0]))
        measure.setAttribute('y3', precyzjaLiczb(Dimline[1]))
        measure.setAttribute('textsize', '1.778')
        measure.setAttribute('layer', '47')
        
        if Start[0] == End[0]:
            measure.setAttribute('dtype', 'vertical')
        elif Start[1] == End[1]:
            measure.setAttribute('dtype', 'horizontal')
        
        self.projektPlain.appendChild(measure)
    
    def save(self, fileName):
        try:
            with codecs.open(fileName, "w", "utf-8") as out:
                self.projektBRD.writexml(out)
            return True
        except Exception, e:
            FreeCAD.Console.PrintWarning(str(e) + "\n")
            return False


class exportPCB_KiCad:
    ''' Export PCB to *.kicad_pcb - KiCad '''
    def __init__(self, parent=None):
        self.projektBRD = codecs.open(__currentPath__ + "/save/untitled.kicad_pcb", "r").readlines()
        
        self.programName = 'kicad'
        self.borderLayer = 'Edge.Cuts'
        self.holesLayer = 'Edge.Cuts'
        
        self.pcbElem = []
        self.minX = 0
        self.minY = 0

    def getMinX(self, x):
        if x < self.minX:
            self.minX = x
            
    def getMinY(self, y):
        if y < self.minY:
            self.minY = y

    def addArc(self, arc, layer, width):
        radius = arc[0]
        xs = arc[1]
        ys = arc[2] * (-1)
        sA = arc[3]
        eA = arc[4]
        
        x1 = radius * cos(sA) + xs
        y1 = (radius * sin(sA)) * (-1) + ys
        curve = degrees(sA - eA)
        
        self.getMinX(xs)
        self.getMinY(ys)
        self.getMinX(x1)
        self.getMinY(y1)
        
        self.pcbElem.append(['gr_arc', xs, ys, x1, y1, curve, width, layer])

    def addLine(self, line, layer, width):
        x1 = float(line[0])
        y1 = float(line[1]) * (-1)
        x2 = float(line[2])
        y2 = float(line[3]) * (-1)
        
        self.getMinX(x1)
        self.getMinY(y1)
        self.getMinX(x2)
        self.getMinY(y2)
        
        self.pcbElem.append(['gr_line', x1, y1, x2, y2, width, layer])
        
    def addHole(self, r, x, y):
        #self.addCircle([r, x, y], self.holesLayer, 0.01)
        self.getMinX(x)
        self.getMinY(y)
        
        self.pcbElem.append(['hole', x, y, r])
        
    def addCircle(self, circle, layer, width):
        xs = float(circle[1])
        ys = float(circle[2]) * (-1)
        xe = float(circle[1]) + float(circle[0])
        
        self.getMinX(xs)
        self.getMinY(ys)
        self.getMinX(xe)
        
        self.pcbElem.append(['gr_circle', xs, ys, xe, width, layer])
        
    def addMeasure(self, Start, End, Dimline, Len):
        rot = 0
        if Start[0] == End[0]:
            rot = 90

        self.pcbElem.append(['dim', Len.Value, Len, Start, End, Dimline, rot])
    
    def addAnnotations(self, x, y, size, layer, annotation, align, rot, mirror, spin):
        y *= -1
        
        self.getMinX(x)
        self.getMinY(y)
        
        if layer == 'TOP':
            layer = 'F.Cu'
        else:
            layer = 'B.Cu'
        
        if rot == 0:
            rot = ''
        else:
            rot = ' {0}'.format(rot)
        
        if align in ["bottom-left", "center-left", "top-left"]:
            align = ' (justify left'
        elif align in ["bottom-right", "center-right", "top-right"]:
            align = ' (justify right'
        else:
            align = ' (justify'
        
        if mirror == 'Local Y axis':
            align = align + ' mirror)'
        else:
            align = align + ')'
        
        if align == ' (justify)':
            align = ''
            
        annotation = annotation.replace('\n', '\\n')
        
        self.pcbElem.append(['gr_text', x, y, layer, size, annotation, rot, align])

    def przesunPCB(self):
        for i in self.pcbElem:
            if i[0] == 'gr_arc':
                self.projektBRD.insert(-2, "  (gr_arc (start {0} {1}) (end {2} {3}) (angle {4}) (layer {6}) (width {5}))\n".format(
                    '{0:.10f}'.format(i[1] + abs(self.minX)), '{0:.10f}'.format(i[2] + abs(self.minY)), '{0:.10f}'.format(i[3] + abs(self.minX)), '{0:.10f}'.format(i[4] + abs(self.minY)), i[5], i[6], i[7]))
            elif i[0] == 'gr_line':
                self.projektBRD.insert(-2, "  (gr_line (start {0} {1}) (end {2} {3}) (angle 90) (layer {5}) (width {4}))\n".format(
                    '{0:.10f}'.format(i[1] + abs(self.minX)), '{0:.10f}'.format(i[2] + abs(self.minY)), '{0:.10f}'.format(i[3] + abs(self.minX)), '{0:.10f}'.format(i[4] + abs(self.minY)), i[5], i[6]))
            elif i[0] == 'gr_circle':
                self.projektBRD.insert(-2, "  (gr_circle (center {0} {1}) (end {2} {1}) (layer {4}) (width {3}))\n".format(
                    '{0:.10f}'.format(i[1] + abs(self.minX)), '{0:.10f}'.format(i[2] + abs(self.minY)), '{0:.10f}'.format(i[3] + abs(self.minX)), i[4], i[5]))
            elif i[0] == 'gr_text':
                x = i[1] + abs(self.minX)
                y = i[2] + abs(self.minY)
                
                self.projektBRD.insert(-2, '''
  (gr_text "{4}" (at {0} {1}{5}) (layer {2})
    (effects (font (size {3} {3}) (thickness 0.3)){6})
  )'''.format(x, y, i[3], i[4], i[5], i[6], i[7]))
            
            elif i[0] == 'hole':
                x = i[1] + abs(self.minX)
                y = i[2] * (-1) + abs(self.minY)
                drill = i[3] * 2
                
                self.projektBRD.insert(-2, '''\n
  (module 1pin (layer F.Cu) (tedit 53DA8F8F) (tstamp 53DB092E)
    (at {0} {1})
    (descr "module 1 pin (ou trou mecanique de percage)")
    (tags DEV)
    (path 1pin)
    (fp_text reference "" (at 0 -3.048) (layer F.SilkS)
      (effects (font (size 1.016 1.016) (thickness 0.254)))
    )
    (fp_text value "" (at 0 2.794) (layer F.SilkS) hide
      (effects (font (size 1.016 1.016) (thickness 0.254)))
    )
    (pad 1 thru_hole circle (at 0 0) (size {3} {3}) (drill {2})
      (layers *.Cu *.Mask F.SilkS)
    )
  )
'''.format(x, y, drill, drill + 0.01))

            elif i[0] == 'dim':
                if i[3][1] == i[4][1]:  # yS == yE
                    arrow1a = "{0} {1}".format("{0:.10f}".format(i[3][0] + abs(self.minX)), "{0:.10f}".format(i[5][1] * (-1) + abs(self.minY)))
                    arrow2a = "{0} {1}".format("{0:.10f}".format(i[4][0] + abs(self.minX)), "{0:.10f}".format(i[5][1] * (-1) + abs(self.minY)))
                elif i[3][0] == i[4][0]:  # xS == xE
                    arrow1a = "{0} {1}".format("{0:.10f}".format(i[5][0] + abs(self.minX)), "{0:.10f}".format(i[3][1] * (-1) + abs(self.minY)))
                    arrow2a = "{0} {1}".format("{0:.10f}".format(i[5][0] + abs(self.minX)), "{0:.10f}".format(i[4][1] * (-1) + abs(self.minY)))
                
                self.projektBRD.insert(-2, '''(dimension {0} (width 0.3) (layer Dwgs.User)
                    (gr_text "{1}" (at {2} {3} {4}) (layer Dwgs.User)
                      (effects (font (size 1.5 1.5) (thickness 0.3)))
                    )
                    (feature1 (pts (xy {5} {6}) (xy {9})))
                    (feature2 (pts (xy {7} {8}) (xy {10})))
                    (crossbar (pts (xy {9}) (xy {10})))
                    (arrow1a (pts (xy {9}) (xy {9})))
                    (arrow1b (pts (xy {9}) (xy {9})))
                    (arrow2a (pts (xy {10}) (xy {10})))
                    (arrow2b (pts (xy {10}) (xy {10})))
                  )'''.format(i[1], i[2], "{0:.10f}".format(i[5][0] + abs(self.minX)), "{0:.10f}".format(i[5][1] * (-1) + abs(self.minY)), i[6], "{0:.10f}".format(i[3][0] + abs(self.minX)), "{0:.10f}".format(i[3][1] * (-1) + abs(self.minY)), "{0:.10f}".format(i[4][0] + abs(self.minX)), "{0:.10f}".format(i[4][1] * (-1) + abs(self.minY)), arrow1a, arrow2a))
                  
    def save(self, fileName):
        try:
            self.przesunPCB()
            
            files = codecs.open(fileName, "w", "utf-8")
            files.write("".join(self.projektBRD))
            files.close()
            return True
        except Exception, e:
            FreeCAD.Console.PrintWarning(str(e) + "\n")
            return False


class exportPCB_FidoCadJ:
    ''' Export PCB to *.fcd - FidoCadJ '''
    def __init__(self, parent=None):
        self.projektBRD = codecs.open(__currentPath__ + "/save/untitled.fcd", "r").readlines()
        self.pcbElem = []
        
        self.programName = 'fidocadj'
        self.borderLayer = 0
        
        self.mnoznik = 0.127
        self.minX = 0
        self.minY = 0

    def getMinX(self, x):
        if x < self.minX:
            self.minX = x
            
    def getMinY(self, y):
        if y < self.minY:
            self.minY = y
    
    def addAnnotations(self, x, y, size, layer, annotation, align, rot, mirror, spin):
        x = int(x / self.mnoznik)
        y = int(y / self.mnoznik) * (-1)
        
        self.getMinX(x)
        self.getMinY(y)
        
        if mirror == 'Global Y axis':
            mirror = 4
        else:
            mirror = 0
        
        if layer == 'TOP':
            layer = 2
        else:
            layer = 1
            
        annotation = annotation.replace('\n', ' ')
        size = int(size / self.mnoznik)
        rot = int(rot)
        
        self.pcbElem.append(["TY", x, y, size, size, rot, mirror, layer, '*', annotation])

    def addArc(self, arc, layer, width):
        pass

    def addLine(self, line, layer, width):
        if layer == 20:
            layer = 0
            
        x1 = int(float(line[0]) / self.mnoznik)
        y1 = int(float(line[1]) / self.mnoznik) * (-1)
        x2 = int(float(line[2]) / self.mnoznik)
        y2 = int(float(line[3]) / self.mnoznik) * (-1)
        
        self.getMinX(x1)
        self.getMinX(x2)
        self.getMinY(y1)
        self.getMinY(y2)
        
        self.pcbElem.append(["LI", x1, y1, x2, y2, layer])

    def przesunPCB(self):
        for i in range(len(self.pcbElem)):
            if self.pcbElem[i][0] == "LI":
                self.pcbElem[i][1] += abs(self.minX)
                self.pcbElem[i][2] += abs(self.minY)
                self.pcbElem[i][3] += abs(self.minX)
                self.pcbElem[i][4] += abs(self.minY)
                self.pcbElem[i] = " ".join([str(k) for k in self.pcbElem[i]]) + "\n"
            elif self.pcbElem[i][0] == "EV":
                self.pcbElem[i][1] += abs(self.minX)
                self.pcbElem[i][2] += abs(self.minY)
                self.pcbElem[i][3] += abs(self.minX)
                self.pcbElem[i][4] += abs(self.minY)
                self.pcbElem[i] = " ".join([str(k) for k in self.pcbElem[i]]) + "\n"
            elif self.pcbElem[i][0] == "TY":
                self.pcbElem[i][1] += abs(self.minX)
                self.pcbElem[i][2] += abs(self.minY)
                self.pcbElem[i] = " ".join([str(k) for k in self.pcbElem[i]]) + "\n"
    
    def addHole(self, r, x, y):
        self.addCircle([r, x, y], 0, 0.01)

    def addCircle(self, circle, layer, width):
        if layer == 20:
            layer = 0
        
        x1 = int((float(circle[1]) - float(circle[0])) / self.mnoznik)
        y1 = int((float(circle[2]) - float(circle[0])) / self.mnoznik) * (-1)
        x2 = int((float(circle[1]) + float(circle[0])) / self.mnoznik)
        y2 = int((float(circle[2]) + float(circle[0])) / self.mnoznik) * (-1)
    
        self.getMinX(x1)
        self.getMinX(x2)
        self.getMinY(y1)
        self.getMinY(y2)
        
        self.pcbElem.append(["EV", x1, y1, x2, y2, layer])
    
    def save(self, fileName):
        try:
            self.przesunPCB()

            files = codecs.open(fileName, "w", "utf-8")
            files.write("".join(self.projektBRD))
            files.write("".join(self.pcbElem))
            files.close()
            return True
        except Exception, e:
            FreeCAD.Console.PrintWarning(str(e) + "\n")
            return False


class exportPCB_FreePCB():
    ''' Export PCB to *.fpc - FreePCB '''
    def __init__(self, parent=None):
        self.projektBRD = codecs.open(__currentPath__ + "/save/untitled.fpc", "r").readlines()
        
        self.programName = 'freepcb'
        self.borderLayer = 0
        
        self.boardOutline = ''
        self.annotations = ''
        
        self.mnoznik = 1. / 1000000.
        self.cornerNumber = 0
        
    def addAnnotations(self, x, y, size, layer, annotation, align, rot, mirror, spin):
        # text: "test" 30480000 27940000 7 0 0 2540000 254000
        annotation = annotation.replace('\n', ' ').replace('\r\n', ' ')
        x = int(x / self.mnoznik)
        y = int(y / self.mnoznik)
        
        if layer == 'TOP':
            layer = 7
        else:
            layer = 0
            
        rot = 360 - rot
        size = int(size / self.mnoznik)
        
        if mirror == 'Center':
            mirror = 1
        else:
            mirror = 0
        
        annotation = annotation.replace('\n', ' ')
        
        self.annotations += 'text: "{0}" {1} {2} {3} {4} {5} {6} 25400\n'.format(annotation, x, y, layer, int(rot), mirror, size)
        
    def addArc(self, arc, layer, width):
        pass
        #if layer == 20:
            #self.cornerNumber += 1
            
            #radius = arc[0]
            #xs = arc[1]
            #ys = arc[2]
            #sA = arc[3]
            #eA = arc[4]
            
            #x1 = radius * cos(sA) + xs
            #y1 = radius * sin(sA) + ys
            #x2 = radius * cos(eA) + xs
            #y2 = radius * sin(eA) + ys
            
            #self.projektBRD.insert(-11, "  corner: {0} {1} {2} 2\n".format(self.cornerNumber, int(x2 / self.mnoznik), int(y2 / self.mnoznik)))
    
    def sortLines(self):
        pass

    def addLine(self, line, layer, width):
        if layer == 0:
            self.cornerNumber += 1
            
            self.boardOutline += "  corner: {0} {1} {2} 0\n".format(
                self.cornerNumber,
                int(float(line[0]) / self.mnoznik),
                int(float(line[1]) / self.mnoznik))

    def addHole(self, r, x, y):
        pass

    def addCircle(self, circle, layer, width):
        pass
    
    def save(self, fileName):
        try:
            txt = "".join(self.projektBRD)
            #txt = re.sub(r"outline: [0-9]\n", "outline: {0}\n".format(self.cornerNumber), txt)
            
            # border outlines
            txt = txt.replace('outline: 0', '''outline: {0}\n{1}'''.format(self.cornerNumber, self.boardOutline))
            # annotations
            txt = txt.replace('[texts]', '''[texts]\n{0}'''.format(self.annotations))
            
            files = codecs.open(fileName, "w", "utf-8")
            files.write(txt.replace('\r\n', '\n').replace('\n', '\r\n'))
            files.close()
            return True
        except Exception, e:
            FreeCAD.Console.PrintWarning(str(e) + "\n")
            return False


class exportPCB_IDF_v2():
    ''' Export PCB to *.idf - IDF v2 '''
    def __init__(self, parent=None):
        self.projektBRD = codecs.open(__currentPath__ + "/save/untitled_v2.idf", "r").readlines()
        
        self.programName = 'idf_v2'
        self.borderLayer = 0

    def addArc(self, arc, layer, width):
        pass

    def addLine(self, line, layer, width):
        pass

    def addCircle(self, circle, layer, width):
        pass
    
    def save(self, fileName):
        try:
            self.projektBRD = "".join(self.projektBRD)
            
            FreeCAD.Console.PrintWarning(u"{0} \n".format(self.projektBRD))
            
            self.projektBRD = self.projektBRD.format(
                    DATE=datetime.datetime.now().strftime("%Y/%m/%d.%H:%M:%S"),
                    BOARD='nazwa'
                )
            
            FreeCAD.Console.PrintWarning(u"******\n\n")
            
            FreeCAD.Console.PrintWarning(u"{0} \n".format(self.projektBRD))
            
            
            #self.projektBRD = self.projektBRD.format(BOARD='nazwa')
        
            files = codecs.open(fileName, "w", "utf-8")
            files.write(self.projektBRD)
            files.close()
            return True
        except Exception, e:
            FreeCAD.Console.PrintWarning(str(e) + "\n")
            return False


class exportPCB_gEDA:
    ''' Export PCB to *.pcb - gEDA '''
    def __init__(self, parent=None):
        self.projektBRD = codecs.open(__currentPath__ + "/save/untitled.pcb", "r").readlines()
        
        self.programName = 'geda'
    
    def wymiaryPlytki(self):
        doc = FreeCAD.ActiveDocument
        for i in doc.Objects:
            if hasattr(i, "Proxy") and hasattr(i, "Type") and i.Proxy.Type == "pcbGroup":
                for j in i.OutList:
                    try:
                        return [True, j.Length]
                    except:
                        return [False, 0]
        return [False, 0]
        
    def addArc(self, arc, layer, width):
        pass

    def addLine(self, line, layer, width):
        pass

    def addCircle(self, circle, layer, width):
        pass
    
    def save(self, fileName):
        try:
            [pcbX, pcbY] = self.wymiaryPlytki()
            
            self.projektBRD = "".join(self.projektBRD)
            self.projektBRD = self.projektBRD.format(pcbX=pcbX, pcbY=pcbY)
        
            files = codecs.open(fileName, "w", "utf-8")
            files.write(self.projektBRD)
            files.close()
            return True
        except Exception, e:
            FreeCAD.Console.PrintWarning(str(e) + "\n")
            return False
