from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

HOST = "localhost"
USER = "root"
PASSWORD = ""
DATABASE = "fooddelivery"

# Enable CORS for all routes
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.urandom(24)

# MySQL configurations
app.config['MYSQL_USER'] = USER
app.config['MYSQL_PASSWORD'] = PASSWORD
app.config['MYSQL_DB'] = DATABASE
app.config['MYSQL_HOST'] = HOST

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
    if user and check_password_hash(user[0], password):
        return redirect(url_for('menu'))
    else:
        flash("Invalid email or password!")
        return redirect(url_for('home'))

# Admin login handling
@app.route('/admin_login', methods=['POST'])
def admin_login():
    print(request.form)
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT password FROM admin WHERE email = %s", (email,))
        admin = cur.fetchone()
    finally:
        cur.close()

    if admin and admin[0]==password:  # Check hashed password
        return redirect(url_for('admin_dashboard'))
    else:
        flash("Invalid email or password!")
        return redirect(url_for('home'))

# Route for handling user signup
@app.route('/signuppage.html', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        address = request.form['address']
        phone = request.form['phone']

        if password != confirm_password:
            return render_template('signuppage.html', error="Passwords do not match!")

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (name, email, password, address, phone_no) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, hashed_password, address, phone))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('menu'))
    
    return render_template('signuppage.html')

# Route for menu page
@app.route('/menu')
def menu():
    return render_template('menupage.html')


@app.route('/add_food', methods=['POST'])
def add_food():
    food_name = request.form['foodName']
    food_price = request.form['foodPrice']
    food_quantity = request.form['foodQuantity']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO menu (name, price, count) VALUES (%s, %s, %s)",
                (food_name, food_price, food_quantity))
    mysql.connection.commit()
    cur.close()
    flash("Food item added successfully!")  # Flash success message
    return redirect(url_for('admin_dashboard'))


# API Endpoint to modify food item
@app.route('/modify_food', methods=['POST'])
def modify_food():
    modify_food_name = request.form['modifyFood']
    new_food_name = request.form['modifyFoodName']
    new_price = request.form['modifyFoodPrice']
    new_quantity = request.form['modifyFoodQuantity']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE menu SET name = %s, price = %s, count = %s WHERE name = %s",
                (new_food_name, new_price, new_quantity, modify_food_name))
    mysql.connection.commit()
    cur.close()
    flash("Food item modified successfully!")  # Flash success message
    return redirect(url_for('admin_dashboard'))

# API Endpoint to delete food item
@app.route('/delete_food', methods=['POST'])
def delete_food():
    food_name = request.form['deleteFoodName']

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM menu WHERE name = %s", (food_name,))
    mysql.connection.commit()
    cur.close()
    flash("Food item deleted successfully!")  # Flash success message
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT name, price, quantity FROM menu")
    food_item = cur1.fetchall()
    cur1.close()
    
    return render_template('adminpage.html', food_item=food_item)
  
# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)

