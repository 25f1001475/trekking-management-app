from flask import Flask, render_template,request,redirect,url_for,session
from database import create_connection

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

        if password != stored_password:
            conn.close()
            return "Incorrect password."

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
    return render_template("admin_dashboard.html")


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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)