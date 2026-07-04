from flask import Flask, render_template, request, redirect, url_for, session , flash
import mysql.connector
import subprocess
import os

app = Flask(__name__, template_folder="template")
app.secret_key = "secret123"

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Sam@200403#",
    "database": "flask_auth",
    "auth_plugin": "mysql_native_password"
}

def get_db():
    return mysql.connector.connect(**db_config)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect(url_for("design"))
        else:
            return render_template("Login.html", error="Invalid credentials")
    return render_template("Login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users
                (fullname, username, email, mobile, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (fullname, username, email, mobile, password))
            conn.commit()
            conn.close()
            flash("Registration Successful Please Login")
            return redirect(url_for("login"))
        except mysql.connector.Error:
            return render_template("Registration.html", error="Username or Email already exists")
    return render_template("Registration.html")

@app.route("/design")
def design():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("Design.html")

@app.route("/run_cv", methods=["POST"])
def start_program():
    if "user" not in session:
        return redirect(url_for("login"))

    # Use Python from your virtual environment
    python_exe = r"D:\BscTYproject\.venv\Scripts\python.exe"
    script_path = r"D:\BscTYproject\PythonDet.py"

    # Start detection script in a separate process
    subprocess.Popen([python_exe, script_path], shell=True)

# add the loading GIF
    return """
<h2 style='text-align:center;margin-top:120px; font-weight:bold; font-size:40px;'>
    Project is starting.. Wait a few moments.. 😊
</h2>
<img src="/static/Loading.gif" style="display:block; margin:auto;">
"""



@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
