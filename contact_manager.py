import sys
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QHBoxLayout, QMessageBox, QLabel, QComboBox, QTabWidget, QInputDialog
)
from PyQt5.QtCore import pyqtSignal
from db_utils import fetch_books, insert_book, update_book, delete_book, fetch_filtered_books, insert_loan, fetch_students, insert_student, update_student, delete_student, fetch_filtered_students
from faker import Faker
from db_utils import validate_uuid
import uuid
from uuid import UUID
from db_utils import get_student_uuid
from db_utils import convert_to_uuid
fake = Faker()

class LibraryManager(QWidget):
    data_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Manager")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()

        # Create the Book Manager tab
        self.book_manager = BookManager(self)
        self.tabs.addTab(self.book_manager, "Books")

        # Create the Student Manager tab
        self.student_manager = StudentManager(self)
        self.tabs.addTab(self.student_manager, "Students")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        self.setLayout(layout)

class BookManager(QWidget):
    data_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Library Book Manager")

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Title", "Author", "Copies Available", "Category", "Actions", "Borrow"])

        self.title_input = QLineEdit(self)
        self.author_input = QLineEdit(self)
        self.copies_input = QLineEdit(self)

        self.category_filter = QComboBox(self)
        self.category_filter.addItem("All Categories")
        self.category_filter.addItem("Science")
        self.category_filter.addItem("Fiction")
        self.category_filter.addItem("History")
        self.category_filter.addItem("Other")

        self.stock_filter = QComboBox(self)
        self.stock_filter.addItem("All")
        self.stock_filter.addItem("In Stock")
        self.stock_filter.addItem("Out of Stock")

        self.add_button = QPushButton("Add Book")
        self.update_button = QPushButton("Update Book List")
        self.delete_button = QPushButton("Delete Selected Book")

        self.add_button.clicked.connect(self.add_book)
        self.update_button.clicked.connect(self.load_data)
        self.delete_button.clicked.connect(self.delete_book)

        self.category_filter.currentIndexChanged.connect(self.filter_books)
        self.stock_filter.currentIndexChanged.connect(self.filter_books)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Author:"))
        layout.addWidget(self.author_input)
        layout.addWidget(QLabel("Copies Available:"))
        layout.addWidget(self.copies_input)
        layout.addWidget(self.add_button)
        layout.addWidget(QLabel("Category Filter:"))
        layout.addWidget(self.category_filter)
        layout.addWidget(QLabel("Stock Filter:"))
        layout.addWidget(self.stock_filter)
        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.data_updated.connect(self.load_data)
        self.load_data()

    def load_data(self):
        books = fetch_books()
        self.table.setRowCount(0)

        for row, book in enumerate(books):
            self.table.insertRow(row)
            for col, data in enumerate(book[:] ):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(self.create_edit_callback(row, book[0]))
            self.table.setCellWidget(row, 4, edit_button)

            borrow_button = QPushButton("Borrow")
            borrow_button.clicked.connect(self.create_borrow_callback(book[0]))
            self.table.setCellWidget(row, 5, borrow_button)

    def create_edit_callback(self, row, book_id):
        return lambda: self.edit_book(row, book_id)

    def create_borrow_callback(self, book_id):
        return lambda: self.borrow_book(book_id)

    def edit_book(self, row, book_id):
        """ویرایش اطلاعات کتاب انتخاب‌شده"""
        title_item = self.table.item(row, 0)
        author_item = self.table.item(row, 1)
        year_item = self.table.item(row, 2)
        genre_item = self.table.item(row, 3)
        
        if not all([title_item, author_item, year_item, genre_item]):
            QMessageBox.warning(self, "Error", "Some cells are missing data.")
            return

        title = title_item.text().strip()
        author = author_item.text().strip()
        year = year_item.text().strip()
        genre = genre_item.text().strip()

        if title and author and year and genre:
            try:
                # تبدیل book_id به UUID
                book_id = convert_to_uuid(book_id)  # تبدیل رشته book_id به UUID
                
                # به روز رسانی کتاب با استفاده از UUID
                update_book(book_id, title, author, int(year), genre)
                self.data_updated.emit()
                QMessageBox.information(self, "Success", "Book updated successfully!")
            except ValueError as ve:
                # در صورت بروز خطا در تبدیل UUID
                QMessageBox.critical(self, "UUID Error", f"Invalid UUID for book_id: {ve}")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        else:
            QMessageBox.warning(self, "Input Error", "Please ensure all fields are filled in correctly.")


    def update_book(book_id, new_title, new_author, new_copies, new_category):
        """به‌روزرسانی اطلاعات کتاب"""
        try:
            # فرض می‌کنیم که book_id یک UUID است
            # تبدیل book_id به رشته و انجام تغییرات روی آن
            book_id_str = str(book_id)  # تبدیل به رشته
            modified_book_id_str = book_id_str.replace("-", "")  # انجام تغییر (مثلاً حذف خط تیره‌ها)
            
            # تبدیل دوباره به UUID
            modified_book_id = uuid.UUID(modified_book_id_str)
            
            # حالا از modified_book_id برای انجام عملیات پایگاه داده استفاده می‌کنیم
            query = """
                UPDATE Books
                SET title = %s, author = %s, copies_available = %s, category = %s
                WHERE book_id = %s
            """
            params = (new_title, new_author, new_copies, new_category, modified_book_id)
            execute_query(query, params)
            
        except ValueError as e:
            print(f"Error: {e}")
            
    def borrow_book(self, book_id):
        current_row = self.table.currentRow()
        copies_available_item = self.table.item(current_row, 2)
        copies_available = int(copies_available_item.text())

        if copies_available > 0:
            student_name = self.get_student_name()
            if student_name is None:
                return 

            borrow_date = datetime.date.today()
            due_date = borrow_date + datetime.timedelta(days=14)

            try:
                student_id = get_student_uuid(student_name)
                insert_loan(book_id, student_id, borrow_date, due_date)
                new_copies = copies_available - 1
                update_book(book_id, new_copies)
                QMessageBox.information(self, "Success", f"Book borrowed successfully! Return by {due_date}.")
                self.data_updated.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        else:
            QMessageBox.warning(self, "Out of Stock", "This book is currently out of stock.")

    def get_student_name(self):
        student_name, ok = QInputDialog.getText(self, "Enter Student Name", "Please enter the student's name:")
        if ok and student_name.strip():
            return student_name.strip()
        else:
            QMessageBox.warning(self, "Input Error", "Student name cannot be empty.")
            return None

    def add_book(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        copies = self.copies_input.text().strip()
        category = self.category_filter.currentText()

        isbn = fake.isbn13()

        if title and author and copies.isdigit() and int(copies) > 0:
            insert_book(title, author, isbn, int(copies), category)
            self.data_updated.emit()
            QMessageBox.information(self, "Success", "Book added successfully!")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter valid data.")

    def delete_book(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            title = self.table.item(current_row, 0).text()
            delete_book(title)
            self.data_updated.emit()
            QMessageBox.information(self, "Success", "Book deleted successfully!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a book to delete.")

    def filter_books(self):
        category = self.category_filter.currentText()
        stock_status = self.stock_filter.currentText()

        query = "SELECT title, author, copies_available, category FROM Books WHERE 1=1"
        
        if category != "All Categories":
            query += f" AND category = '{category}'"
        
        if stock_status == "In Stock":
            query += " AND copies_available > 0"
        elif stock_status == "Out of Stock":
            query += " AND copies_available = 0"
        
        books = fetch_filtered_books(query)
        self.load_filtered_data(books)

    def load_filtered_data(self, books):
        self.table.setRowCount(0)

        for row, book in enumerate(books):
            self.table.insertRow(row)
            for col, data in enumerate(book[:] ):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, b_id=book['book_id']: self.edit_book(row_index, b_id))
            self.table.setCellWidget(row, 4, edit_button)

            borrow_button = QPushButton("Borrow")
            borrow_button.clicked.connect(lambda checked, book_id=book[0]: self.borrow_book(book_id))
            self.table.setCellWidget(row, 5, borrow_button)

class StudentManager(QWidget):
    data_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Student Manager")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Email", "Phone", "Department", "Actions"])

        self.name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.phone_input = QLineEdit(self)
        self.department_input = QLineEdit(self)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search by name, or department")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_students)

        self.add_button = QPushButton("Add Student")
        self.update_button = QPushButton("Update Student List")
        self.delete_button = QPushButton("Delete Selected Student")

        self.add_button.clicked.connect(self.add_student)
        self.update_button.clicked.connect(self.load_data)
        self.delete_button.clicked.connect(self.delete_student)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Phone:"))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel("Department:"))
        layout.addWidget(self.department_input)
        layout.addWidget(self.add_button)

        layout.addWidget(QLabel("Search:"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)

        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.data_updated.connect(self.load_data)

        self.load_data()

    def load_data(self):
        students = fetch_students()
        self.table.setRowCount(0)

        for row, student in enumerate(students):
            self.table.insertRow(row)
            for col, data in enumerate(student[1:]):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, r=row, student_id=student[0]: self.edit_student(r, student_id))
            self.table.setCellWidget(row, 4, edit_button)

    def add_student(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        department = self.department_input.text().strip()

        if name and email and phone and department:
            insert_student(name, email, phone, department)
            self.data_updated.emit()
            QMessageBox.information(self, "Success", "Student added successfully!")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter valid data.")

    def edit_student(self, row, student_id):
        """ویرایش اطلاعات دانشجوی انتخاب‌شده"""
        name_item = self.table.item(row, 0)
        email_item = self.table.item(row, 1)
        phone_item = self.table.item(row, 2)
        department_item = self.table.item(row, 3)
        
        if not all([name_item, email_item, phone_item, department_item]):
            QMessageBox.warning(self, "Error", "Some cells are missing data.")
            return

        name = name_item.text().strip()
        email = email_item.text().strip()
        phone = phone_item.text().strip()
        department = department_item.text().strip()

        if name and email and phone and department:
            try:
                update_student(student_id, name, email, phone, department)
                self.data_updated.emit()
                QMessageBox.information(self, "Success", "Student updated successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        else:
            QMessageBox.warning(self, "Input Error", "Please ensure all fields are filled in correctly.")


    def delete_student(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            student_name = self.table.item(current_row, 0).text()
            delete_student(student_name)
            self.data_updated.emit()
            QMessageBox.information(self, "Success", "Student deleted successfully!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a student to delete.")

    def search_students(self):
        query = self.search_input.text().strip()
        students = fetch_filtered_students(query)
        self.table.setRowCount(0)
        for row, student in enumerate(students):
            self.table.insertRow(row)
            for col, data in enumerate(student[1:]):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))


def main():
    app = QApplication(sys.argv)
    window = LibraryManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()