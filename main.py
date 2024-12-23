import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox, QInputDialog, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel
)
from PyQt5.QtCore import QThread, pyqtSignal
from db_connection import create_connection  
import time

class UpdateThread(QThread):
    update_signal = pyqtSignal()

    def run(self):
        while True:
            time.sleep(5)  # هر ۵ ثانیه یک‌بار به‌روزرسانی انجام می‌شود
            self.update_signal.emit()

class PaginatedBookView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paginated Book List")
        self.setGeometry(100, 100, 800, 600)

        # تعداد کتاب‌ها در هر صفحه
        self.items_per_page = 10
        self.current_page = 1

        # جدول نمایش کتاب‌ها
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Book ID", "Title", "Author"])

        # دکمه‌های صفحه‌بندی
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.page_label = QLabel(f"Page: {self.current_page}")

        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

        # چیدمان دکمه‌ها
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.page_label)
        button_layout.addWidget(self.next_button)

        # چیدمان اصلی
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_data()

        # راه‌اندازی Thread برای به‌روزرسانی لحظه‌ای
        self.update_thread = UpdateThread()
        self.update_thread.update_signal.connect(self.load_data)
        self.update_thread.start()

    def load_data(self):
        """بارگذاری داده‌های صفحه فعلی از دیتابیس"""
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            offset = (self.current_page - 1) * self.items_per_page
            cursor.execute("""
                SELECT book_id, title, author
                FROM Books
                LIMIT %s OFFSET %s
            """, (self.items_per_page, offset))
            books = cursor.fetchall()
            self.table.setRowCount(0)

            for row, book in enumerate(books):
                self.table.insertRow(row)
                for col, data in enumerate(book):
                    self.table.setItem(row, col, QTableWidgetItem(str(data)))

            cursor.close()
            connection.close()

            self.page_label.setText(f"Page: {self.current_page}")

    def next_page(self):
        """رفتن به صفحه بعدی"""
        self.current_page += 1
        self.load_data()

    def prev_page(self):
        """رفتن به صفحه قبلی"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

class BookManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Book Management")
        self.setGeometry(100, 100, 600, 400)
        self.edit_button = QPushButton("Edit Book", self)
        self.edit_button.clicked.connect(self.edit_book)

        layout = QVBoxLayout()
        self.book_list = QListWidget(self)
        layout.addWidget(self.book_list)

        self.add_button = QPushButton("Add Book", self)
        self.edit_button = QPushButton("Edit Book", self)
        self.delete_button = QPushButton("Delete Book", self)
        self.filter_button = QPushButton("Filter Available Books", self)
        self.paginated_view_button = QPushButton("View Paginated Books", self)

        self.add_button.clicked.connect(self.add_book)
        self.edit_button.clicked.connect(self.edit_book)
        self.delete_button.clicked.connect(self.delete_book)
        self.filter_button.clicked.connect(self.filter_books)
        self.paginated_view_button.clicked.connect(self.open_paginated_view)

        layout.addWidget(self.book_list)
        layout.addWidget(self.add_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.filter_button)
        layout.addWidget(self.paginated_view_button)

        self.setLayout(layout)
        self.load_books()

    def edit_book(self):
        print("Editing book...")
        
    def load_books(self):
        """بارگذاری لیست کتاب‌ها از دیتابیس"""
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT book_id, title, author FROM Books")
            books = cursor.fetchall()
            self.book_list.clear()
            for book in books:
                self.book_list.addItem(f"{book[0]} - {book[1]} by {book[2]}")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            cursor.close()
            connection.close()

    def add_book(self):
        """افزودن کتاب جدید"""
        title, ok1 = QInputDialog.getText(self, "Add Book", "Enter Book Title:")
        author, ok2 = QInputDialog.getText(self, "Add Book", "Enter Author Name:")
        
        if ok1 and ok2:
            if len(title) > 15:
                QMessageBox.warning(self, "Error", "Title is too long. Maximum length is 15 characters.")
                return
            if len(author) > 15:
                QMessageBox.warning(self, "Error", "Author name is too long. Maximum length is 15 characters.")
                return
            
            try:
                connection = create_connection()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Books (title, author, copies_available, category) VALUES (%s, %s, %s, %s)", 
                               (title, author, 1, 'Other'))
                connection.commit()
                QMessageBox.information(self, "Success", "Book Added Successfully!")
                self.load_books()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))
            finally:
                cursor.close()
                connection.close()

    def delete_book(self):
        """حذف کتاب انتخاب‌شده"""
        selected_item = self.book_list.currentItem()
        if selected_item:
            book_id = selected_item.text().split(" - ")[0]
            try:
                connection = create_connection()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Books WHERE book_id = %s", (book_id,))
                connection.commit()
                QMessageBox.information(self, "Success", "Book Deleted Successfully!")
                self.load_books()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))
            finally:
                cursor.close()
                connection.close()

    def filter_books(self):
        """فیلتر کردن کتاب‌های موجود"""
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT book_id, title, author FROM Books WHERE copies_available > 0")
            books = cursor.fetchall()
            self.book_list.clear()
            for book in books:
                self.book_list.addItem(f"{book[0]} - {book[1]} by {book[2]}")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            cursor.close()
            connection.close()

    def open_paginated_view(self):
        """باز کردن نمای صفحه‌بندی کتاب‌ها"""
        self.paginated_view = PaginatedBookView()
        self.paginated_view.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())
