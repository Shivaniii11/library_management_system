import mysql.connector
from datetime import datetime 

# Connect to the database
db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='1111',
    database='week05'
)
mycursor = db.cursor(buffered=True)

# --- Create Tables ---
# Each statement must be executed separately
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS books1 (
        book_id INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(100) NOT NULL,
        author VARCHAR(100) NOT NULL,
        category VARCHAR(100),
        total_copies INT CHECK(total_copies >= 0),
        available_copies INT CHECK(available_copies >= 0)
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS members1 (
        member_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        join_date DATE NOT NULL,
        status VARCHAR(100) CHECK(status IN ('active', 'inactive')) NOT NULL
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS book_issues1 (
        issue_id INT PRIMARY KEY AUTO_INCREMENT,
        book_id INT,
        member_id INT,
        issue_date DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        FOREIGN KEY (book_id) REFERENCES books1(book_id),
        FOREIGN KEY (member_id) REFERENCES members1(member_id)
    )
""")

db.commit()

# --- Insert Book ---

def  add_book():
    title = input("Enter book title: ")
    author = input("Enter author name: ")
    category = input("Enter book category: ")
    total_copies = int(input("Enter total copies of the book: "))

# Insert into correct table and use only %s
    mycursor.execute(
        "INSERT INTO books1 (title, author, category, total_copies, available_copies) VALUES (%s, %s, %s, %s, %s)",
        (title, author, category, total_copies, total_copies)
    )

    db.commit()
    print("Book inserted successfully.")
    

def update_book():
    book_id = int(input("Book ID to update: "))
    new_total = int(input("New total copies: "))
    mycursor.execute("SELECT total_copies, available_copies FROM books1 WHERE book_id = %s", (book_id,))
    data = mycursor.fetchone()
    if not data:
        print("Book not found.")
        return
    total_copies, available_copies = data
    diff = new_total - total_copies
    new_available = available_copies + diff
    if new_available < 0:
        print("Not enough available copies to reduce.")
        return
    mycursor.execute(
        "UPDATE books1 SET total_copies = %s, available_copies = %s WHERE book_id = %s",
        (new_total, new_available, book_id)
    )
    db.commit()
    print("Book updated.")


def delete_book():
    book_id = int(input("Book ID to delete: "))

    # Check if the book is currently issued and not yet returned
    mycursor.execute(
        "SELECT COUNT(*) FROM book_issues1 WHERE book_id = %s AND return_date IS NULL",(book_id,))
    if mycursor.fetchone()[0] > 0:
        print("Cannot delete. Book is currently issued.")
        return

    # Delete the book
    mycursor.execute(
        "DELETE FROM books1 WHERE book_id = %s",
        (book_id,)
    )
    db.commit()
    print("Book deleted.")


# --- Insert Member ---
def add_member():
    name = input("Enter name: ")
    email = input("Enter email: ")
    join_date = input("Enter joining date (YYYY-MM-DD): ")
    status = input("Enter status (active/inactive): ")

    mycursor.execute(
        "INSERT INTO members1 (name, email, join_date, status) VALUES (%s, %s, %s, %s)",
        (name, email, join_date, status)
    )

    db.commit()
    print("Member added successfully.")

def delete_member():
    member_id = int(input("Member ID to delete: "))
    mycursor.execute("SELECT COUNT(*) FROM book_issues1 WHERE member_id =%s  AND return_date IS NULL", (member_id,))
    if mycursor.fetchone()[0] > 0:
        print("Member has borrowed books.")
        return
    mycursor.execute("DELETE FROM members1 WHERE member_id =%s ", (member_id,))
    db.commit()
    print("Member deleted.")

def issue_book():
    member_id = int(input("Enter Member ID: "))
    book_id = int(input("Enter Book ID: "))

    # Check if book exists and has available copies
    mycursor.execute("SELECT available_copies FROM books1 WHERE book_id = %s", (book_id,))
    result = mycursor.fetchone()
    if not result:
        print("Book not found.")
        return
    if result[0] <= 0:
        print("No available copies.")
        return

    issue_date = input("Enter issue date (YYYY-MM-DD): ")
    due_date = input("Enter due date (YYYY-MM-DD): ")

    mycursor.execute("""
        INSERT INTO book_issues1 (book_id, member_id, issue_date, due_date)
        VALUES (%s, %s, %s, %s)
    """, (book_id, member_id, issue_date, due_date))

    mycursor.execute("UPDATE books1 SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))
    db.commit()
    print("Book issued successfully.")


 # Ensure this is at the top of your file

def return_book():
    issue_id = int(input("Issue ID: "))

    # Check if the book has already been returned or the issue ID is invalid
    mycursor.execute(
        "SELECT book_id FROM book_issues1 WHERE issue_id = %s AND return_date IS NULL",
        (issue_id,)
    )
    data = mycursor.fetchone()

    if not data:
        print(" Already returned or invalid ID.")
        return

    book_id = data[0]
    return_date = datetime.today().date()

    # Update return_date in book_issues1
    mycursor.execute(
        "UPDATE book_issues1 SET return_date = %s WHERE issue_id = %s",
        (return_date, issue_id)
    )

    # Increment the available copies of the book
    mycursor.execute(
        "UPDATE books1 SET available_copies = available_copies + 1 WHERE book_id = %s",
        (book_id,)
    )

    db.commit()
    print("Book returned successfully on", return_date)


def available_books():
    mycursor.execute("SELECT SUM(available_copies) FROM books1")
    total = mycursor.fetchone()[0]
    total = total if total is not None else 0
    print(f"Total Available Books: {total}")


def borrowed_books():
    mycursor.execute("""
        SELECT m.name, b.title, i.issue_date, i.due_date
        FROM book_issues1 i
        JOIN members1 m ON i.member_id = m.member_id
        JOIN books1 b ON i.book_id = b.book_id
        WHERE i.return_date IS NULL
    """)
    rows = mycursor.fetchall()
    if not rows:
        print("No books are currently borrowed.")
    else:
        for row in rows:
            print(f" {row[0]} borrowed '{row[1]}' on {row[2]} (Due: {row[3]})")


def overdue_books():
    mycursor.execute("""
        SELECT m.name, b.title, i.due_date
        FROM book_issues1 i
        JOIN members1 m ON i.member_id = m.member_id
        JOIN books1 b ON i.book_id = b.book_id
        WHERE i.return_date IS NULL AND i.due_date < CURDATE()
    """)
    rows = mycursor.fetchall()
    if not rows:
        print("No overdue books.")
    else:
        for row in rows:
            print(f" Overdue: {row[0]} - '{row[1]}' (Due: {row[2]})")


def top_books():
    mycursor.execute("""
        SELECT b.title, COUNT(*) as count
        FROM book_issues1 i
        JOIN books1 b ON b.book_id = i.book_id
        GROUP BY b.title
        ORDER BY count DESC
        LIMIT 5
    """)
    rows = mycursor.fetchall()
    if not rows:
        print("No books have been borrowed yet.")
    else:
        for row in rows:
            print(f"{row[0]} - Borrowed {row[1]} times")
def view_books():
    mycursor.execute("SELECT book_id, title, author, category, total_copies, available_copies FROM books1")
    rows = mycursor.fetchall()
    if not rows:
        print("No books found in the library.")
    else:
        print("\n List of All Books:")
        for book in rows:
            print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} | Category: {book[3]} | Total: {book[4]} | Available: {book[5]}")

def view_issue_books():
    mycursor.execute("SELECT issue_id, book_id, member_id, issue_date, due_date, return_date FROM book_issues1")
    row1= mycursor.fetchall()
    if not row1:
         print("📚 No books are issued.")
    else:
        print("\n List of All issued Books:")
        for book in row1:
            print(f'issue_ID: {book[0]} |book_id: {book[1]} | member_id: {book[2]} | issue_date: {book[3]} | due_date: {book[4]} | return_date: {book[5]}')

def view_member():
    mycursor.execute("SELECT member_id, name, email, join_date, status FROM members1")
    row2= mycursor.fetchall()
    if not row2:
         print("📚 No members available.")
    else:
        print("\n List of All members:")
        for book in row2:
            print(f'Member_ID: {book[0]} |name: {book[1]} | email: {book[2]} | join_date: {book[3]} | status: {book[4]}')
    
def bottom_books():
    mycursor.execute("""
        SELECT b.title, COUNT(i.issue_id) AS borrow_count
        FROM books1 b
        LEFT JOIN book_issues1 i ON b.book_id = i.book_id
        GROUP BY b.book_id, b.title
        ORDER BY borrow_count ASC
        LIMIT 5
    """)
    rows = mycursor.fetchall()
    if not rows:
        print("No books found.")
    else:
        print("\n Least Borrowed Books:")
       
        for row in rows:
            print(f"{row[0]} - Borrowed {row[1]} times")

def member_history():
    member_id = int(input("Enter Member ID to view history: "))

    # Check if member exists
    mycursor.execute("SELECT name FROM members1 WHERE member_id = %s", (member_id,))
    member = mycursor.fetchone()
    if not member:
        print("Member not found.")
        return

    member_name = member[0]

    # Fetch all issued book history for this member
    mycursor.execute("""
        SELECT b.title, i.issue_date, i.due_date, i.return_date
        FROM book_issues1 i
        JOIN books1 b ON i.book_id = b.book_id
        WHERE i.member_id = %s
        ORDER BY i.issue_date DESC
    """, (member_id,))
    
    records = mycursor.fetchall()

    if not records:
        print(f"No books issued by {member_name}.")
        return

    print(f"\nIssue History for Member: {member_name} (ID: {member_id})")
    count_total = 0
    count_active = 0
    for title, issue_date, due_date, return_date in records:
        count_total += 1
        if return_date is None:
            count_active += 1
            status = "Not Returned"
        else:
            status = f"Returned on {return_date}"

        print(f"{title} | Issued: {issue_date} | Due: {due_date} | {status}")

    print(f"Total Books Issued: {count_total}")
    print(f"Currently Borrowed: {count_active}")
    print(f"Returned Books: {count_total - count_active}")


def menu():
    while True:
        print("\n======  Library System ======")
        print("1. Add Book")
        print("2. Update Book Quantity")
        print("3. Delete Book")
        print("4. Add Member")
        print("5. Delete Member")
        print("6. Issue Book")
        print("7. Return Book")
        print("8. Show Available Books")
        print("9. Show Borrowed Books")
        print("10. Show Overdue Books")
        print("11. Top 5 Most Borrowed Books")
        print("12. view  Books")
        print("13. view issued Books")
        print("14. view member")
        print("15. least borrowed books")
        print("16. view member history")
        print("0. Exit")
        choice = input("Choose option: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            update_book()
        elif choice == "3":
            delete_book()
        elif choice == "4":
            add_member()
        elif choice == "5":
            delete_member()
        elif choice == "6":
            issue_book()
        elif choice == "7":
            return_book()
        elif choice == "8":
            available_books()
        elif choice == "9":
            borrowed_books()
        elif choice == "10":
            overdue_books()
        elif choice == "11":
            top_books()
        elif choice == "12":
            view_books()
        elif choice == "13":
            view_issue_books()
        elif choice == "14":
            view_member()
        elif choice == "15":
            bottom_books()
        elif choice == "16":
            member_history()
        elif choice == "0":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

# ----------------------------
# Run the Menu
# ----------------------------
if __name__ == "__main__":
    menu()
    db.close()