import psycopg2
import uuid
import datetime
from contextlib import contextmanager
import hashlib

@contextmanager
def create_connection():
    """Create a connection to the PostgreSQL database using context manager."""
    connection = None
    try:
        connection = psycopg2.connect(
            dbname="library_db",
            user="postgres",  # Replace with your username
            password="2275483n",  # Replace with your password
            host="localhost",
            port="5432"
        )
        yield connection
    except psycopg2.Error as e:
        print(f"Error creating connection: {e}")
    finally:
        if connection:
            connection.close()

def execute_query(query, params=None):
    """Execute any query using a connection to the database."""
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                connection.commit()
    except psycopg2.DatabaseError as e:
        print(f"Error executing query: {e}")

def convert_to_uuid(book_id):
    """تبدیل یک رشته به UUID با استفاده از هش کردن آن"""
    # هش کردن رشته
    hashed = hashlib.sha1(book_id.encode()).hexdigest()
    
    # ایجاد UUID از هش شده (توجه کنید که این فقط 16 بایت اول از هش SHA1 را استفاده می‌کند)
    return uuid.UUID(hashed[:32])  # فقط 32 کاراکتر اول هش برای ساخت UUID کافی است

def fetch_books():
    """Retrieve the list of books from the database."""
    query = "SELECT title, author, copies_available, category FROM Books"
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                books = cursor.fetchall()
        return books
    except psycopg2.DatabaseError as e:
        print(f"Error fetching books: {e}")
        return []

def fetch_books_paginated(page, page_size=5):
    """بازیابی داده‌های کتاب‌ها با صفحه‌بندی"""
    connection = create_connection()
    cursor = connection.cursor()
    offset = (page - 1) * page_size
    cursor.execute("""
        SELECT title, author, copies_available FROM Books
        LIMIT %s OFFSET %s
    """, (page_size, offset))
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return books

def fetch_students_paginated(page, page_size=5):
    """بازیابی داده‌های دانشجویان با صفحه‌بندی"""
    connection = create_connection()
    cursor = connection.cursor()
    offset = (page - 1) * page_size
    cursor.execute("""
        SELECT name, email, phone FROM Students
        LIMIT %s OFFSET %s
    """, (page_size, offset))
    students = cursor.fetchall()
    cursor.close()
    connection.close()
    return students


def validate_uuid(book_id):
    try:
        # تلاش برای تبدیل book_id به UUID
        uuid_obj = uuid.UUID(book_id, version=4)
        return True
    except ValueError:
        # در صورتی که UUID نامعتبر باشد، خطا را می‌گیرد
        return False
    
