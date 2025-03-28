import hashlib
import random
import string

import bcrypt
from PyQt6.QtWidgets import QMessageBox
from numpy.ma.core import append
from pymongo.errors import PyMongoError

from lbs.JsonFileFactory import JsonFileFactory
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class Employee:
    def __init__(self, EmployeeId = None, EmployeeName = None, UserName = None, Password = None):
        self.EmployeeId=EmployeeId
        self.EmployeeName=EmployeeName
        self.UserName=UserName
        self.Password=Password
    def __str__(self):
        return f"{self.EmployeeId}\t{self.EmployeeName}"

class User:
    def __init__(self, user_id, name, username, password, role, bookborrow=None, receipt_id=None):
        self.user_id = user_id
        self.name = name
        self.username = username
        self.password = password
        self.role = role
        if bookborrow is None:
            self.bookborrow = []
        else:
            self.bookborrow = bookborrow
        self.receipt_id = receipt_id

    def __str__(self):
        return f"{self.user_id}\t{self.name}\t{self.role}\t{self.bookborrow}\t{self.receipt_id}"

class BorrowReceipt():
    def __init__(self, receipt_id,user_id, name, book_id,title, quantity_borrow):
        self.receipt_id = receipt_id
        self.borrower = user_id
        self.title=title
        self.name=name
        self.book_id=book_id
        self.quantity_borrow=quantity_borrow

    def __str__(self):
        return f"{self.receipt_id}\t{self.borrower}\t{self.name}\t{self.book_id}\t{self.title}\t{self.quantity_borrow}"

class Book:
    def __init__(self, book_id, title, author, publication_year, quantity, link):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.quantity = quantity
        self.link = link
    def __str__(self):
        return f"{self.book_id}\t{self.title}\t {self.author}\t{self.publication_year}\t{self.quantity}"

