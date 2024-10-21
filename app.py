from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')
HOST = os.getenv('HOST')
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
        cur = mysql.connection.cursor()
        try:
           
            cur.execute("INSERT INTO orders (email) VALUES (%s)", (email,))
            mysql.connection.commit()
        finally:
            cur.close()
        return redirect(url_for('menu'))
    else:
        flash("Invalid email or password!")
        return redirect(url_for('home'))

# Admin login handling
@app.route('/admin_login', methods=['POST'])
def admin_login():
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

        return redirect(url_for('home'))
    return render_template('signuppage.html')



@app.route('/add_food', methods=['POST'])
def add_food():
    food_name = request.form['foodName']
    food_price = request.form['foodPrice']
    food_quantity = request.form['foodQuantity']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO menu (name, price, quantity) VALUES (%s, %s, %s)",
                (food_name, food_price, food_quantity))
    mysql.connection.commit()
    cur.close()
    flash("Food item added successfully!")  # Flash success message
    return redirect(url_for('admin_dashboard'))


# API Endpoint to retrieve all food items


# API Endpoint to modify food item
@app.route('/modify_food', methods=['POST'])
def modify_food():
    modify_food_name = request.form['modifyFood']
    new_food_name = request.form['modifyFoodName']
    new_price = request.form['modifyFoodPrice']
    new_quantity = request.form['modifyFoodQuantity']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE menu SET name = %s, price = %s, quantity = %s WHERE name = %s",
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

@app.route('/menu')
def menu():
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, price, quantity FROM menu")
    food_items = cur.fetchall()  # Fetch all items from the menu table
    cur.close()

    return render_template('menupage.html', food_items=food_items)

@app.route('/place_order', methods=['POST'])
def place_order():
    order_items = request.form  # Access the submitted form data
    cur = mysql.connection.cursor()

    # List to store the selected food items
    selected_items = []

    # Loop through form data to process each item
    for food_name, count_str in order_items.items():
        try:
            count = int(count_str)
        except ValueError:
            count = 0  # If count is not a valid integer, treat it as zero

        if count > 0:
            # Fetch food item from the menu
            cur.execute("SELECT quantity, price FROM menu WHERE name = %s", (food_name,))
            menu_item = cur.fetchone()

            if menu_item:
                available_quantity, price = menu_item

                # Validate if the user-selected count does not exceed available stock
                if count > available_quantity:
                    flash(f"Not enough stock for {food_name}. Available: {available_quantity}.")
                    return redirect(url_for('menu'))

                # Prepare item for order details
                selected_items.append({
                    'name': food_name,
                    'count': count,
                    'price': price
                })

    if not selected_items:
        flash("No items selected or invalid quantities entered.")
        return redirect(url_for('menu'))

    # Insert each selected item into order_details and update menu stock
    cur.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
    order_id = cur.fetchone()[0]

    total_price = 0  # Initialize total price

    for item in selected_items:
        cur.execute("INSERT INTO order_details (order_id, food_name, price, count) VALUES (%s, %s, %s, %s)",
                    (order_id, item['name'], item['price'], item['count']))
        # Update the menu quantity
        cur.execute("UPDATE menu SET quantity = quantity - %s WHERE name = %s", (item['count'], item['name']))

        # Calculate total price
        total_price += item['price'] * item['count']

    mysql.connection.commit()
    cur.close()
    flash("Order placed successfully!")
    # Pass the order details to the template
    return render_template('orderpage.html', order_items=selected_items, total_price=total_price)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)




