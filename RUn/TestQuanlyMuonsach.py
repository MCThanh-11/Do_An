from PyQt6.QtWidgets import QApplication, QMainWindow

# from ui.QuanLySachExt import QuanLySachExt
from ui.QuanliMuonSachExt import QuanLyMuonSachExt

app=QApplication([])
mainwindow=QMainWindow()
myui=QuanLyMuonSachExt("Thanh","111")
myui.setupUi(mainwindow)
myui.showWindow()
app.exec()