def insert_book(title, author, isbn, copies, category='Other'):
    """Insert a new book into the database."""
    query = """
        INSERT INTO Books (book_id, title, author, isbn, copies_available, category)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (str(uuid.uuid4()), title, author, isbn, copies, category)
    execute_query(query, params)

def insert_loan(book_id, student_name, borrow_date, due_date):
    try:
        conn = psycopg2.connect(dbname="library_db", user="postgres", password="2275483n", host="localhost")
        cursor = conn.cursor()

        # پیدا کردن student_id بر اساس student_name
        cursor.execute("SELECT student_id FROM Students WHERE name = %s", (student_name,))
        result = cursor.fetchone()

        if result:
            student_id = result[0]

            # تبدیل book_id و student_id به UUID
            try:
                book_id = uuid.UUID(book_id)
                student_id = uuid.UUID(student_id)
            except ValueError:
                print("Invalid book ID or student ID format. Please provide valid UUIDs.")
                return

            # درج اطلاعات امانت در جدول Loans
            cursor.execute(
                "INSERT INTO Loans (book_id, student_id, date_borrowed, due_date) VALUES (%s, %s, %s, %s)",
                (book_id, student_id, borrow_date, due_date)
            )

            conn.commit()
            print("Loan inserted successfully.")
        else:
            print("Student not found.")

    except Exception as e:
        print(f"Error inserting loan: {e}")

    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

def update_book(book_id, new_title, new_author, new_copies, new_category):
    # اعتبارسنجی UUID قبل از انجام عملیات
    if not validate_uuid(book_id):
        raise ValueError("Invalid UUID for book_id")
    
    query = "UPDATE Books SET title = %s, author = %s, copies_available = %s, category = %s WHERE book_id = %s"
    params = (new_title, new_author, new_copies, new_category, book_id)
    execute_query(query, params)


def update_book_inventory(book_title, new_inventory):
    """Update the inventory of a book based on its title."""
    query = """
        UPDATE Books
        SET copies_available = %s
        WHERE title = %s
    """
    params = (new_inventory, book_title)
    execute_query(query, params)

def delete_book(title):
    """Delete a book from the database based on its title."""
    query = "DELETE FROM Books WHERE title = %s"
    params = (title,)
    execute_query(query, params)

def fetch_filtered_books(query):
    """Retrieve books based on the provided query."""
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                filtered_books = cursor.fetchall()
        return filtered_books
    except psycopg2.DatabaseError as e:
        print(f"Error fetching filtered books: {e}")
        return []

def get_student_uuid(student_name):
    # فرض می‌کنیم که از نام دانش‌آموز UUID ایجاد می‌کنیم
    try:
        student_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, student_name)
        return student_uuid
    except ValueError:
        raise ValueError("Invalid student ID format. Please provide a valid student name.")
    
def fetch_students():
    """Retrieve the list of students from the database."""
    query = "SELECT student_id, name, email, phone, department FROM Students"
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                students = cursor.fetchall()
        return students
    except psycopg2.DatabaseError as e:
        print(f"Error fetching students: {e}")
        return []

def insert_student(name, email, phone, department):
    """Insert a new student into the database."""
    query = """
        INSERT INTO Students (student_id, name, email, phone, department)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (str(uuid.uuid4()), name, email, phone, department)
    execute_query(query, params)

def update_student(student_id, name, email, phone, department):
    """Update student information in the database."""
    query = """
        UPDATE Students
        SET name = %s, email = %s, phone = %s, department = %s
        WHERE student_id = %s
    """
    params = (name, email, phone, department, student_id)
    execute_query(query, params)

def delete_student(name):
    """Delete a student from the database based on their name."""
    query = "DELETE FROM Students WHERE name = %s"
    params = (name,)
    execute_query(query, params)

def fetch_filtered_students(query):
    """Retrieve students based on name or department."""
    sql_query = """
        SELECT student_id, name, email, phone, department
        FROM Students
        WHERE name ILIKE %s OR department ILIKE %s
    """
    params = (f"%{query}%", f"%{query}%")
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                students = cursor.fetchall()
        return students
    except psycopg2.DatabaseError as e:
        print(f"Error fetching filtered students: {e}")
        return []

def check_book_availability(title):
    """Check if a book is available based on its title."""
    query = "SELECT copies_available FROM Books WHERE title = %s"
    params = (title,)
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result and result[0] > 0
    except psycopg2.DatabaseError as e:
        print(f"Error checking book availability: {e}")
        return False

