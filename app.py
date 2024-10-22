from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect('supermarket.db')
    return conn

# Initialize the database and create tables
def init_db():
    with connect_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            barcode TEXT NOT NULL UNIQUE
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            barcode TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )''')

# Route for displaying products
@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Add product to the database
@app.route('/add', methods=['POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']
    barcode = request.form['barcode']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, quantity, barcode) VALUES (?, ?, ?, ?)",
                   (name, price, quantity, barcode))
    conn.commit()
    conn.close()

    flash('Product added successfully!', 'success')
    return redirect(url_for('index'))

# Sell a product based on its barcode
@app.route('/sell', methods=['POST'])
def sell_product():
    barcode = request.form['barcode']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()

    if product and product[0] > 0:
        new_quantity = product[0] - 1
        cursor.execute("UPDATE products SET quantity = ? WHERE barcode = ?", (new_quantity, barcode))
        conn.commit()

        # Log the action
        cursor.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                       ('Sold 1 item', barcode, datetime.now()))
        conn.commit()

        # flash('Product sold!', 'success')
    else:
        flash('Product not found or out of stock!', 'danger')

    conn.close()
    return redirect(url_for('index'))

# View logs of all actions
@app.route('/logs')
def view_logs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return render_template('logs.html', logs=logs)

@app.route('/scan-sell', methods=['POST'])
def scan_sell():
    barcode = request.form['barcode']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()

    if product and product[0] > 0:
        new_quantity = product[0] - 1
        cursor.execute("UPDATE products SET quantity = ? WHERE barcode = ?", (new_quantity, barcode))
        conn.commit()

        # Log the action
        cursor.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                       ('Sold 1 item', barcode, datetime.now()))
        conn.commit()

        conn.close()
        return
    else:
        conn.close()
        return jsonify({"success": False, "message": "商品不存在或者无存货"})


@app.route('/scan-return', methods=['POST'])
def scan_return():
    barcode = request.form['barcode']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()

    if product and product[0] > 0:
        new_quantity = product[0] + 1
        cursor.execute("UPDATE products SET quantity = ? WHERE barcode = ?", (new_quantity, barcode))
        conn.commit()

        # Log the action
        cursor.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                       ('Sold 1 item', barcode, datetime.now()))
        conn.commit()

        conn.close()
        return
    else:
        conn.close()
        return jsonify({"success": False, "message": "商品不存在或者无存货!"})



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
