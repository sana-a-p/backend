from flask import Flask, render_template, request, redirect, url_for,flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) 
# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'san@06FEB2004'
app.config['MYSQL_DB'] = 'fooddelivery'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/', methods=['POST'])  # Handling user login on the homepage
def user_login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    try:
        # Fetch user by email
        cur.execute("SELECT password FROM user WHERE email = %s", (email,))
        user = cur.fetchone()
    finally:
        cur.close()

    # Check if user exists and if the password matches
    if user and check_password_hash(user[0], password):  # Assuming password is hashed
        return redirect(url_for('menu'))  # Redirect to the menu page after successful login
    else:
        flash("Invalid email or password!")  # Show an error message
        return redirect(url_for('home'))  # Redirect back to the homepage

# Admin login handling (create a new route)
@app.route('/admin_login', methods=['POST'])
def admin_login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    try:
        # Fetch admin by email
        cur.execute("SELECT password FROM admin WHERE email = %s", (email,))  # Assuming you have an admin table
        admin = cur.fetchone()
    finally:
        cur.close()

    # Check if admin exists and if the password matches
    if admin and admin[0] == password:  # Assuming password is hashed
        return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
    else:
        flash("Invalid email or password!")  # Show an error message
        return redirect(url_for('home'))  # Redirect back to the homepage
# Route for handling user signup
@app.route('/signuppage.html', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        address = request.form['address']
        phone = request.form['phone']

        # Check if passwords match
        if password != confirm_password:
            return render_template('signuppage.html', error="Passwords do not match!")

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (name, email, password, address, phone_no) VALUES (%s, %s, %s, %s, %s)",(name, email, hashed_password, address, phone))
        mysql.connection.commit()
        cur.close()

        # Redirect to menu page after successful signup
        return redirect(url_for('menu'))
    
    else:
        # Render the signup page on GET request
        return render_template('signuppage.html')

# Route for menu page (after signup)
@app.route('/menu')
def menu():
    return render_template('menupage.html')
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('adminpage.html')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
