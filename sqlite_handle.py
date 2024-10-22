import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('supermarket.db')

# Create a cursor object to execute SQL commands
cur = conn.cursor()

# Create the "product" table
cur.execute('''
CREATE TABLE IF NOT EXISTS product (
    name TEXT NOT NULL,
    sale_price REAL NOT NULL,
    barcode TEXT PRIMARY KEY,
    remain_in_stock INTEGER NOT NULL
)
''')

# Create the "cash_flow" table
cur.execute('''
CREATE TABLE IF NOT EXISTS cash_flow (
    time_stamp TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('buy', 'sell')),  -- Actions can be either 'buy' or 'sell'
    product_barcode TEXT NOT NULL,
    count INTEGER NOT NULL,
    FOREIGN KEY (product_barcode) REFERENCES product(barcode)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables have been created.")
