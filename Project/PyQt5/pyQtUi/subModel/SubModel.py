# This Python file uses the following encoding: utf-8
import os

from PySide2.QtWidgets import QWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile


class SubModel(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.load_ui()
        self.setGeometry(0,0,100,100)

    def load_ui(self):
        loader=QUiLoader()
        rootPath=os.path.dirname(__file__)
        print(rootPath)
        path=os.path.join(rootPath,"SubModel.ui")
        ui_file=QFile(path)
        ui_file.open(QFile.ReadOnly)
        window=loader.load(ui_file,self)
        ui_file.close()

def foo():
    print("fooTest")
    return