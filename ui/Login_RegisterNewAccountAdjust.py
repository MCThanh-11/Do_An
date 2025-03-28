import uuid
from time import sleep

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from lbs.DataConnector import DataConnector
from ui.Login_RegisterNewAccount import Ui_Form


class RegisterNewAccount(Ui_Form):
    def __init__(self):
        super().__init__()
        self.dc = DataConnector()

    def setupUi(self, Form, main_window=None):
        super().setupUi(Form)
        self.MainWindow = Form
        self.MainWindow.showMaximized()
        self.main_window=main_window
        self.setUpSignalAndSlot()
        if self.main_window:
                self.pushButton_Signin.clicked.connect(main_window.showLoginForm)

        self.lineEditConfirmPassword.textChanged.connect(self.validate_input)
        self.lineEditFirstPassword.textChanged.connect(self.validate_input)

    def setUpSignalAndSlot(self):
        self.pushButton_Signup.clicked.connect(self.gen_new_account)

    def gen_new_account(self):
        user_id = str(uuid.uuid4())  # Tạo ID mới
        name = self.lineEditNewName.text()
        username = self.lineEditNewUserName.text()
        instanceusername = self.dc.get_all_users()
        firstpassword = self.lineEditFirstPassword.text()
        confirmpassword = self.lineEditConfirmPassword.text()

        # Kiểm tra username đã tồn tại hay chưa
        for i in instanceusername:
            if username == i['username']:
                self.labelNotification_newUserName.setText("This username is already taken, please choose another one.")
                return False  # Thoát ngay nếu username đã tồn tại

        # Kiểm tra mật khẩu có khớp không
        if firstpassword != confirmpassword:
            self.labelNotification_Password.setText("Passwords do not match, please try again.")
            return False  # Thoát ngay nếu mật khẩu không khớp

        # Nếu cả hai điều kiện đúng, thêm user vào Database
        password_hashed = confirmpassword  # Có thể băm mật khẩu tại đây nếu cần
        result = self.dc.add_new_user(user_id, name, username, password_hashed)

        # Nếu thêm tài khoản thành công, hiển thị thông báo
        if result:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Registration Successful")
            msg_box.setText("Your account has been created successfully! Please Sign In")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            QTimer.singleShot(1000, self.main_window.showLoginForm)
            # sleep(2)
            # self.main_window.showLoginForm()  # Chuyển sang màn hình đăng nhập
            return True
        else:
            self.show_error_message("Registration Failed", "Account creation was unsuccessful. Please check your input.")
            return False  # Nếu không thêm được tài khoản

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def showWindow(self):
        self.MainWindow.showMaximized()


    def validate_input(self):
        firstpassword = self.lineEditFirstPassword.text()
        confirmpassword = self.lineEditConfirmPassword.text()
        if firstpassword and confirmpassword:
            if firstpassword != confirmpassword:
                self.labelNotification_Password.setText("❌ Passwords do not match, please try again")
            else:
                self.labelNotification_Password.setText("✅ Passwords match")