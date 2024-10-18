CREATE database fooddelivery;
use fooddelivery;
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone_no VARCHAR(15),
    address TEXT
)AUTO_INCREMENT=100;

CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(50) UNIQUE
);

CREATE TABLE menu (
    menu_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    food_name VARCHAR(100) NOT NULL,
    address VARCHAR(250) NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) AUTO_INCREMENT = 100;

CREATE TABLE order_details (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    menu_id INT,
    count INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id)
);
INSERT INTO admin (email,password) VALUES ("admin123@gmail.com","admin@123");
