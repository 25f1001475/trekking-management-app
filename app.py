from flask import Flask, render_template,request,redirect,url_for,session
from database import (
    create_connection,
    get_dashboard_counts,
    add_trek,
    delete_trek,
    get_all_treks,
    get_trek_by_id,
    update_trek,
    get_all_staff,
    approve_staff,
    reject_staff,
    get_approved_staff,
    get_all_users,
    deactivate_user,
    activate_user,
    search_records,
    get_all_bookings,
    deactivate_staff,
    activate_staff,
    get_staff_dashboard_counts,
    get_staff_treks,
    get_staff_trek_by_id,
    update_staff_trek,
    get_staff_participants,
    trek_has_bookings,
    get_staff_profile,
    update_staff_profile,
    get_trekker_dashboard_counts,
    get_available_treks,
    get_user_recent_bookings,
    get_locations,
    get_difficulties,
    filter_treks,
    get_trek_by_id,
    user_has_booking,
    book_trek,
    get_user_bookings,
    get_user_history,
    get_trekker_profile,
    update_trekker_profile,
)
app = Flask(__name__)
app.secret_key = "trekking_secret_key"


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
    
        email=request.form["email"]
        password=request.form["password"]
        
        conn=create_connection()
        cursor=conn.cursor()

        cursor.execute(
            """SELECT * FROM Users where email=?
            """,(email,)
            )

        user=cursor.fetchone()

        if user is None:
            conn.close()
            return "User not found."
        stored_password = user[3]
        role = user[5]
        approval_status = user[6]
        account_status = user[7]

        if password != stored_password:
            conn.close()
            return "Incorrect password."

        if account_status == "Inactive":
            conn.close()
            return "Your account has been deactivated by the administrator."

        if role=="admin":
            session["user_id"] = user[0]
            session["role"] = role

            conn.close()
            return redirect(url_for("admin_dashboard"))

        elif role=="staff":
            if approval_status == "Pending":
                conn.close()
                return "Please wait for admin approval."
            session["user_id"] = user[0]
            session["role"] = role
            conn.close()
            return redirect(url_for("staff_dashboard"))

        elif role=="trekker":
            session["user_id"] = user[0]
            session["role"] = role
            conn.close()
            return redirect(url_for("trekker_dashboard"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        if password != confirm_password:
            return "Passwords do not match."
        
        conn=create_connection()
        cursor=conn.cursor()

        cursor.execute(
            "SELECT user_id from users where email=?",(email,)
        )

        existing_user=cursor.fetchone()

        if existing_user:
            conn.close()
            return "Email already exists."
        if role=="trekker":
            approval_status="Approved"
        else:
            approval_status="Pending"

        cursor.execute("""
            INSERT INTO Users
            (name, email, phone, password, role, approval_status)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
            name,
            email,
            phone,
            password,
            role,
            approval_status
        ))

        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
            return redirect(url_for("login"))
    total_treks, total_trekkers, total_staff, total_bookings = get_dashboard_counts()
    return render_template(
        "admin_dashboard.html",
        total_treks=total_treks,
        total_trekkers=total_trekkers,
        total_staff=total_staff,
        total_bookings=total_bookings
    )

@app.route("/staff_dashboard")
def staff_dashboard():

    if "user_id" not in session or session["role"] != "staff":
        return redirect(url_for("login"))

    staff_id = session["user_id"]

    assigned_treks, total_participants, open_treks = \
        get_staff_dashboard_counts(staff_id)

    treks = get_staff_treks(staff_id)

    return render_template(
        "staff_dashboard.html",
        assigned_treks=assigned_treks,
        total_participants=total_participants,
        open_treks=open_treks,
        treks=treks
    )


@app.route("/trekker_dashboard")
def trekker_dashboard():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    available_treks, my_bookings = \
        get_trekker_dashboard_counts(user_id)

    treks = get_available_treks()

    bookings = get_user_recent_bookings(user_id)

    return render_template(
        "trekker_dashboard.html",
        available_treks=available_treks,
        my_bookings=my_bookings,
        treks=treks,
        bookings=bookings
    )

@app.route("/browse_treks")
def browse_treks():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect(url_for("login"))

    location = request.args.get("location")
    difficulty = request.args.get("difficulty")

    treks = filter_treks(location, difficulty)

    locations = get_locations()

    difficulties = get_difficulties()

    return render_template(
        "browse_treks.html",
        treks=treks,
        locations=locations,
        difficulties=difficulties,
        selected_location=location,
        selected_difficulty=difficulty
    )


@app.route("/trek_details/<int:trek_id>", methods=["GET", "POST"])
def trek_details(trek_id):

    if "user_id" not in session or session["role"] != "trekker":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    trek = get_trek_by_id(trek_id)

    if trek is None:
        return "Trek not found."

    if request.method == "POST":

        if user_has_booking(user_id, trek_id):
            return "<h2>You have already booked this trek.</h2>"

        if trek[8] != "Open":
            return "<h2>This trek is not open for booking.</h2>"

        if trek[7] <= 0:
            return "<h2>No slots available.</h2>"

        book_trek(user_id, trek_id)

        return redirect(url_for("my_bookings"))

    return render_template(
        "trek_details.html",
        trek=trek
    )


@app.route("/my_bookings")
def my_bookings():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    bookings = get_user_bookings(user_id)

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

@app.route("/booking_details/<int:trek_id>")
def booking_details(trek_id):

    if "user_id" not in session or session["role"] != "trekker":
        return redirect(url_for("login"))

    return f"<h2>Booking Details {trek_id}</h2>"


@app.route("/trek_history")
def trek_history():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    history = get_user_history(user_id)

    return render_template(
        "trek_history.html",
        history=history
    )


@app.route("/trekker_profile", methods=["GET", "POST"])
def trekker_profile():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        password = request.form["password"]

        update_trekker_profile(
            user_id,
            name,
            phone,
            password
        )

        return redirect(url_for("trekker_profile"))

    user = get_trekker_profile(user_id)

    return render_template(
        "trekker_profile.html",
        user=user
    )

@app.route("/manage_treks")
def manage_treks():

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))
    
    treks = get_all_treks()
    return render_template(
        "manage_treks.html",
        treks=treks
    )


@app.route("/manage_staff")
def manage_staff():

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    staff = get_all_staff()

    return render_template(
        "manage_staff.html",
        staff=staff
    )

@app.route("/add_trek", methods=["GET", "POST"])
def add_trek_page():
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        trek_name = request.form["trek_name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        available_slots = request.form["available_slots"]
        assigned_staff = request.form["assigned_staff"]
        status = request.form["status"]
        description = request.form["description"]

        add_trek(
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
        )

        return redirect(url_for("manage_treks"))
    staff = get_approved_staff()
    return render_template("add_trek.html",staff=staff)

@app.route("/edit_trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek_page(trek_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        trek_name = request.form["trek_name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        available_slots = request.form["available_slots"]
        assigned_staff = request.form["assigned_staff"]
        status = request.form["status"]
        description = request.form["description"]

        update_trek(
            trek_id,
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
        )

        return redirect(url_for("manage_treks"))

    trek = get_trek_by_id(trek_id)
    staff = get_approved_staff()

    return render_template(
        "add_trek.html",
        trek=trek,staff=staff
    )

@app.route("/delete_trek/<int:trek_id>")
def delete_trek_page(trek_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    if trek_has_bookings(trek_id):
        return """
        <h2>Cannot delete this trek because bookings already exist.</h2>

        <a href='/manage_treks'>Back to Manage Treks</a>
        """

    delete_trek(trek_id)

    return redirect(url_for("manage_treks"))
@app.route("/approve_staff/<int:user_id>")
def approve_staff_page(user_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    approve_staff(user_id)

    return redirect(url_for("manage_staff"))

@app.route("/reject_staff/<int:user_id>")
def reject_staff_page(user_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    reject_staff(user_id)

    return redirect(url_for("manage_staff"))

@app.route("/deactivate_staff/<int:user_id>")
def deactivate_staff_page(user_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    deactivate_staff(user_id)

    return redirect(url_for("manage_staff"))


@app.route("/activate_staff/<int:user_id>")
def activate_staff_page(user_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    activate_staff(user_id)

    return redirect(url_for("manage_staff"))

@app.route("/manage_users")
def manage_users():

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    users = get_all_users()

    return render_template(
        "manage_users.html",
        users=users
    )
@app.route("/deactivate_user/<int:user_id>")
def deactivate_user_page(user_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    deactivate_user(user_id)

    return redirect(url_for("manage_users"))


@app.route("/activate_user/<int:user_id>")
def activate_user_page(user_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    activate_user(user_id)

    return redirect(url_for("manage_users"))

@app.route("/search", methods=["GET", "POST"])
def search():

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    results = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        results = search_records(keyword)

    return render_template(
        "search.html",
        results=results
    )

@app.route("/booking_records")
def booking_records():

    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    bookings = get_all_bookings()

    return render_template(
        "booking_records.html",
        bookings=bookings
    )

@app.route("/my_treks")
def my_treks():

    if "user_id" not in session or session["role"] != "staff":
        return redirect(url_for("login"))

    staff_id = session["user_id"]

    treks = get_staff_treks(staff_id)

    return render_template(
        "my_treks.html",
        treks=treks)


@app.route("/participants")
def participants():

    if "user_id" not in session or session["role"] != "staff":
        return redirect(url_for("login"))

    staff_id = session["user_id"]

    participants = get_staff_participants(staff_id)

    return render_template(
        "participants.html",
        participants=participants
    )

@app.route("/staff_profile", methods=["GET", "POST"])
def staff_profile():

    if "user_id" not in session or session["role"] != "staff":
        return redirect(url_for("login"))

    staff_id = session["user_id"]

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        password = request.form["password"]

        update_staff_profile(
            staff_id,
            name,
            phone,
            password
        )

        return redirect(url_for("staff_profile"))

    staff = get_staff_profile(staff_id)

    return render_template(
        "staff_profile.html",
        staff=staff
    )


@app.route("/manage_staff_trek/<int:trek_id>", methods=["GET", "POST"])
def manage_staff_trek(trek_id):

    if "user_id" not in session or session["role"] != "staff":
        return redirect(url_for("login"))

    staff_id = session["user_id"]

    if request.method == "POST":

        available_slots = request.form["available_slots"]
        status = request.form["status"]

        update_staff_trek(
            trek_id,
            staff_id,
            available_slots,
            status
        )

        return redirect(url_for("my_treks"))

    trek = get_staff_trek_by_id(
        trek_id,
        staff_id
    )

    if trek is None:
        return "Trek not found or access denied."

    return render_template(
        "manage_staff_trek.html",
        trek=trek
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)