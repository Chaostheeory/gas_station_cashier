from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


ADMIN_PASSWORD = "xmqjyz"  # Change to your actual password
SCAN_CURRENT_VAL = 0
SCAN_SUM_VAL = 0

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('supermarket.db')
    conn.row_factory = sqlite3.Row
    return conn


# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect('supermarket.db')
    return conn


@app.route('/update-product', methods=['POST'])
def update_product():
    barcode = request.form['barcode']
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']
    password = request.form['password']

    # Check if the entered password is correct
    if password != ADMIN_PASSWORD:
        return jsonify({'success': False, 'message': 'Incorrect password!'}), 403

    # Connect to the database
    conn = get_db_connection()

    # Check if the product exists
    product = conn.execute('SELECT * FROM products WHERE name = ?', (name,)).fetchone()

    if product:
        # Update the product if it exists
        conn.execute('UPDATE products SET barcode = ?, price = ?, quantity = ? WHERE name = ?',
                     (barcode, price, quantity, name))
        conn.commit()
        conn.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                       (f'更新商品：：名称：{name}, 零售价：{price}，数量：{quantity}，条码：{barcode}', barcode,
                        datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
        # jsonify({'success': True, 'message': 'Product updated successfully!'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': '商品不存在!'}), 404


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


        conn.execute('''CREATE TABLE IF NOT EXISTS accum_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT NOT NULL,
            items TEXT NOT NULL,
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

    cursor.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                   (f'添加商品：：名称：{name}, 零售价：{price}，数量：{quantity}，条码：{barcode}', barcode, datetime.now()))
    conn.commit()
    conn.close()

    flash('Product added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/accumulate', methods=['GET', 'POST'])
def accumulate():
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT SUM(quantity * price) AS total_product_sum FROM products;"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    print(f"accumulate: {result}")
    # cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
    conn.commit()

    cursor.execute("INSERT INTO accum_logs (asset, items, timestamp) VALUES (?, ?, ?)",
                   (result, "not yet", datetime.now()))
    conn.commit()
    conn.close()
    flash(f'累积时间：{datetime.now()}，累积资产金额：￥{result}!', 'success')
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

current_value, total_sum = 0, 0

# View logs of all accumulations
@app.route('/view_accume_logs')
def view_accume_logs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accum_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return render_template('accum_logs.html', logs=logs)


# @app.route('/scanner', methods=["GET", "POST"])
# def sell_scan(current_val=0, sum_val=0):
#     return render_template("scanner.html", current_val=current_val, sum_val=sum_val)


@app.route('/sell_get_price', methods=[ "POST"])
def sell_get_price():
    if request.method == "POST":
        barcode = int(request.json.get('barcode'))
        print(f"barcode: {barcode}")
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products WHERE barcode = ?", (barcode,))
        name = cursor.fetchone()
        conn.commit()
        conn.close()


        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
        product = cursor.fetchone()
        conn.commit()
        conn.close()

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT price FROM products WHERE barcode = ?", (barcode,))
        price = int(cursor.fetchone()[0])
        if product and product[0] > 0:
            new_quantity = product[0] - 1
            cursor.execute("UPDATE products SET quantity = ? WHERE barcode = ?", (new_quantity, barcode))
            conn.commit()
            # Log the action
            cursor.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                           ('Sold 1 item', barcode, datetime.now()))
            logs = cursor.fetchall()
            conn.commit()
        if price:
            print(f"!!price: {price}")
            return jsonify({'price': price, 'name': name[0]})
        else:
            return jsonify({'price': 0}), 404


@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/next-page')
def next_page():
    return render_template('next_page.html')

@app.route('/scanner_compute', methods=["GET", "POST"])
def sell_scan_compute():
    global SCAN_CURRENT_VAL, SCAN_SUM_VAL
    if request.method == "POST":
        entered_value = int(request.form["number"])
        current_value = SCAN_CURRENT_VAL
        total_sum = SCAN_SUM_VAL

        barcode = request.form['barcode']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
        product = cursor.fetchone()
        cursor.execute("SELECT price FROM products WHERE barcode = ?", (barcode,))
        price = int(cursor.fetchone())
        if product and product[0] > 0:
            new_quantity = product[0] - 1
            cursor.execute("UPDATE products SET quantity = ? WHERE barcode = ?", (new_quantity, barcode))
            conn.commit()
            # Log the action
            cursor.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                           ('Sold 1 item', barcode, datetime.now()))
            logs = cursor.fetchall()
            conn.commit()

        session["current_val"] = price
        session["sum_val"] = total_sum + price
        conn.close()
        flash(f"current: {entered_value}")
        flash(f"sum: {entered_value + sum}")
        total_sum += current_value
        # return render_template('test.html', current=current_value, sum=total_sum, logs=logs)
    return render_template("scanner.html", current=current_value, sum=total_sum)

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

@app.route('/accum_logs')
def view_accum_logs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accum_logs ORDER BY timestamp DESC")
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
                       ('售出 1 item', barcode, datetime.now()))
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

    if product:
        new_quantity = product[0] + 1
        cursor.execute("UPDATE products SET quantity = ? WHERE barcode = ?", (new_quantity, barcode))
        conn.commit()

        # Log the action
        cursor.execute("INSERT INTO logs (action, barcode, timestamp) VALUES (?, ?, ?)",
                       ('退货 1 item', barcode, datetime.now()))
        conn.commit()

        conn.close()
        return
    else:
        conn.close()
        return jsonify({"success": False, "message": "商品不存在"})



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
