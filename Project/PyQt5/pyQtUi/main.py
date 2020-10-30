# This Python file uses the following encoding: utf-8
import sys
import os
import subModel.SubModel as m


from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader


class MainUI(QWidget):
    def __init__(self):
        super(MainUI, self).__init__()
        self.load_ui()


    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        window = loader.load(ui_file, self)
        ui_file.close()
        # window.pushButton.clicked.connect(self.onClicked)
        window.btn.clicked.connect(self.onClicked)
    
    def onClicked(self,click):
        print("click",click)

if __name__ == "__main__":
    app = QApplication([])
    widget = MainUI()
    widget.show()
    subWid=m.SubModel(widget)
    # subWid.setWindowTitle("subModel")
    subWid.show()
    # m.foo()
    sys.exit(app.exec_())
