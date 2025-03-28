from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QWidget, QTableWidget, QVBoxLayout, QFileDialog, QMainWindow
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from lbs.DataConnector import DataConnector
from lbs.DataConnector import Book
from lbs.ExportTool import ExportTool

from ui.QuanLySach import Ui_MainWindow


class QuanLySachExt(Ui_MainWindow):
    def __init__(self,name,userid):
        uri = "mongodb+srv://admin:123@cluster0.7rh5y.mongodb.net/"

        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client["Chatbot"]
        self.dc=DataConnector()
        self.books= self.dc.get_all_books()
        self.book_borrowed=None
        self.allborrowers=self.dc.get_all_borrow_receipt()
        self.alluser=self.dc.get_all_users()
        self.name=name
        self.userid=userid
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow=MainWindow
        self.setupSignalAndSlot()
        self.show_books_gui()
        self.timer.start(30000)
    def showWindow(self):
        self.MainWindow.showMaximized()

    def show_books_gui(self):
        # clear all previous data from QTableWidget:
        self.books = self.dc.get_all_books()
        self.tableWidget.setRowCount(0)
        # load product into QTableWidget:
        for book in self.books:
            # get number of row (meaning last index):
            row = self.tableWidget.rowCount()
            # insert new row (last row, at the end of row in the Table):
            self.tableWidget.insertRow(row)
            # creating 5 columns for each row:
            col_book_id = QTableWidgetItem(book.book_id)
            col_title = QTableWidgetItem(book.title)
            col_author = QTableWidgetItem(str(book.author))
            col_publication_year = QTableWidgetItem(str(book.publication_year))
            col_quantity = QTableWidgetItem(str(book.quantity))
             # set column for row:
            self.tableWidget.setItem(row, 0, col_book_id)
            self.tableWidget.setItem(row, 1, col_title)
            self.tableWidget.setItem(row, 2, col_author)
            self.tableWidget.setItem(row, 3, col_publication_year)
            self.tableWidget.setItem(row, 4, col_quantity)

    def setupSignalAndSlot(self):
        self.pushButtonThemSach.clicked.connect(self.add_book)
        self.pushButtonUpdate.clicked.connect(self.update_book)
        self.pushButtonXoaSach.clicked.connect(self.delete_book)
        self.tableWidget.cellClicked.connect(self.load_book_to_form)
        self.actionExcel_File_Export.triggered.connect(self.export_to_book_excel)
        self.pushButton_Signout.clicked.connect(self.Signout_handle)


    def load_book_to_form(self, row, column):
        """Lấy dữ liệu từ bảng và hiển thị lên các ô nhập liệu khi người dùng chọn một hàng"""
        book = self.books[row]  # Lấy sách từ danh sách theo chỉ số dòng

        self.lineEditISBN.setText(book.book_id)
        self.lineEditBookName.setText(book.title)
        self.lineEditAuthor.setText(book.author)
        self.lineEditPubYear.setText(str(book.publication_year))
        self.lineEditQuantity.setText(str(book.quantity))

    def add_book(self):
        """Thêm sách vào danh sách"""
        book_id = self.lineEditISBN.text().strip()
        title = self.lineEditBookName.text().strip()
        author = self.lineEditAuthor.text().strip()
        pub_year = self.lineEditPubYear.text().strip()
        quantity = self.lineEditQuantity.text().strip()
        link=None

        if not (book_id and title and author and pub_year and quantity):
            QMessageBox.warning(self.MainWindow, "Error", "Please fill in all banks!")
            return

        # Kiểm tra sách đã tồn tại chưa
        for book in self.books:
            if book.book_id == book_id:
                QMessageBox.warning(self.MainWindow, "Error", "Bokid_existed!")
                return

        # Thêm sách mới
        self.dc.add_new_book(book_id, title, author, int(pub_year), int(quantity),link)

        # Cập nhật giao diện
        self.show_books_gui()

        QMessageBox.information(self.MainWindow, "Done", "Book added sucessfully!")

    # def save_books_to_json(self):
    #     """Lưu danh sách sách vào file JSON"""
    #     jff = JsonFileFactory()
    #     filename = "../dataset/book.json"
    #     jff.write_data(self.books, filename)

    def update_book(self):
        """Cập nhật thông tin sách"""
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self.MainWindow, "Error", "No books has benn chosen!")
            return

        book_id = self.lineEditISBN.text().strip()
        title = self.lineEditBookName.text().strip()
        author = self.lineEditAuthor.text().strip()
        pub_year = self.lineEditPubYear.text().strip()
        quantity = self.lineEditQuantity.text().strip()
        link=None

        if not (book_id and title and author and pub_year and quantity):
            QMessageBox.warning(self.MainWindow, "Error", "Please fill in all blanks!")
            return

        try:
            collection = self.dc.db["book"]
            result = collection.update_one(
                {"book_id": book_id},  # Điều kiện tìm sách
                {"$set": {
                    "title": title,
                    "author": author,
                    "publication_year": int(pub_year),
                    "quantity": int(quantity),
                    "link":link
                }}
            )

            if result.matched_count == 0:
                QMessageBox.warning(self.MainWindow, "Error", "No book found!")
                return

        # Cập nhật lại bảng hiển thị

            self.show_books_gui()

            QMessageBox.information(self.MainWindow, "Successfully", "The book has been updated.!")
        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Error", f"Error when update: {str(e)}")

    def delete_book(self):
        """Xóa sách khỏi MongoDB và giao diện"""
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self.MainWindow, "Error", "No book found!")
            return

        book_id = self.books[selected_row].book_id

        dlg = QMessageBox(self.MainWindow)
        dlg.setWindowTitle("Delete")
        dlg.setText(f"Are you sure you want to delete book [{book_id}]?")
        dlg.setIcon(QMessageBox.Icon.Question)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        button = dlg.exec()
        if button == QMessageBox.StandardButton.No:
            return  # Dừng nếu người dùng không đồng ý xóa

        try:
            collection = self.db["book"]
            result = collection.delete_one({"book_id": book_id})  # Xóa trong MongoDB

            if result.deleted_count == 0:
                QMessageBox.warning(self.MainWindow, "Error", "No ISBN found!")
                return

            # Xóa khỏi danh sách hiện tại
            del self.books[selected_row]

            # Cập nhật lại bảng hiển thị
            self.show_books_gui()

            QMessageBox.information(self.MainWindow, "Succesfully", "Book removed successfully!")

        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Error", f"Can not fix: {str(e)}")
        self.show_books_gui()

    def export_to_book_excel(self):
        """Xuất danh sách sách ra file Excel với đường dẫn do người dùng chọn"""
        self.books=self.dc.get_all_books()
        file_path, _ = QFileDialog.getSaveFileName(
            self.MainWindow,
            "Choosing Excel",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if not file_path:  # Người dùng bấm hủy
            return

        exporter = ExportTool()
        success = exporter.export_books_to_excel(file_path, self.books)

        if success:
            QMessageBox.information(self.MainWindow, "Done", f"The book list has been exported to file in:\n{file_path}")
        else:
            QMessageBox.warning(self.MainWindow, "Error", "Can not export!")



    def Signout_handle(self):
        reply = QMessageBox.question(
            self.MainWindow,
            "Sign out",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from ui.Login_MainWindowAdjust import Dangnhap

            # Đóng cửa sổ hiện tại
            self.MainWindow.close()
            # Mở lại giao diện đăng nhập (Dangnhap) trong cửa sổ mới
            self.login_window = QMainWindow()
            login_ui = Dangnhap()
            login_ui.setupUi(self.login_window)
            login_ui.showWindow()


    def refresh_data(self):
        """Hàm gọi khi QTimer timeout, cập nhật lại dữ liệu giao diện."""
        self.show_books_gui()
