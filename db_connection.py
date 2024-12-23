import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget
from PyQt5.QtCore import Qt
import psycopg2

def create_connection():
    try:
        connection = psycopg2.connect(
            dbname="library_db",  
            user="postgres",     
            password="2275483n", 
            host="localhost",    
            port="5432"           
        )
        return connection
    except Exception as e:
        print(f"Error: {e}")
        return None

class LibraryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Welcome to the Library System", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.book_list = QListWidget(self)
        layout.addWidget(self.book_list)

        self.load_books_button = QPushButton("Load Books", self)
        self.load_books_button.clicked.connect(self.load_books)
        layout.addWidget(self.load_books_button)

        self.setLayout(layout)

    def load_books(self):
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT title, author FROM Books")
            books = cursor.fetchall()
            self.book_list.clear()
            for book in books:
                self.book_list.addItem(f"{book[0]} by {book[1]}")
            cursor.close()
            connection.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryApp()
    window.show()
    sys.exit(app.exec_())
