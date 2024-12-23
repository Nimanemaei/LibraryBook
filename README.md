# LibraryBook Management System

## Overview
The LibraryBook Management System is a comprehensive library database project designed to manage books, students, loans, and fines. It supports essential functionalities such as book borrowing, tracking overdue loans, calculating fines, and generating reports.


---
## Screenshots

### 1. Books Management
![Books Management](D:\myproject\assets\screenshots\book-management.png)

### 2. Students Management
![Students Management](D:\myproject\assets\screenshots\student-management.png)

---

## Features

### Book Management
- **Add, Edit, Delete Books**: Manage book records with details such as title, author, ISBN, category, and available copies.
- **Top Borrowed Books**: Retrieve the 5 most borrowed books in each category.

### Student Management
- **Student Records**: Maintain student details, including name, email, phone, and department.
- **Overdue Notifications**: List students with overdue books.

### Loan Management
- **Borrow and Return Books**: Record when students borrow and return books.
- **Overdue Tracking**: Identify overdue loans and calculate fines automatically.

### Fine Management
- **Unpaid Fines**: Calculate total unpaid fines for a student.
- **Fine Payments**: Record payments and update fine statuses.

### Reporting
- **Borrowing History**: View borrowing and returning activities for the last 30 days.
- **Category Insights**: Analyze borrowing trends by category.

---

## Database Structure

### Tables

#### Books
| Column           | Type     | Description                                      |
|------------------|----------|--------------------------------------------------|
| book_id          | UUID     | Unique identifier for each book.                |
| title            | VARCHAR  | Title of the book.                              |
| author           | VARCHAR  | Author of the book.                             |
| isbn             | VARCHAR  | Unique ISBN for the book.                       |
| copies_available | INTEGER  | Number of copies available for borrowing.       |
| category         | VARCHAR  | Category of the book (e.g., Science, Fiction).  |

#### Students
| Column     | Type     | Description                                      |
|------------|----------|--------------------------------------------------|
| student_id | UUID     | Unique identifier for each student.             |
| name       | VARCHAR  | Name of the student.                            |
| email      | VARCHAR  | Email of the student.                           |
| phone      | VARCHAR  | Phone number of the student.                    |
| department | VARCHAR  | Department of the student.                      |

#### Loans
| Column        | Type     | Description                                      |
|---------------|----------|--------------------------------------------------|
| loan_id       | UUID     | Unique identifier for each loan record.         |
| book_id       | UUID     | Foreign key referencing Books table.            |
| student_id    | UUID     | Foreign key referencing Students table.         |
| date_borrowed | DATE     | Date when the book was borrowed.                |
| due_date      | DATE     | Due date for returning the book.                |
| return_date   | DATE     | Date when the book was returned.                |

#### Fines
| Column   | Type     | Description                                      |
|----------|----------|--------------------------------------------------|
| fine_id  | UUID     | Unique identifier for each fine record.         |
| loan_id  | UUID     | Foreign key referencing Loans table.            |
| amount   | DECIMAL  | Fine amount for overdue books.                  |
| paid     | BOOLEAN  | Status indicating if the fine has been paid.    |

---

## Example SQL Queries

### 1. Top 5 Borrowed Books in Each Category
```sql
WITH BookLoanCounts AS (
    SELECT
        b.book_id,
        b.category,
        COUNT(l.loan_id) AS loan_count
    FROM
        Books b
    LEFT JOIN Loans l ON b.book_id = l.book_id
    GROUP BY
        b.book_id, b.category
)
SELECT
    bl.category,
    b.title,
    b.author,
    bl.loan_count
FROM
    BookLoanCounts bl
JOIN Books b ON bl.book_id = b.book_id
WHERE
    bl.loan_count > 0
ORDER BY
    bl.category, bl.loan_count DESC
LIMIT 5;
```

### 2. Students with Overdue Books
```sql
SELECT
    s.name,
    s.email,
    COUNT(l.loan_id) AS overdue_books
FROM
    Students s
JOIN Loans l ON s.student_id = l.student_id
WHERE
    l.due_date < CURRENT_DATE
    AND l.return_date IS NULL
GROUP BY
    s.student_id
HAVING
    COUNT(l.loan_id) > 0;
```

### 3. Total Unpaid Fines for a Student
```sql
SELECT
    s.name,
    s.email,
    SUM(f.amount) AS total_unpaid_fines
FROM
    Students s
JOIN Loans l ON s.student_id = l.student_id
JOIN Fines f ON l.loan_id = f.loan_id
WHERE
    f.paid = FALSE
GROUP BY
    s.student_id
HAVING
    SUM(f.amount) > 0;
```

### 4. Borrowing and Returning History in the Last 30 Days
```sql
SELECT
    b.title,
    b.author,
    l.date_borrowed,
    l.return_date
FROM
    Loans l
JOIN Books b ON l.book_id = b.book_id
WHERE
    l.return_date IS NOT NULL
    AND l.return_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY
    l.return_date DESC;
```

---

## Installation
1. Clone the repository.
   ```bash
   git clone https://github.com/Nimanemaei/LibraryBook.git
   ```
2. Set up the PostgreSQL database.
3. Execute the SQL scripts to create tables and populate initial data.
4. Configure the application.

---

## Future Enhancements
- **Real-Time Notifications**: Notify students about overdue books and fines.
- **Advanced Reporting**: Include visual dashboards for insights.
- **Role-Based Access Control**: Differentiate permissions for librarians and students.
- **Mobile App**: Develop a mobile-friendly interface.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributors
- [NimaNemaei] - Project Owner & Developer

For any questions or suggestions, feel free to contact us at [nimanemaee6655@gmail.com].

