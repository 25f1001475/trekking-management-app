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
    activate_staff
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
    return render_template("staff_dashboard.html")


@app.route("/trekker_dashboard")
def trekker_dashboard():
    if "user_id" not in session or session["role"] != "trekker":
            return redirect(url_for("login"))
    return render_template("trekker_dashboard.html")

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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)