import sqlite3
from datetime import date




def create_connection():
    conn = sqlite3.connect(
        "instance/trekking.db",
        timeout=30
    )
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
    payment_status TEXT NOT NULL DEFAULT 'Pending',
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

def trek_has_bookings(trek_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bookings
        WHERE trek_id = ?
    """, (trek_id,))

    count = cursor.fetchone()[0]

    conn.close()

    return count > 0

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

def get_staff_dashboard_counts(staff_id):

    conn = create_connection()
    cursor = conn.cursor()

    # Assigned Treks
    cursor.execute("""
        SELECT COUNT(*)
        FROM Treks
        WHERE assigned_staff = ?
    """, (staff_id,))
    assigned_treks = cursor.fetchone()[0]

    # Open Treks
    cursor.execute("""
        SELECT COUNT(*)
        FROM Treks
        WHERE assigned_staff = ?
        AND status = 'Open'
    """, (staff_id,))
    open_treks = cursor.fetchone()[0]

    # Total Participants
    cursor.execute("""
        SELECT COUNT(*)
        FROM Bookings B
        JOIN Treks T
        ON B.trek_id = T.trek_id
        WHERE T.assigned_staff = ?
    """, (staff_id,))
    total_participants = cursor.fetchone()[0]

    conn.close()

    return (
        assigned_treks,
        total_participants,
        open_treks
    )

def get_staff_treks(staff_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            T.trek_id,
            T.trek_name,
            T.location,
            COUNT(B.booking_id),
            T.available_slots,
            T.status

        FROM Treks T

        LEFT JOIN Bookings B
        ON T.trek_id = B.trek_id

        WHERE T.assigned_staff = ?

        GROUP BY T.trek_id

        ORDER BY T.trek_name
    """, (staff_id,))

    treks = cursor.fetchall()

    conn.close()

    return treks

def get_staff_trek_by_id(trek_id, staff_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            trek_id,
            trek_name,
            location,
            difficulty,
            duration,
            start_date,
            end_date,
            available_slots,
            status,
            description

        FROM Treks

        WHERE trek_id = ?
        AND assigned_staff = ?
    """, (trek_id, staff_id))

    trek = cursor.fetchone()

    conn.close()

    return trek

def update_staff_trek(trek_id, staff_id, available_slots, status):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Treks

        SET
            available_slots = ?,
            status = ?

        WHERE trek_id = ?
        AND assigned_staff = ?
    """, (
        available_slots,
        status,
        trek_id,
        staff_id
    ))

    conn.commit()
    conn.close()

def get_staff_participants(staff_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            T.trek_name,
            U.name,
            U.phone,
            B.booking_date,
            B.status

        FROM Bookings B

        JOIN Users U
        ON B.user_id = U.user_id

        JOIN Treks T
        ON B.trek_id = T.trek_id

        WHERE T.assigned_staff = ?

        ORDER BY
            T.trek_name,
            U.name
    """, (staff_id,))

    participants = cursor.fetchall()

    conn.close()

    return participants

def get_staff_profile(staff_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            name,
            email,
            phone,
            password
        FROM Users
        WHERE user_id = ?
    """, (staff_id,))

    staff = cursor.fetchone()

    conn.close()

    return staff

def update_staff_profile(staff_id, name, phone, password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users

        SET
            name = ?,
            phone = ?,
            password = ?

        WHERE user_id = ?
    """, (
        name,
        phone,
        password,
        staff_id
    ))

    conn.commit()
    conn.close()

def get_trekker_dashboard_counts(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Treks
        WHERE status = 'Open'
        AND available_slots > 0
    """)
    available_treks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bookings
        WHERE user_id = ?
    """, (user_id,))
    my_bookings = cursor.fetchone()[0]

    conn.close()

    return available_treks, my_bookings

def get_available_treks():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            trek_id,
            trek_name,
            location,
            difficulty,
            duration,
            available_slots

        FROM Treks

        WHERE
            status='Open'
        AND
            available_slots>0

        ORDER BY trek_name
    """)

    treks = cursor.fetchall()

    conn.close()

    return treks

def get_user_recent_bookings(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            T.trek_name,
            B.booking_date,
            B.status,
            B.booking_id

        FROM Bookings B

        JOIN Treks T
        ON B.trek_id = T.trek_id

        WHERE B.user_id = ?

        ORDER BY B.booking_date DESC
    """, (user_id,))

    bookings = cursor.fetchall()

    conn.close()

    return bookings

def get_locations():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT location
        FROM Treks
        WHERE status='Open'
        ORDER BY location
    """)

    locations = cursor.fetchall()

    conn.close()

    return locations

