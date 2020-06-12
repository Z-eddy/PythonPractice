import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from mainWindow import Ui_MainWindow

if __name__ == "__main__":
    app=QApplication(sys.argv)
    w=QMainWindow()
    ui=Ui_MainWindow()
    ui.setupUi(w)
    w.show()
    sys.exit(app.exec())
