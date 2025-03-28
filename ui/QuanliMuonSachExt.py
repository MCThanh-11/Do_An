import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QMainWindow, QHeaderView, QProgressDialog, QApplication
from lbs.DataConnector import DataConnector, BorrowReceipt
from models.chat_app import ChatBotApp
from ui.QuanliMuonSach import Ui_MainWindow


class QuanLyMuonSachExt(Ui_MainWindow):
    def __init__(self, username, userid):
        super().__init__()
        self.dc = DataConnector()
          # Lấy tất cả sách từ DataConnector
        self.selectedBook = None
        self.borrowed_books = []  # Danh sách sách đã mượn
        self.username = username
        self.user_id = userid
        self.books = self.dc.get_all_books()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.setupSignalAndSlot()
        self.MainWindow.showMaximized()
        self.tableWidget.itemSelectionChanged.connect(self.processItemSelection)
        self.show_books_gui()  # Hiển thị sách khi cửa sổ được mở
        self.show_borrowed_books()
        self.label_welcomeuser.setText(f"Welcome {self.username}")
        self.timer.start(5000)

    def show_books_gui(self):
        """
        Hiển thị tất cả các sách trong tableWidget với nội dung căn giữa và cột giãn đều.
        """
        self.books = self.dc.get_all_books()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)  # Xóa các dòng cũ trong bảng

        for book in self.books:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            columns = [
                book.book_id,
                book.title,
                str(book.author),
                str(book.publication_year),
                str(book.quantity)
            ]

            for col, value in enumerate(columns):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, col, item)

        # Căn giữa cột và giãn đều
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def showWindow(self):
        self.MainWindow.showMaximized()

    def setupSignalAndSlot(self):
        # Kết nối các button với các phương thức xử lý
        self.pushButtonLoc.clicked.connect(self.loc_button)
        self.pushButtonMuon.clicked.connect(self.muon_button)
        self.pushButtonTra.clicked.connect(self.tra_button)
        self.pushButton_Chatbot.clicked.connect(self.chatbotinteraction)
        self.pushButton_Signout.clicked.connect(self.Signout_handle)

    def tra_button(self):
        selected_row = self.tableWidgetsachmuon.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self.MainWindow, "No Selection",
                                "Please select a book in the receipt you want to return.")
            return

        receipt_id_item = self.tableWidgetsachmuon.item(selected_row, 0)
        book_id_item = self.tableWidgetsachmuon.item(selected_row, 1)

        if not receipt_id_item or not book_id_item:
            QMessageBox.warning(self.MainWindow, "Missing Data", "Cannot identify the receipt or book ID.")
            return

        receipt_id = receipt_id_item.text().strip()
        book_id = book_id_item.text().strip()

        reply = QMessageBox.question(
            self.MainWindow,
            "Confirm Return",
            f"Are you sure you want to return the book {book_id} from receipt {receipt_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for receipt in self.dc.list:
                if receipt.receipt_id == receipt_id:
                    self.dc.list.remove(receipt)
                    break
            self.show_borrowed_books()
            #  Tăng lại số lượng trong RAM
            # for book in self.dc.allbooks:
            #     if book.book_id == book_id:
            #         book.quantity += 1
            #         break

            #  Cập nhật lại giao diện ngay lập tức


            #  Cập nhật MongoDB ngầm phía sau
            self.dc.remove_borrowed_book(book_id=book_id, user_id=self.user_id)

            QMessageBox.information(self.MainWindow, "Book Returned", f"Returned book {book_id}.")

    def move_books_up_and_clear(self, selected_row):
        """
        Hàm này sẽ xóa dữ liệu trong các ô của dòng và di chuyển dữ liệu từ các dòng phía dưới lên trên.
        Cập nhật lại toàn bộ thông tin trong bảng sách đã mượn sau khi trả sách.
        """
        # Xóa dữ liệu trong các ô của dòng
        for col in range(self.tableWidgetsachmuon.columnCount()):
            self.tableWidgetsachmuon.setItem(selected_row, col, QTableWidgetItem(''))

        # Di chuyển dữ liệu từ các dòng phía dưới lên trên
        for row in range(selected_row, self.tableWidgetsachmuon.rowCount() - 1):
            for col in range(self.tableWidgetsachmuon.columnCount()):
                current_item = self.tableWidgetsachmuon.item(row + 1, col)
                self.tableWidgetsachmuon.setItem(row, col, QTableWidgetItem(current_item.text()))
                self.tableWidgetsachmuon.setItem(row + 1, col, QTableWidgetItem(''))

        # Sau khi đã trả hết sách, reset lại bảng sách đã mượn
        self.tableWidgetsachmuon.setRowCount(0)  # Xóa toàn bộ dữ liệu trong bảng sách đã mượn
        self.borrowed_books.clear()  # Xóa danh sách sách đã mượn

    def chatbotinteraction(self):
        """Gọi ChatBotApp và đảm bảo QApplication không bị khởi tạo nhiều lần"""
        print("Change to Chatbot")
        if hasattr(self, "chatbot_window") and self.chatbot_window is not None:
            # Nếu cửa sổ chatbot đã tồn tại, đưa nó lên trước
            self.chatbot_window.activateWindow()
            self.chatbot_window.raise_()
        else:
            # Nếu chưa có, tạo cửa sổ mới
            self.chatbot_window = ChatBotApp(self.username)

        self.chatbot_window.show()

    def processItemSelection(self):
         # Lấy dòng sách đã chọn
        selected_row = self.tableWidget.currentRow()
        if selected_row != -1:
            book_id = self.tableWidget.item(selected_row, 0).text()
            title = self.tableWidget.item(selected_row, 1).text()
            author = self.tableWidget.item(selected_row, 2).text()
            publication_year = self.tableWidget.item(selected_row, 3).text()
            quantity = self.tableWidget.item(selected_row, 4).text()
            self.selectedBook = {
                'book_id': book_id,
                'title': title,
                'author': author,
                'publication_year': publication_year,
                'quantity': quantity
            }

    def loc_button(self):
        # Lọc sách theo tiêu chí trong comboBox và lineEdit
        search_criteria = self.comboBox.currentText()
        search_value = self.lineEdit_Infor.text().strip()

        if search_value:
            filtered_books = []
            for book in self.books:
                if search_criteria == "ISBN" and search_value in str(book.book_id):
                    filtered_books.append(book)
                elif search_criteria == "Name Book" and search_value.lower() in book.title.lower():
                    filtered_books.append(book)
                elif search_criteria == "Author" and search_value.lower() in book.author.lower():
                    filtered_books.append(book)
                elif search_criteria == "Publication Year" and search_value in str(book.publication_year):
                    filtered_books.append(book)
                elif search_criteria == "Quantity" and search_value in str(book.quantity):
                    filtered_books.append(book)

            if filtered_books:
                # Nếu tìm thấy sách phù hợp, cập nhật bảng
                self.update_table_with_books(filtered_books)
            else:
                # Nếu không có sách phù hợp, hiển thị QMessageBox thay vì thay đổi bảng
                msg_box = QMessageBox(self.MainWindow)

                msg_box.setText("Không có dữ liệu trùng khớp.")
                msg_box.setWindowTitle("Thông Báo")
                msg_box.setStyleSheet("""
                           QMessageBox {
                               background-color: #CC99FF;
                               border: 2px solid #9999FF;
                               border-radius: 10px;
                           }
                           QMessageBox QLabel {
                               color: #FFFF00;
                               font-size: 14px;
                           }
                           QMessageBox QPushButton {
                               background-color: #4CAF50;
                               color: white;
                               border-radius: 5px;
                               padding: 5px;
                           }
                           QMessageBox QPushButton:hover {
                               background-color: #45a049;
                           }
                       """)
                msg_box.exec()
        else:
            QMessageBox.warning(self.MainWindow, "Input Error", "Please enter a value to search.")

    def update_table_with_books(self, filtered_books):
        """
        Cập nhật bảng tableWidget với các sách đã lọc.
        """
        self.tableWidget.setRowCount(0)  # Xóa các dòng cũ trong bảng
        for book in filtered_books:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            col_book_id = QTableWidgetItem(str(book.book_id))
            col_title = QTableWidgetItem(book.title)
            col_author = QTableWidgetItem(str(book.author))
            col_publication_year = QTableWidgetItem(str(book.publication_year))
            col_quantity = QTableWidgetItem(str(book.quantity))

            self.tableWidget.setItem(row, 0, col_book_id)
            self.tableWidget.setItem(row, 1, col_title)
            self.tableWidget.setItem(row, 2, col_author)
            self.tableWidget.setItem(row, 3, col_publication_year)
            self.tableWidget.setItem(row, 4, col_quantity)

    def muon_button(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self.MainWindow, "No Selection", "Please select a book to borrow.")
            return

        book_id = self.tableWidget.item(selected_row, 0).text()
        title = self.tableWidget.item(selected_row, 1).text()
        quantity_text = self.tableWidget.item(selected_row, 4).text()

        if not quantity_text.isdigit():
            QMessageBox.warning(self.MainWindow, "Data Error", "Invalid book quantity.")
            return

        quantity = int(quantity_text)
        if quantity <= 0:
            QMessageBox.warning(self.MainWindow, "Out of Stock", "This book is out of stock.")
            return

        #  Lưu tạm vào RAM (self.dc.list)
        new_receipt_id = self.dc.generate_unique_receipt_id()
        receipt = BorrowReceipt(
            receipt_id=new_receipt_id,
            user_id=self.user_id,
            name=self.username,
            book_id=book_id,
            title=title,
            quantity_borrow=1
        )
        # self.dc.list.append(receipt)  # Lưu tạm

        # #  Trừ số lượng
        # for book in self.dc.allbooks:
        #     if book.book_id == book_id:
        #         book.quantity -= 1
        #         break

        #  Cập nhật giao diện ngay lập tức
        self.dc.create_borrow_receipt(self.user_id, self.username, book_id, 1)
        self.show_borrowed_books()
        self.show_books_gui()

        QMessageBox.information(self.MainWindow, "Book Borrowed", f"Book borrowed: {title} (ID: {book_id})")

        #  Cập nhật MongoDB ngầm phía sau (sau khi giao diện đã hiển thị)


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

    def show_borrowed_books(self):
        """
        Hiển thị sách đang mượn của người dùng với user_id, từ cả MongoDB và RAM (self.list).
        """
        borrowed_books=[]
        self.tableWidgetsachmuon.clearContents()
        self.tableWidgetsachmuon.setRowCount(0)
        borrow_receipt_id = self.dc.get_bookborrow_from_userid(self.user_id)
        print("Receipt IDs:", borrow_receipt_id)
        for receipt_id in borrow_receipt_id:
            books = self.dc.get_book_from_receiptid(receipt_id)
            print("Borrowed from DB:", books)
            if books:
                # Gắn receipt_id vào từng book
                for book in books:
                    book["receipt_id"] = receipt_id
                borrowed_books.extend(books)

        # Trường hợp không có sách mượn nào
        if not borrowed_books:
            self.tableWidgetsachmuon.setColumnCount(1)
            self.tableWidgetsachmuon.setHorizontalHeaderLabels(["Notice"])
            self.tableWidgetsachmuon.setRowCount(1)
            item = QTableWidgetItem("No books borrowed")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidgetsachmuon.setItem(0, 0, item)
            self.tableWidgetsachmuon.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            return

        # Cấu hình bảng sách mượn
        self.tableWidgetsachmuon.setColumnCount(6)
        self.tableWidgetsachmuon.setHorizontalHeaderLabels([
            "Receipt ID", "ISBN", "Book Name", "Author", "Pub Year", "Quantity"
        ])

        for book in borrowed_books:
            row = self.tableWidgetsachmuon.rowCount()
            self.tableWidgetsachmuon.insertRow(row)

            columns = [
                str(book.get("receipt_id", "")),
                str(book["book_id"]),
                str(book["title"]),
                str(book["author"]),
                str(book["publication_year"]),
                str(book["quantity"]),
            ]

            for col, value in enumerate(columns):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidgetsachmuon.setItem(row, col, item)

            # columns = [
            #     str(book['book_id']),
            #     str(book['title']),
            #     str(book['author']),
            #     str(book['publication_year']),
            #     str(book['quantity'])
            # ]
            #
            # for col, value in enumerate(columns):
            #     item = QTableWidgetItem(value)
            #     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            #     self.tableWidgetsachmuon.setItem(row, col, item)

        # Giãn đều các cột
        self.tableWidgetsachmuon.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def show_loading_dialog(parent, message):
        progress = QProgressDialog(message, None, 0, 0, parent)
        progress.setWindowTitle("Loading")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)
        progress.show()
        QApplication.processEvents()
        return progress
    def refresh_data(self):
        """Hàm gọi khi QTimer timeout, cập nhật lại dữ liệu giao diện."""
        self.show_books_gui()
        self.show_borrowed_books()

