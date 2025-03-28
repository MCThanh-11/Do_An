from PyQt6.QtWidgets import QApplication, QMainWindow
from models.chucnang import  chucnang

app=QApplication([])
mainwindow=QMainWindow()
myui=chucnang()
myui.setupUi(mainwindow)
myui.showWindow()
app.exec()

