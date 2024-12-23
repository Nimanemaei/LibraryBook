import psycopg2
from faker import Faker
import uuid
import random

# ایجاد اتصال به دیتابیس
def create_connection():
    return psycopg2.connect(
        dbname="library_db",
        user="postgres",  # نام کاربری خود را وارد کنید
        password="2275483n",  # رمز عبور خود را وارد کنید
        host="localhost",
        port="5432"
    )

fake = Faker()

def generate_students(n=100):
    students = []
    for _ in range(n):
        students.append((
            str(uuid.uuid4()),
            fake.name(),
            fake.email(),
            fake.phone_number()[:15],  # محدود کردن طول به 15 کاراکتر
            random.choice(['Computer Science', 'Mathematics', 'Physics', 'History', 'Literature'])
        ))
    return students

def generate_books(n=50):
    categories = ['Science', 'Fiction', 'History', 'Technology', 'Other']
    books = []
    for _ in range(n):
        books.append((
            str(uuid.uuid4()),
            fake.sentence(nb_words=3),
            fake.name(),
            fake.isbn13(),
            random.randint(0, 5),  # تعداد نسخه‌های موجود بین 0 تا 5
            random.choice(categories)
        ))
    return books

def insert_data():
    connection = create_connection()
    cursor = connection.cursor()

    # درج داده‌های دانشجو
    students = generate_students()
    cursor.executemany("""
        INSERT INTO Students (student_id, name, email, phone, department)
        VALUES (%s, %s, %s, %s, %s)
    """, students)

    # درج داده‌های کتاب
    books = generate_books()
    cursor.executemany("""
        INSERT INTO Books (book_id, title, author, isbn, copies_available, category)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, books)

    connection.commit()
    cursor.close()
    connection.close()
    print("Sample data inserted successfully!")

if __name__ == "__main__":
    insert_data()
