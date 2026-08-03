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
            approval_status TEXT NOT NULL DEFAULT 'Approved',
            account_status TEXT NOT NULL DEFAULT 'Active'
        )
"""
)

    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS Treks(
    trek_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trek_name TEXT NOT NULL,
    location TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    duration INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    available_slots INTEGER NOT NULL,
    assigned_staff INTEGER,
    status TEXT NOT NULL DEFAULT 'Open',
    description TEXT,
    FOREIGN KEY (assigned_staff) REFERENCES Users(user_id)
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
    (email, name, password, phone, role, approval_status, account_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "admin@trek.com",
    "Admin",
    "admin123",
    "9876543210",
    "admin",
    "Approved",
    "Active"
))

        conn.commit()
        print("Default admin created.")

    else:
        print("Admin already exists.")

def get_dashboard_counts():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Treks
    """)
    total_treks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM Users
        WHERE role = 'trekker'
    """)
    total_trekkers = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM Users
        WHERE role = 'staff'
    """)
    total_staff = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bookings
    """)
    total_bookings = cursor.fetchone()[0]

    conn.close()

    return (
        total_treks,
        total_trekkers,
        total_staff,
        total_bookings
    )

def add_trek(trek_name, location, difficulty, duration,
             start_date, end_date, available_slots,assigned_staff, status,
             description):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Treks
        (trek_name, location, difficulty, duration,
         start_date, end_date, available_slots,assigned_staff,
         status, description)

         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trek_name,
        location,
        difficulty,
        duration,
        start_date,
        end_date,
        available_slots,
        assigned_staff,
        status,
        description
    ))

    conn.commit()
    conn.close()

def delete_trek(trek_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM Treks
        WHERE trek_id = ?
    """, (trek_id,))

    conn.commit()
    conn.close()

def get_all_treks():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
    T.trek_id,
    T.trek_name,
    T.location,
    T.difficulty,
    U.name,
    T.available_slots,
    T.status
    FROM Treks T
    LEFT JOIN Users U
    ON T.assigned_staff = U.user_id
    ORDER BY T.trek_id
    """)

    treks = cursor.fetchall()

    conn.close()

    return treks

def get_trek_by_id(trek_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Treks
        WHERE trek_id = ?
    """, (trek_id,))

    trek = cursor.fetchone()

    conn.close()
    return trek

def update_trek(trek_id, trek_name, location, difficulty,
                duration, start_date, end_date,
                available_slots,assigned_staff,status, description):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Treks
        SET trek_name = ?,
            location = ?,
            difficulty = ?,
            duration = ?,
            start_date = ?,
            end_date = ?,
            available_slots = ?,
            assigned_staff = ?,
            status = ?,
            description = ?
        WHERE trek_id = ?
    """, (
        trek_name,
        location,
        difficulty,
        duration,
        start_date,
        end_date,
        available_slots,
        assigned_staff,
        status,
        description,
        trek_id
    ))

    conn.commit()
    conn.close()

def get_all_staff():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id,
               name,
               email,
               phone,
               approval_status,
               account_status
        FROM Users
        WHERE role = 'staff'
    """)

    staff = cursor.fetchall()

    conn.close()

    return staff

def approve_staff(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users
        SET approval_status = 'Approved'
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def reject_staff(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM Users
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def get_approved_staff():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, name
        FROM Users
        WHERE role = 'staff'
        AND approval_status = 'Approved'
    """)

    staff = cursor.fetchall()

    conn.close()

    return staff

def deactivate_staff(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users
        SET account_status = 'Inactive'
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def activate_staff(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users
        SET account_status = 'Active'
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def get_all_users():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            user_id,
            name,
            email,
            phone,
            role,
            approval_status,
            account_status
        FROM Users
        ORDER BY user_id
    """)

    users = cursor.fetchall()

    conn.close()

    return users

def deactivate_user(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users
        SET account_status = 'Inactive'
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def activate_user(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users
        SET account_status = 'Active'
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def search_records(keyword):

    conn = create_connection()
    cursor = conn.cursor()

    keyword = f"%{keyword}%"

    results = []

    # Search Treks
    cursor.execute("""
        SELECT
            trek_id,
            trek_name
        FROM Treks
        WHERE trek_name LIKE ?
           OR CAST(trek_id AS TEXT) LIKE ?
    """, (keyword, keyword))

    for row in cursor.fetchall():
        results.append(("Trek", row[0], row[1]))

    # Search Staff
    cursor.execute("""
        SELECT
            user_id,
            name
        FROM Users
        WHERE role='staff'
        AND (
            name LIKE ?
            OR CAST(user_id AS TEXT) LIKE ?
        )
    """, (keyword, keyword))

    for row in cursor.fetchall():
        results.append(("Staff", row[0], row[1]))

    # Search Trekkers
    cursor.execute("""
        SELECT
            user_id,
            name
        FROM Users
        WHERE role='trekker'
        AND (
            name LIKE ?
            OR CAST(user_id AS TEXT) LIKE ?
        )
    """, (keyword, keyword))

    for row in cursor.fetchall():
        results.append(("User", row[0], row[1]))

    conn.close()

    return results

def get_all_bookings():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            B.booking_id,
            U.name,
            T.trek_name,
            B.booking_date,
            B.status
        FROM Bookings B
        JOIN Users U
            ON B.user_id = U.user_id
        JOIN Treks T
            ON B.trek_id = T.trek_id
        ORDER BY B.booking_id
    """)

    bookings = cursor.fetchall()

    conn.close()

    return bookings

if __name__ == "__main__":
    create_tables()
    create_admin()