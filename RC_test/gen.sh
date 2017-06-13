#! /bin/bash

pyrcc4 -py3 RC.qrc -o ../PCBrc.py
sed -i 's/PyQt4/PySide/g' ../PCBrc.py