def get_difficulties():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT difficulty
        FROM Treks
        WHERE status='Open'
        ORDER BY difficulty
    """)

    difficulties = cursor.fetchall()

    conn.close()

    return difficulties

def filter_treks(location=None, difficulty=None):

    conn = create_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            trek_id,
            trek_name,
            location,
            difficulty,
            duration,
            available_slots

        FROM Treks

        WHERE
            status='Open'
        AND
            available_slots>0
    """

    values = []

    if location:
        query += " AND location=?"
        values.append(location)

    if difficulty:
        query += " AND difficulty=?"
        values.append(difficulty)

    query += " ORDER BY trek_name"

    cursor.execute(query, values)

    treks = cursor.fetchall()

    conn.close()

    return treks

def get_trek_by_id(trek_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            trek_id,
            trek_name,
            location,
            difficulty,
            duration,
            start_date,
            end_date,
            available_slots,
            status,
            description

        FROM Treks

        WHERE trek_id = ?
    """, (trek_id,))

    trek = cursor.fetchone()

    conn.close()

    return trek

def user_has_booking(user_id, trek_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bookings
        WHERE
            user_id = ?
        AND
            trek_id = ?
    """, (user_id, trek_id))

    count = cursor.fetchone()[0]

    conn.close()

    return count > 0

def book_trek(user_id, trek_id):

    conn = create_connection()
    cursor = conn.cursor()

    booking_date = date.today().isoformat()

    cursor.execute("""
        INSERT INTO Bookings
        (
            user_id,
            trek_id,
            booking_date,
            status,
            payment_status
        )

        VALUES
        (
            ?,
            ?,
            ?,
            'Booked',
            'Pending'
        )
    """, (
        user_id,
        trek_id,
        booking_date
    ))

    cursor.execute("""
        UPDATE Treks

        SET available_slots =
            available_slots - 1

        WHERE trek_id = ?
    """, (trek_id,))

    conn.commit()
    conn.close()

def get_user_bookings(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            B.booking_id,
            T.trek_name,
            T.location,
            T.start_date,
            T.end_date,
            B.booking_date,
            B.status,
            B.payment_status,
            T.trek_id

        FROM Bookings B

        JOIN Treks T
        ON B.trek_id = T.trek_id

        WHERE B.user_id = ?

        ORDER BY B.booking_date DESC
    """, (user_id,))

    bookings = cursor.fetchall()

    conn.close()

    return bookings

def get_user_history(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            T.trek_name,
            T.location,
            T.start_date,
            T.end_date,
            B.booking_date,
            B.status,
            B.payment_status

        FROM Bookings B

        JOIN Treks T
        ON B.trek_id = T.trek_id

        WHERE
            B.user_id = ?
        AND
            T.status = 'Completed'

        ORDER BY T.end_date DESC
    """, (user_id,))

    history = cursor.fetchall()

    conn.close()

    return history

def get_trekker_profile(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            name,
            email,
            phone,
            password
        FROM Users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    conn.close()

    return user

def update_trekker_profile(user_id, name, phone, password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users

        SET
            name = ?,
            phone = ?,
            password = ?

        WHERE user_id = ?
    """, (
        name,
        phone,
        password,
        user_id
    ))

    conn.commit()
    conn.close()

def update_booking_status_by_trek(trek_id, booking_status):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Bookings
        SET status = ?
        WHERE trek_id = ?
    """, (booking_status, trek_id))

    conn.commit()
    conn.close()

def get_booking_details(booking_id, user_id=None):

    conn = create_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            B.booking_id,
            T.trek_name,
            T.location,
            T.difficulty,
            T.duration,
            T.start_date,
            T.end_date,
            B.booking_date,
            B.status,
            B.payment_status,
            U.name,
            T.description

        FROM Bookings B

        JOIN Treks T
            ON B.trek_id = T.trek_id

        LEFT JOIN Users U
            ON T.assigned_staff = U.user_id

        WHERE B.booking_id = ?
    """

    values = [booking_id]

    if user_id is not None:
        query += " AND B.user_id = ?"
        values.append(user_id)

    cursor.execute(query, values)

    booking = cursor.fetchone()

    conn.close()

    return booking

def cancel_booking(booking_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Bookings
        SET status = 'Cancelled'
        WHERE booking_id = ?
    """, (booking_id,))

    conn.commit()
    conn.close()

def restore_trek_slot(booking_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Treks

        SET available_slots = available_slots + 1

        WHERE trek_id = (

            SELECT trek_id
            FROM Bookings
            WHERE booking_id = ?

        )
    """, (booking_id,))

    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    create_tables()
    create_admin()