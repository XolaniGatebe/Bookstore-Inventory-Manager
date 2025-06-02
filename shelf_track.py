# shelf_track.py: Bookstore inventory management
# Manages ebookstore db with book/author tables

import sqlite3

def connect_db(db_name='ebookstore.db'):
    """Connect to ebookstore db, return conn, cursor.

    Args:
        db_name (str): Database file name.
    Returns:
        tuple: Connection, cursor objects.
    """
    # Establish database connection
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"DB connection error: {e}")
        raise

def create_tables():
    """Create book, author tables with foreign key."""
    conn, cursor = connect_db()
    # Set up author and book table
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS author (
                ID INTEGER PRIMARY KEY NOT NULL,
                Name TEXT,
                Country TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY NOT NULL,
                title TEXT,
                authorID INTEGER,
                quantity INTEGER,
                FOREIGN KEY (authorID) REFERENCES author(ID)
            )
        ''')
        conn.commit()
        print("Tables created or exist.\n")
    except sqlite3.Error as e:
        print(f"Table creation error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_initial_data():
    """Insert initial author and book records if not exist."""
    # Add default authors and books
    conn, cursor = connect_db()
    try:
        # Check and insert authors
        authors = [
            (1290, 'Charles Dickens', 'England'),
            (8937, 'J.K. Rowling', 'England'),
            (6380, 'J.R.R. Tolkien', 'South Africa'),
            (2356, 'C.S. Lewis', 'Ireland'),
            (5620, 'Lewis Carrol', 'England')
        ]
        cursor.execute('SELECT ID FROM author WHERE ID IN (?, ?, ?, ?, ?)',
                       [a[0] for a in authors])
        existing_ids = {row[0] for row in cursor.fetchall()}
        new_authors = [a for a in authors if a[0] not in existing_ids]
        if new_authors:
            cursor.executemany('''
                INSERT INTO author (ID, Name, Country)
                VALUES (?, ?, ?)
            ''', new_authors)

        # Check and insert books
        books = [
            (3001, 'A Tale Of Two Cities', 1290, 30),
            (3002, "Harry Potter And The Philosopher's Stone", 8937, 40),
            (3003, 'The Lion, The Lord Of The Rings', 6380, 37),
            (3004, 'Pride and Prejudice', 2356, 25),
            (3005, "Alice's Adventures In Wonderland", 5620, 12)
        ]
        cursor.execute('SELECT id FROM book WHERE id IN (?, ?, ?, ?, ?)',
                       [b[0] for b in books])
        existing_ids = {row[0] for row in cursor.fetchall()}
        new_books = [b for b in books if b[0] not in existing_ids]
        if new_books:
            cursor.executemany('''
                INSERT INTO book (id, title, authorID, quantity)
                VALUES (?, ?, ?, ?)
            ''', new_books)

        if new_authors or new_books:
            conn.commit()
            print(f"Inserted {len(new_authors)} authors,"
                  f" {len(new_books)} books.\n")
        else:
            print("Initial data exists.\n")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def validate_id(value, name):
    """Validate ID is a 4-digit integer.

    Args:
        value: Input value to validate.
        name (str): ID type (e.g., 'Book ID').
    Returns:
        int: Validated ID.
    """
    try:
        id = int(value)
        if not 1000 <= id <= 9999:
            raise ValueError(f"{name} must be 4 digits.")
        return id
    except ValueError as e:
        raise ValueError(f"Invalid {name}: Must be a 4-digit integer.") from e

def add_book():
    """Add new book and author."""
    print("\n--- Add New Book ---")
    # Handles author and book addition
    try:
        id = validate_id(input("Enter book ID: "), "Book ID")
        title = input("Enter book title: ")
        author_id = validate_id(input("Enter author ID: "), "Author ID")
        author_name = input("Enter author name: ").title()
        country = input("Enter author country: ").title()
        quantity = int(input("Enter quantity: "))

        if not title.strip() or not author_name.strip() or not country.strip():
            print("Error: Title, author, country cannot be empty.")
            return
        if quantity < 0:
            print("Error: Quantity cannot be negative.")
            return

        conn, cursor = connect_db()
        cursor.execute('SELECT ID FROM author WHERE ID = ?', (author_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO author (ID, Name, Country)
                VALUES (?, ?, ?)
            ''', (author_id, author_name, country))

        cursor.execute('''
            INSERT INTO book (id, title, authorID, quantity)
            VALUES (?, ?, ?, ?)
        ''', (id, title, author_id, quantity))
        conn.commit()
        print(f"Book '{title}' added.\n")
    except ValueError as e:
        print(f"Error: {e}")
    except sqlite3.IntegrityError:
        print("Error: Book or author ID already exists.")
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        conn.rollback()
    finally:
        conn.close()

