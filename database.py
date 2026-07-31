import sqlite3


def create_connection():
    conn = sqlite3.connect("instance/trekking.db")
    return conn


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """ 
CREATE TABLE IF NOT EXISTS Users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            approval_status TEXT NOT NULL DEFAULT 'Approved'
        )
"""
    )

    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS Treks (
            trek_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trek_name TEXT NOT NULL,
            location TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            duration INTEGER NOT NULL,
            available_slots INTEGER NOT NULL,
            assigned_staff_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            FOREIGN KEY (assigned_staff_id) REFERENCES Users(user_id)
        )
        """
    )


    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS Bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trek_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Booked',
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (trek_id) REFERENCES Treks(trek_id)
        )
        """
    )

    conn.commit()
    conn.close()


def create_admin():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id
    FROM Users
    WHERE email = ?
    """, ("admin@trek.com",))

    admin = cursor.fetchone()

    if admin is None:
        cursor.execute("""
            INSERT INTO Users
            (email, name, password, phone, role, approval_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "admin@trek.com",
            "Admin",
            "admin123",
            "9876543210",
            "admin",
            "Approved"
        ))

        conn.commit()
        print("Default admin created.")

    else:
        print("Admin already exists.")

if __name__ == "__main__":
    create_tables()
    create_admin()