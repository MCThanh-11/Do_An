from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.Login_MainWindowAdjust import Dangnhap

app=QApplication([])
mainwindow=QMainWindow()
myui=Dangnhap()
myui.setupUi(mainwindow)
myui.showWindow()
app.exec()