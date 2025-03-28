import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox, QFileDialog

# Import giao diện đã tạo từ Qt Designer
from models.QABot_simpleInteraction import ChatBot
from models.QABot_withPDF import QABot
from models.prepare_vector_db import VectorDBProcess
from ui.Chatbot_interface import Ui_MainWindow


class ChatBotApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username  # Lưu tên người dùng
        self.first_message_sent = False  # Biến kiểm tra tin nhắn đầu tiên
        self.fade_animation = None  # Lưu animation để tránh bị thu gom rác
        self.vector_db_processor = VectorDBProcess()
        # Thiết lập giao diện
        self.setupUi(self)
        self.setupSignalAndSlot()

        # Hiển thị cửa sổ
        self.showMaximized()
        self.selected_file_path=None
    # Kết nối sự kiện
    def setupSignalAndSlot(self):
        self.pushButtonSubmitext.clicked.connect(self.send_message)
        self.lineEditInputQuestion.installEventFilter(self)  # Hỗ trợ Enter để gửi
        self.pushButtonopenfile.clicked.connect(self.handle_file_selection)
        self.pushButtonRefresh.clicked.connect(self.refresh_functionprocessing)

        # Kết nối nút cuộn xuống
        self.pushButtonScrolldown.clicked.connect(self.scroll_to_bottom)

        # Tạo layout trong scrollArea để chứa tin nhắn
        self.chat_layout = QtWidgets.QVBoxLayout()
        self.chat_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.addLayout(self.chat_layout)

        # Đảm bảo ScrollArea tự điều chỉnh kích thước
        self.scrollAreaAnswer.setWidgetResizable(True)

        # Hiển thị lời chào khi khởi động
        self.welcome_label = QtWidgets.QLabel(f"Xin chào, {self.username}!")
        self.welcome_label.setStyleSheet("font-size: 30px; font-weight: bold; padding: 10px;")
        self.welcome_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Đặt lời chào vào layout trung tâm
        self.welcome_container = QtWidgets.QWidget()
        welcome_layout = QtWidgets.QVBoxLayout(self.welcome_container)
        welcome_layout.addStretch()
        welcome_layout.addWidget(self.welcome_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addStretch()

        self.chat_layout.addWidget(self.welcome_container)

    def eventFilter(self, source, event):
        """Xử lý sự kiện nhấn phím Enter trong QTextEdit"""
        if source == self.lineEditInputQuestion and event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Return and not event.modifiers():
                self.send_message()
                return True
        return QtWidgets.QMainWindow.eventFilter(self, source, event)

    def send_message(self):
        """Lấy nội dung từ lineEditInputQuestion và hiển thị trong giao diện"""
        message = self.lineEditInputQuestion.toPlainText().strip()
        if message:
            self.add_message(message, "user")  # Hiển thị tin nhắn của người dùng
            self.lineEditInputQuestion.clear()

            # Chọn chế độ xử lý dựa trên file PDF (nếu có)
            if self.selected_file_path:
                try:
                    print(message)
                    from models.QABot_withPDF import QABot  # Đảm bảo bạn import đúng
                    qa_bot = QABot("7cfc08f9f0266495db28836e118354831597ff6ca7e81342469e410b68293d9a","../vectorstorage/db_faiss")
                    answer = qa_bot.get_answer(message)
                    print(answer)
                except Exception as e:
                    answer = f"Lỗi khi xử lý với file PDF: {str(e)}"
            else:
                print(message)
                chatbot = ChatBot("7cfc08f9f0266495db28836e118354831597ff6ca7e81342469e410b68293d9a")
                answer = chatbot.send_message(message)
                print(answer)
            # Phản hồi từ máy chủ
                QtCore.QTimer.singleShot(0, lambda: self.add_message(answer, "server"))

    def add_message(self, text, sender):
        """Thêm một tin nhắn vào giao diện chat"""

        # Xóa lời chào sau khi gửi tin nhắn đầu tiên với hiệu ứng fade-out
        if not self.first_message_sent:
            self.fade_out_welcome_message()
            self.first_message_sent = True

        message_container = QtWidgets.QWidget()  # Tạo container cho tin nhắn
        message_layout = QtWidgets.QHBoxLayout(message_container)
        message_layout.setContentsMargins(5, 2, 5, 2)  # Giảm margin để gọn hơn

        message_label = QtWidgets.QLabel(text)
        message_label.setWordWrap(True)

        # Tính toán kích thước tin nhắn theo nội dung nhưng không vượt quá 70% chiều rộng cửa sổ
        max_width = int(self.width() * 0.7)  # 70% chiều rộng cửa sổ
        message_label.setMaximumWidth(max_width)
        message_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)

        # Điều chỉnh kích thước dựa trên nội dung thực tế
        message_label.adjustSize()

        # Bọc nội dung trong một QHBoxLayout để căn chỉnh dễ dàng hơn
        message_wrapper = QtWidgets.QWidget()
        message_layout_wrapper = QtWidgets.QHBoxLayout(message_wrapper)
        message_layout_wrapper.setContentsMargins(0, 0, 0, 0)
        message_layout_wrapper.setSpacing(5)  # Khoảng cách giữa tin nhắn và lề

        if sender == "user":
            message_label.setStyleSheet(
                "background-color: lightblue; padding: 8px; border-radius: 10px;"
            )
            message_layout_wrapper.addStretch()
            message_layout_wrapper.addWidget(message_label)
        else:
            message_label.setStyleSheet(
                "background-color: lightgreen; padding: 8px; border-radius: 10px;"
            )
            message_layout_wrapper.addWidget(message_label)
            message_layout_wrapper.addStretch()

        # Thêm vào giao diện chính
        self.chat_layout.addWidget(message_wrapper)

        # Cập nhật kích thước tin nhắn theo nội dung
        message_label.adjustSize()

        # Cuộn xuống tin nhắn mới nhất
        self.scroll_to_bottom()

    def fade_out_welcome_message(self):
        """Làm mờ lời chào trước khi xóa nó khỏi giao diện"""
        if hasattr(self, "welcome_container") and self.welcome_container is not None:
            effect = QtWidgets.QGraphicsOpacityEffect(self.welcome_container)
            self.welcome_container.setGraphicsEffect(effect)

            # Tạo animation để giảm độ mờ từ 1 → 0
            self.fade_animation = QtCore.QPropertyAnimation(effect, b"opacity")
            self.fade_animation.setDuration(1)  # 0.5 giây
            self.fade_animation.setStartValue(1)
            self.fade_animation.setEndValue(0)

            # Kết nối sự kiện hoàn thành animation với hàm xóa
            self.fade_animation.finished.connect(self.remove_welcome_message)
            self.fade_animation.start()

    def remove_welcome_message(self):
        """Xóa lời chào khỏi giao diện sau khi hiệu ứng hoàn tất"""
        if self.welcome_container:
            self.chat_layout.removeWidget(self.welcome_container)
            self.welcome_container.deleteLater()
            self.welcome_container = None

    def scroll_to_bottom(self):
        """Cuộn xuống tin nhắn mới nhất"""
        QtWidgets.QApplication.processEvents()
        self.scrollAreaAnswer.verticalScrollBar().setValue(self.scrollAreaAnswer.verticalScrollBar().maximum())

    def handle_file_selection(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Chọn File PDF",
            "",
            "PDF Files (*.pdf)"
        )
        self.pushButtonopenfile.setIcon(
            QIcon("D:\\CodeArchive\\KTLT\\duanmonhoc\\images\\ic_processing.png"))

        # Kiểm tra nếu file_path rỗng
        if not file_path:
            self.pushButtonopenfile.setIcon(
                QIcon("D:\\CodeArchive\\KTLT\\duanmonhoc\\images\\ic_add-button.png"))
            return

        if file_path:
            try:
                    """
                    # Cắt tên file nếu quá dài (trên 25 ký tự)
                    file_name = file_path.split('/')[-1]
                    if len(file_name) > 25:
                        file_name = file_name[:22] + "..."
                    """
                    # Lưu đường dẫn file
                    self.selected_file_path = file_path

                    #Xử lý vectorDB từ đường dẫn
                    self.vector_db_path=self.vector_db_processor.create_db_from_files(file_path)

                    # Đổi icon của nút pushButtonopenfile thành icon file PDF
                    self.pushButtonopenfile.setIcon(
                        QIcon("D:\\CodeArchive\\KTLT\\duanmonhoc\\images\\ic_pdf-file.png"))
            #Bắt lỗi file pdf
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể mở file: {str(e)}")

    def refresh_functionprocessing(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Xác nhận tạo mới hội thoại!")
        dlg.setText("Bạn có muốn tạo mới hội thoại không?")
        dlg.setIcon(QMessageBox.Icon.Question)
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        dlg.setStandardButtons(buttons)

        if dlg.exec() == QMessageBox.StandardButton.Yes:
            # ✅ Xóa tất cả widget trong chat_layout
            while self.chat_layout.count():
                item = self.chat_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

            # ✅ Thêm lại lời chào như ban đầu
            self.first_message_sent = False
            self.welcome_label = QtWidgets.QLabel(f"Xin chào, {self.username}!")
            self.welcome_label.setStyleSheet("font-size: 30px; font-weight: bold; padding: 10px;")
            self.welcome_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            self.welcome_container = QtWidgets.QWidget()
            welcome_layout = QtWidgets.QVBoxLayout(self.welcome_container)
            welcome_layout.addStretch()
            welcome_layout.addWidget(self.welcome_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            welcome_layout.addStretch()
            self.chat_layout.addWidget(self.welcome_container)

            # ✅ Reset các biến và giao diện
            self.lineEditInputQuestion.setText("Đang chờ câu hỏi")
            self.selected_file_path = None
            self.pushButtonopenfile.setIcon(QIcon("D:\\CodeArchive\\KTLT\\duanmonhoc\\images\\ic_add-button.png"))
            #self.vector_db_processor.clear_database()  # Nếu cần
"""
# Chạy ứng dụng
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ChatBotApp(username="UserName1")  # Tên người dùng tùy chỉnh
    window.show()  # Hiển thị cửa sổ
    sys.exit(app.exec())

if __name__ == "__main__":
    api_key = "7cfc08f9f0266495db28836e118354831597ff6ca7e81342469e410b68293d9a"  # Thay thế bằng API Key thực tế
    vector_db_path = "../vectorstorage/db_faiss"

    bot = QABot(api_key, vector_db_path)
    question = "Nội dung sách là gì?"
    response = bot.get_answer(question)

    print(response)
"""