def lend_book(book_title, student_name):
    """Lend a book to a student."""
    if not check_book_availability(book_title):
        return False, "Book is not available."

    return_date = datetime.date.today() + datetime.timedelta(days=14)

    query_book = "SELECT book_id FROM Books WHERE title = %s"
    params_book = (book_title,)
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_book, params_book)
                book_result = cursor.fetchone()
                if not book_result:
                    return False, "Book not found."
                book_id = book_result[0]

                query_student = "SELECT student_id FROM Students WHERE name = %s"
                params_student = (student_name,)
                cursor.execute(query_student, params_student)
                student_result = cursor.fetchone()
                if not student_result:
                    return False, "Student not found."
                student_id = student_result[0]

                borrow_id = str(uuid.uuid4())
                query_borrow = """
                    INSERT INTO Borrows (borrow_id, book_id, student_id, borrow_date, return_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                params_borrow = (borrow_id, book_id, student_id, datetime.date.today(), return_date)

                query_update_book = """
                    UPDATE Books
                    SET copies_available = copies_available - 1
                    WHERE book_id = %s
                """
                params_update_book = (book_id,)

                cursor.execute(query_borrow, params_borrow)
                cursor.execute(query_update_book, params_update_book)
                connection.commit()

                return True, f"Book lent successfully! Return by {return_date}."
    except psycopg2.DatabaseError as e:
        print(f"Error lending book: {e}")
        return False, f"An error occurred: {e}"

def return_book(book_title, student_name):
    """Return a book and calculate the fine if delayed."""
    query_book = "SELECT book_id FROM Books WHERE title = %s"
    params_book = (book_title,)
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_book, params_book)
                book_result = cursor.fetchone()
                if not book_result:
                    return False, "Book not found."
                book_id = book_result[0]

                query_student = "SELECT student_id FROM Students WHERE name = %s"
                params_student = (student_name,)
                cursor.execute(query_student, params_student)
                student_result = cursor.fetchone()
                if not student_result:
                    return False, "Student not found."
                student_id = student_result[0]

                query_borrow = "SELECT borrow_date, return_date FROM Borrows WHERE book_id = %s AND student_id = %s AND actual_return_date IS NULL"
                params_borrow = (book_id, student_id)
                cursor.execute(query_borrow, params_borrow)
                borrow_result = cursor.fetchone()
                if not borrow_result:
                    return False, "No active borrow record found."

                borrow_date, return_date = borrow_result
                actual_return_date = datetime.date.today()

                fine = calculate_fine(return_date, actual_return_date)

                query_update_return = """
                    UPDATE Borrows
                    SET actual_return_date = %s, fine = %s
                    WHERE book_id = %s AND student_id = %s AND actual_return_date IS NULL
                """
                params_update_return = (actual_return_date, fine, book_id, student_id)

                query_update_book = """
                    UPDATE Books
                    SET copies_available = copies_available + 1
                    WHERE book_id = %s
                """
                params_update_book = (book_id,)

                cursor.execute(query_update_return, params_update_return)
                cursor.execute(query_update_book, params_update_book)
                connection.commit()

                return True, f"Book returned successfully! Fine: {fine}."
    except psycopg2.DatabaseError as e:
        print(f"Error returning book: {e}")
        return False, f"An error occurred: {e}"

def calculate_fine(return_date, actual_return_date):
    """Calculate fine based on the return dates."""
    if actual_return_date <= return_date:
        return 0
    delay_days = (actual_return_date - return_date).days
    fine_per_day = 100
    return delay_days * fine_per_day

def fetch_unpaid_fines():
    """Display a list of unpaid fines."""
    query = """
        SELECT student_id, book_id, fine
        FROM Borrows
        WHERE fine > 0 AND paid = FALSE
    """
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                fines = cursor.fetchall()
        return fines
    except psycopg2.DatabaseError as e:
        print(f"Error fetching unpaid fines: {e}")
        return []

def pay_fine(student_name, book_title):
    """Pay fine and update the fine payment status."""
    query_book = "SELECT book_id FROM Books WHERE title = %s"
    params_book = (book_title,)
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_book, params_book)
                book_result = cursor.fetchone()
                if not book_result:
                    return False, "Book not found."
                book_id = book_result[0]

                query_student = "SELECT student_id FROM Students WHERE name = %s"
                params_student = (student_name,)
                cursor.execute(query_student, params_student)
                student_result = cursor.fetchone()
                if not student_result:
                    return False, "Student not found."
                student_id = student_result[0]

                query_update_fine = """
                    UPDATE Borrows
                    SET paid = TRUE
                    WHERE student_id = %s AND book_id = %s AND paid = FALSE
                """
                params_update_fine = (student_id, book_id)

                cursor.execute(query_update_fine, params_update_fine)
                connection.commit()

                return True, "Fine paid successfully."
    except psycopg2.DatabaseError as e:
        print(f"Error paying fine: {e}")
        return False, f"An error occurred: {e}"

def insert_borrow(book_id, student_id, borrow_date, return_date):
    """ثبت اطلاعات امانت‌کتاب در دیتابیس"""
    borrow_id = str(uuid.uuid4())
    query = """
        INSERT INTO Borrows (borrow_id, book_id, student_id, borrow_date, return_date)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (borrow_id, book_id, student_id, borrow_date, return_date)
    execute_query(query, params)
