import sys
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QWidget, QApplication
from lbs.DataConnector import DataConnector
from ui.Login_MainWindow import Ui_MainWindow
from ui.QuanLySachExt import QuanLySachExt
from ui.QuanliMuonSachExt import QuanLyMuonSachExt

class Dangnhap(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.book_borrow = []
        self.MainWindow = None  # Sẽ gán sau khi setupUi

    def setupUi(self, MainWindow):
        """
        Gọi setupUi cho giao diện đăng nhập, trên cùng 1 QMainWindow.
        """
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Kết nối tín hiệu nút
        self.setupSignalAndSlot()

    def showWindow(self):
        """Hiển thị cửa sổ chính ở chế độ bình thường hoặc full."""
        self.MainWindow.showMaximized()

    def setupSignalAndSlot(self):
        """Kết nối các nút với hàm xử lý."""
        self.pushButton_Login.clicked.connect(self.process_login)
        self.pushButton_Signup.clicked.connect(self.Signup_handle)
        self.pushButton_resetPassword.clicked.connect(self.Resetpassword_handle)

    def Signup_handle(self):
        print("Switching to Signup Form...")

        # Xóa các widget hiện tại trong gridLayout_3
        for i in reversed(range(self.gridLayout_3.count())):
            item = self.gridLayout_3.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Import giao diện đăng ký
        from ui.Login_RegisterNewAccountAdjust import RegisterNewAccount
        self.registerForm = QWidget(self.centralwidget)
        self.registerUi = RegisterNewAccount()
        # setupUi cho form đăng ký, truyền self (là main_window) để quay lại login được
        self.registerUi.setupUi(self.registerForm, main_window=self)
        # Khi nhấn "Sign in" thì quay lại form đăng nhập
        self.registerUi.pushButton_Signin.clicked.connect(self.showLoginForm)

        # Thêm form đăng ký vào layout
        self.gridLayout_3.addWidget(self.registerForm, 1, 1, 4, 1)

    def showLoginForm(self):
        """Trở về giao diện đăng nhập bên trong cùng cửa sổ."""
        print("Switching back to Login Form...")

        # Xóa các widget hiện tại (form đăng ký / quên mật khẩu)
        for i in reversed(range(self.gridLayout_3.count())):
            item = self.gridLayout_3.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Thêm lại giao diện login (các control gốc)
        # Nhưng ta đã **có sẵn** các control login (lineEditUserName...) trong Dangnhap,
        # nên chỉ việc gọi lại setupUi trên chính layout này:
        self.setupUi(self.MainWindow)
        self.showWindow()  # Tùy chọn hiển thị full

    def Resetpassword_handle(self):
        print("Switching to Reset Password Form...")

        # Xóa widget giao diện login
        for i in reversed(range(self.gridLayout_3.count())):
            item = self.gridLayout_3.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        from ui.Login_forgotyourpasswordAdjust import ForgotyoupasswordAdjust
        self.resetPasswordForm = QWidget(self.centralwidget)
        self.resetPassword = ForgotyoupasswordAdjust()
        self.resetPassword.setupUi(self.resetPasswordForm, main_window=self)

        self.gridLayout_3.addWidget(self.resetPasswordForm, 1, 1, 4, 1)
        # Khi nhấn "Sign in" thì quay lại login
        self.resetPassword.pushButton_Signin.clicked.connect(self.showLoginForm)

    def process_login(self):
        print("Logging in...")
        ds = DataConnector()
        uid = self.lineEditUserName.text()
        pwd = self.lineEditPassword.text()
        emp = ds.login(uid, pwd)

        if emp is not None:
            name = emp.name
            userid = emp.user_id
            role = emp.role

            if role == "Admin":
                # Xóa các widget giao diện login
                for i in reversed(range(self.gridLayout_3.count())):
                    item = self.gridLayout_3.itemAt(i)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)

                # Dùng QuanLySachExt ngay trong cửa sổ này
                self.admin_ui = QuanLySachExt(name, userid)
                self.admin_ui.setupUi(self.MainWindow)

                # Gọi hàm phóng to cửa sổ
                self.MainWindow.showMaximized()

            elif role == "User":
                # Xóa các widget giao diện login
                for i in reversed(range(self.gridLayout_3.count())):
                    item = self.gridLayout_3.itemAt(i)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)

                self.user_ui = QuanLyMuonSachExt(name, userid)
                self.user_ui.setupUi(self.MainWindow)

                # Gọi hàm phóng to cửa sổ
                self.MainWindow.showMaximized()

                self.user_ui = QuanLyMuonSachExt(name, userid)
                self.user_ui.setupUi(self.MainWindow)
                self.showWindow()
        else:
            self.labelNotification.setStyleSheet("font-weight: bold; color: red")
            self.labelNotification.setText("Incorrect Username or Password!")

#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = QMainWindow()
#     ui = Dangnhap()
#     ui.setupUi(main_window)
#     ui.showWindow()
#     sys.exit(app.exec())
