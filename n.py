import psycopg2

def clear_tables():
    try:
        connection = psycopg2.connect(
            dbname="library_db",  
            user="postgres",     
            password="2275483n", 
            host="localhost",    
        )
        cursor = connection.cursor()

        # Delete data from tables
        cursor.execute("DELETE FROM Fines;")
        cursor.execute("DELETE FROM Loans;")
        cursor.execute("DELETE FROM Books;")
        cursor.execute("DELETE FROM Students;")

        connection.commit()
        print("All data has been cleared from the tables.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    clear_tables()






 