class DataConnector():
    def __init__(self):
        super().__init__()
        self.list=[]
        uri = "mongodb+srv://admin:123@cluster0.7rh5y.mongodb.net/"

        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client["Chatbot"]  # Databas
        self.allusers=self.get_all_users()
        self.allbooks=self.get_all_books()
        # Send a ping to confirm a successful connection
        self.borrowed_books = []  # Khởi tạo danh sách sách mượn trong suốt phiên làm việc


    def __str__(self):
        pass

    def get_all_users(self):
        collection = self.db["users"]
        projection = {"user_id": 1, "name": 1, "username": 1,"password":1, 'role':1, 'receipt_id':1}
        data = collection.find({}, projection)
        users=[]
        for i in data:
            user = User(
                user_id=i.get("user_id"),
                name=i.get("name"),
                username=i.get("username"),
                password=i.get("password"),
                role=i.get("role"),
                receipt_id=i.get("receipt_id")
            )
            users.append(user)
        return users

    def get_all_books(self):
        collection = self.db["book"]
        projection = {"book_id": 1, "title": 1, "author": 1, "publication_year": 1, 'quantity': 1, 'link': 1}
        data = collection.find({}, projection)
        books = []
        for i in data:
            book = Book(
                book_id=i.get("book_id"),
                title=i.get("title"),
                author=i.get("author"),
                publication_year=i.get("publication_year"),
                quantity=i.get("quantity"),
                link=i.get("link")
            )
            books.append(book)
        return books

    def get_all_borrow_receipt(self):
        collection = self.db["borrowreceipt"]
        projection = {"receipt_id": 1, "borrower": 1, "title": 1, "name": 1, 'book_id': 1, 'quantity': 1}
        data = collection.find({}, projection)
        receipts = []
        for i in data:
            receipt = BorrowReceipt(
                receipt_id=i.get("receipt_id"),
                user_id=i.get("borrower"),
                title=i.get("title"),
                name=i.get("name"),
                book_id=i.get("book_id"),
                quantity_borrow=i.get("quantity")
            )
            receipts.append(receipt)
        return receipts

    # def verify_password(self, plain_text_password, hashed_password):
    #     """Kiểm tra mật khẩu nhập vào với mật khẩu đã băm"""
    #     return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

    def get_bookborrow_from_userid(self,user_id):
        for user in self.allusers:
            if user.user_id == user_id:
                return user.receipt_id
        return None

    def login(self,username,password):
        account=self.get_all_users()
        for e in account:
            if e.username == username and e.password == password:
                return e  # Trả về thông tin tài khoản nếu đúng
        return None

    def get_book_from_receiptid(self, receipt_id):
        book_borrowed = []

        # Nếu là list, lấy phần tử đầu tiên
        if isinstance(receipt_id, list):
            receipt_id = receipt_id[0]

        allreceipts = self.get_all_borrow_receipt()
        receipt = next((r for r in allreceipts if r.receipt_id == receipt_id), None)

        if not receipt:
            return None

        book_id = receipt.book_id
        quantity = receipt.quantity_borrow

        if quantity is None:
            return []  # Không thêm sách nếu quantity là None

        book = next((b for b in self.allbooks if b.book_id == book_id), None)
        if book:
            book_borrowed.append({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "publication_year": book.publication_year,
                "quantity": str(quantity),
                "link": book.link
            })

        return book_borrowed

    def add_new_user(self,user_id,name,username,password):
        collection=self.db["users"]
        # projection = {"user_id": 1, "name": 1, "username": 1, "password": 1, 'role': 1, 'receipt_id': 1}
        # salt = bcrypt.gensalt()
        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        user = {
            "user_id": user_id,  # Tạo ID duy nhất
            "name": name,
            "username": username,
            "password": password,  # Lưu mật khẩu dưới dạng hash
            "role": "Student",
            "receipt_id": []
        }
        collection.insert_one(user)
        return True

    def update_new_password(self, user_id, newpassword):
        """Cập nhật mật khẩu mới dựa trên user_id trong MongoDB."""
        try:
            collection = self.db["users"]

            # Băm mật khẩu trước khi lưu (nếu cần)
            # hashed_password = hashlib.sha256(newpassword.encode()).hexdigest()

            # Cập nhật password theo user_id
            result = collection.update_one(
                {"user_id": user_id},
                {"$set": {"password": newpassword}}
            )

            # Kiểm tra nếu có tài khoản được cập nhật
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"MongoDB Update Error: {e}")
            return False

    def add_new_book(self,book_id,title,author,publication_year,quantity,link):
        collection = self.db["book"]
        projection = {"book_id": 1, "title": 1, "author": 1, "publication_year": 1, 'quantity': 1}
        user = {
            "book_id": book_id,  # Tạo ID duy nhất
            "title": title,
            "author": author,
            "publication_year": publication_year,  # Lưu mật khẩu dưới dạng hash
            "quantity": quantity,
            "link":link
        }
        collection.insert_one(user)
        return True

    def generate_unique_receipt_id(self):
        """
        Tạo một receipt_id ngẫu nhiên không trùng trong MongoDB và RAM.
        """
        existing_ids = set()

        # Lấy receipt_id từ MongoDB
        collection = self.db["borrowreceipt"]
        for doc in collection.find({}, {"receipt_id": 1}):
            if "receipt_id" in doc:
                existing_ids.add(doc["receipt_id"])

        # Lấy receipt_id từ RAM (self.list)
        for r in self.list:
            existing_ids.add(r.receipt_id)

        # Tạo mới cho đến khi không trùng
        while True:
            rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            receipt_id = f"A{rand_part}"
            if receipt_id not in existing_ids:
                return receipt_id

    def create_borrow_receipt(self, user_id, username, book_id, quantity_borrow):
        """
        Tạo phiếu mượn mới, lưu vào MongoDB, và cập nhật số lượng sách còn lại.
        """
        try:
            # Tìm sách trong danh sách RAM
            book = next((b for b in self.allbooks if b.book_id == book_id), None)
            if not book:
                print("Book not found.")
                return False

            if book.quantity < quantity_borrow:
                print("Not enough books in stock.")
                return False

            # Trừ số lượng sách trong RAM
            book.quantity -= quantity_borrow
            # Cập nhật số lượng sách mới trong MongoDB
            books_collection = self.db["book"]
            books_collection.update_one(
                {"book_id": book_id},
                {"$set": {"quantity": book.quantity}}  # quantity đã được giảm ở trên
            )
            # Tạo receipt mới
            new_receipt_id = self.generate_unique_receipt_id()
            print(new_receipt_id)
            receipt = BorrowReceipt(
                receipt_id=new_receipt_id,
                user_id=user_id,
                name=username,
                book_id=book_id,
                title=book.title,
                quantity_borrow=quantity_borrow
            )

            # Lưu receipt vào RAM
            self.list.append(receipt)

            # Lưu receipt vào MongoDB
            borrowreceipt_collection = self.db["borrowreceipt"]
            borrowreceipt_collection.insert_one({
                "receipt_id": receipt.receipt_id,
                "borrower": receipt.borrower,
                "name": receipt.name,
                "book_id": receipt.book_id,
                "title": receipt.title,
                "quantity": receipt.quantity_borrow
            })


            # Cập nhật receipt_id mới vào user (dưới dạng danh sách)
            users_collection = self.db["users"]
            users_collection.update_one(
                {"user_id": user_id},
                {"$push": {"receipt_id": new_receipt_id}}  # Thêm vào cuối mảng
            )
            return True

        except Exception as e:
            print(f"Error while creating receipt: {e}")
            return False

    def update_book_quantity(self, book_id, new_quantity):
        """
        Cập nhật số lượng sách trong danh sách allbooks.
        """
        for book in self.allbooks:
            if book.book_id == book_id:
                book.quantity = new_quantity
                break

    def remove_borrowed_book(self, book_id, user_id):
        """
        Xóa sách khỏi phiếu mượn và cập nhật số lượng sách trong MongoDB (không dùng RAM).
        """
        try:
            # Tìm phiếu mượn tương ứng trong MongoDB
            receipt = self.db["borrowreceipt"].find_one({
                "book_id": book_id,
                "borrower": user_id
            })

            if not receipt:
                print("Receipt not found in MongoDB.")
                return False

            quantity_returned = receipt.get("quantity", 0)

            # Tăng lại số lượng sách trong kho
            self.db["book"].update_one(
                {"book_id": book_id},
                {"$inc": {"quantity": quantity_returned}}
            )

            # Xóa phiếu mượn khỏi MongoDB
            self.db["borrowreceipt"].delete_one({
                "_id": receipt["_id"]
            })

            # Xóa receipt_id khỏi user
            self.db["users"].update_one(
                {"user_id": user_id},
                {"$pull": {"receipt_id": receipt["receipt_id"]}}
            )

            print(f"Removed receipt {receipt['receipt_id']} for book {book_id} and user {user_id}")
            return True

        except Exception as e:
            print(f"Error while removing borrowed book from MongoDB: {e}")
            return False

dc=DataConnector()