from time import sleep

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from ui.Login_forgotyourpassword import Ui_Form
import uuid
from lbs.DataConnector import User, DataConnector


class ForgotyoupasswordAdjust(Ui_Form):
    def __init__(self):
        self.dc=DataConnector()

    def setupUi(self, Form, main_window=None):
        super().setupUi(Form)
        self.MainWindow = Form
        self.MainWindow.showMaximized()
        self.mainwindow=main_window
        if self.mainwindow:
                self.pushButton_Signin.clicked.connect(self.mainwindow.showLoginForm)
        self.lineEditUserName.textChanged.connect(self.validate_input)
        self.lineEditFirstUserID.textChanged.connect(self.validate_input)
        self.lineEditConfirmPassword.textChanged.connect(self.validate_input)
        self.pushButton_Login.clicked.connect(self.resetpassword)
    def validate_input(self):
        """Kiểm tra tài khoản và mật khẩu theo thời gian thực."""
        instanceusername = self.lineEditUserName.text()
        user_id = self.lineEditFirstUserID.text()
        firstpassword = self.lineEditFirstPassword.text()
        confirmpassword = self.lineEditConfirmPassword.text()
        instance_information = self.dc.get_all_users()

        # Kiểm tra user có tồn tại không
        found = False
        while found==False:
            for i in instance_information:
                if instanceusername == i.username and user_id == i.user_id:
                    found = True
            if found:
                self.labelNotificationUserNameConfirm.setText("✅ Account found")
                break
            else:
                self.labelNotificationUserNameConfirm.setText("❌ Can not find your Account")
                return False
        # Kiểm tra mật khẩu nhập lại có khớp không
        if firstpassword and confirmpassword:
            if firstpassword != confirmpassword:
                self.labelNotificationPasswordConfirm.setText("❌ Passwords do not match, please try again")
            else:
                self.labelNotificationPasswordConfirm.setText("✅ Passwords match")

    def resetpassword(self):
        user_id = self.lineEditFirstUserID.text()
        instance_information = self.dc.get_all_users()
        instanceusername=self.lineEditUserName.text()
        firstpassword = self.lineEditFirstPassword.text()
        confirmpassword = self.lineEditConfirmPassword.text()

        found = False
        for i in instance_information:
            if instanceusername == i.username and user_id == i.user_id:
                found = True
                break

        if not found:
            self.show_error_message("Account Error", "Can not find your Account")
            return

        if firstpassword != confirmpassword:
            self.labelNotificationPasswordConfirm.setText("Passwords do not match, please try again")
            return

        # Nếu cả hai điều kiện đúng, update mat khau vào Database (MongoDB)
        newpassword = confirmpassword  # Có thể băm mật khẩu tại đây nếu cần
        result = self.dc.update_new_password(user_id,newpassword)

        # Nếu cập nhật tài khoản thành công, hiển thị thông báo
        if result:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Update Password Successful")
            msg_box.setText("Your account has been update successfully! Please Sign In")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            # sleep(2)
            # self.mainwindow.showLoginForm()
            QTimer.singleShot(2000, self.mainwindow.showLoginForm)
            return True
        else:
            self.show_error_message("Update Failed", "Can not change your account password. Please contact the Librarian.")
            return False

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    def showWindow(self):
        self.MainWindow.showMaximized()