def update_book():
    """Update book or author details."""
    print("\n--- Update Book ---")
    # Can only update name, country, title and quantity
    try:
        id = validate_id(input("Enter book ID: "), "Book ID")

        conn, cursor = connect_db()
        cursor.execute('''
            SELECT b.title, a.Name, a.Country
            FROM book b INNER JOIN author a ON b.authorID = a.ID
            WHERE b.id = ?
        ''', (id,))
        book = cursor.fetchone()
        if not book:
            print("Error: Book ID not found.")
            conn.close()
            return

        print(f"\nBook: {book[0]}")
        print(f"Author: {book[1]}, Country: {book[2]}")
        print("1. Update quantity")
        print("2. Update title")
        print("3. Update author name")
        print("4. Update author country")
        choice = input("Select option 1-4: ")

        if choice == "1":
            quantity = int(input("Enter new quantity: "))
            if quantity < 0:
                print("Error: Quantity cannot be negative.")
                conn.close()
                return
            cursor.execute('''
                UPDATE book SET quantity = ? WHERE id = ?
            ''', (quantity, id))
            print(f"Quantity updated for '{book[0]}'.\n")
        elif choice == "2":
            title = input("Enter new title: ")
            if not title.strip():
                print("Error: Title cannot be empty.")
                conn.close()
                return
            cursor.execute('''
                UPDATE book SET title = ? WHERE id = ?
            ''', (title, id))
            print(f"Title updated to '{title}'.\n")
        elif choice == "3":
            name = input("Enter new author name: ").title()
            if not name.strip():
                print("Error: Author name cannot be empty.")
                conn.close()
                return
            cursor.execute('''
                UPDATE author SET Name = ?
                WHERE ID = (SELECT authorID FROM book WHERE id = ?)
            ''', (name, id))
            print(f"Author name updated to '{name}'.\n")
        elif choice == "4":
            country = input("Enter new country: ").title()
            if not country.strip():
                print("Error: Country cannot be empty.")
                conn.close()
                return
            cursor.execute('''
                UPDATE author SET Country = ?
                WHERE ID = (SELECT authorID FROM book WHERE id = ?)
            ''', (country, id))
            print(f"Country updated to '{country}'.\n")
        else:
            print("Invalid choice, no updates.")
            conn.close()
            return

        conn.commit()
    except ValueError as e:
        print(f"Error: {e}")
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        conn.rollback()
    finally:
        conn.close()

def delete_book():
    """Delete book by ID."""
    print("\n--- Delete Book ---")
    try:
        id = validate_id(input("Enter book ID: "), "Book ID")

        conn, cursor = connect_db()
        cursor.execute('SELECT title FROM book WHERE id = ?', (id,))
        book = cursor.fetchone()
        if not book:
            print("Error: Book ID not found.")
            conn.close()
            return

        cursor.execute('DELETE FROM book WHERE id = ?', (id,))
        conn.commit()
        print(f"Book '{book[0]}' deleted.\n")
    except ValueError as e:
        print(f"Error: {e}")
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        conn.rollback()
    finally:
        conn.close()

def search_book():
    """Search books by ID or title."""
    print("\n--- Search Books ---")
    try:
        print("1. Search by ID")
        print("2. Search by title")
        choice = input("Select option (1-2): ")

        conn, cursor = connect_db()
        if choice == "1":
            id = validate_id(input("Enter book ID: "), "Book ID")
            cursor.execute('''
                SELECT b.id, b.title, a.Name, a.Country, b.quantity
                FROM book b INNER JOIN author a ON b.authorID = a.ID
                WHERE b.id = ?
            ''', (id,))
        # Can filter common entered keywords for convinient search
        elif choice == "2":
            title = input("Enter title (partial): ")
            cursor.execute('''
                SELECT b.id, b.title, a.Name, a.Country, b.quantity
                FROM book b INNER JOIN author a ON b.authorID = a.ID
                WHERE b.title LIKE ?
            ''', (f'%{title}%',))
        else:
            print("Invalid choice.")
            conn.close()
            return

        books = cursor.fetchall()
        if books:
            print("\nSearch results:")
            for book in books:
                print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, "
                      f"Country: {book[3]}, Qty: {book[4]}")
        else:
            print("No books found.\n")
    except ValueError as e:
        print(f"Error: {e}")
    except sqlite3.Error as e:
        print(f"DB error: {e}")
    finally:
        conn.close()

def view_all_books():
    """Show all books with author details."""
    print("\n--- View All Books ---")
    # Returns the author's name, country and book's title
    try:
        conn, cursor = connect_db()
        cursor.execute('''
            SELECT b.title, a.Name, a.Country
            FROM book b INNER JOIN author a ON b.authorID = a.ID
            ORDER BY b.title
        ''')
        books = cursor.fetchall()

        if books:
            print("\nDetails " + "-" * 50)
            for title, name, country in books:
                print(f"Title: {title}")
                print(f"Author's Name: {name}")
                print(f"Author's Country: {country}")
                print("-" * 52)
        else:
            print("No books found.\n")
    except sqlite3.Error as e:
        print(f"DB error: {e}")
    finally:
        conn.close()

def main_menu():
    """Run bookstore menu."""
    # Initializes database and menu
    create_tables()
    insert_initial_data()

    while True:
        print("=== Shelf Track: Bookstore Management ===")
        print("1. Enter book")
        print("2. Update book")
        print("3. Delete book")
        print("4. Search books")
        print("5. View details of all books")
        print("0. Exit")

        choice = input("Enter choice (0-5): ")

        if choice == "1":
            add_book()
        elif choice == "2":
            update_book()
        elif choice == "3":
            delete_book()
        elif choice == "4":
            search_book()
        elif choice == "5":
            view_all_books()
        elif choice == "0":
            print("Exiting Shelf Track. Goodbye!")
            break
        else:
            print("Invalid choice, try again.\n")

if __name__ == "__main__":
    main_menu()