import tkinter as tk
from tkinter import messagebox
import csv
import os


scan_barcode_prompt = "请扫描条形码："
input_product_name_prompt = "请输入产品名称"
input_sale_price_prompt = "请输入产品零售价"

# File where product data will be stored
PRODUCT_FILE = 'products.csv'

# Initialize product file if not exists
if not os.path.exists(PRODUCT_FILE):
    with open(PRODUCT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'name', 'price', 'quantity'])

# Function to read product data from the file
def read_products():
    products = {}
    with open(PRODUCT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products[row['barcode']] = {'name': row['name'], 'price': float(row['price']), 'quantity': int(row['quantity'])}
    return products

# Function to write product data to the file
def write_product(barcode, name, price, quantity):
    products = read_products()
    products[barcode] = {'name': name, 'price': price, 'quantity': quantity}
    with open(PRODUCT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'name', 'price', 'quantity'])
        for barcode, data in products.items():
            writer.writerow([barcode, data['name'], data['price'], data['quantity']])

# Function to add a product
def add_product():
    def submit():
        barcode = barcode_entry.get()
        name = name_entry.get()
        price = float(price_entry.get())
        quantity = 0  # Initially zero when adding a new product
        write_product(barcode, name, price, quantity)
        messagebox.showinfo('Success', 'Product added successfully!')
        add_product_window.destroy()

    add_product_window = tk.Toplevel(window)
    add_product_window.title("Add Product")

    tk.Label(add_product_window, text="Barcode:").grid(row=0, column=0)
    barcode_entry = tk.Entry(add_product_window)
    barcode_entry.grid(row=0, column=1)

    tk.Label(add_product_window, text="Name:").grid(row=1, column=0)
    name_entry = tk.Entry(add_product_window)
    name_entry.grid(row=1, column=1)

    tk.Label(add_product_window, text="Price:").grid(row=2, column=0)
    price_entry = tk.Entry(add_product_window)
    price_entry.grid(row=2, column=1)

    tk.Button(add_product_window, text="Submit", command=submit).grid(row=3, columnspan=2)

# Function to handle warehousing
def warehousing():
    def submit():
        barcode = barcode_entry.get()
        quantity = int(quantity_entry.get())
        products = read_products()

        if barcode in products:
            products[barcode]['quantity'] += quantity
            write_product(barcode, products[barcode]['name'], products[barcode]['price'], products[barcode]['quantity'])
            messagebox.showinfo('Success', 'Product quantity updated successfully!')
        else:
            messagebox.showerror('Error', 'Product not found!')
        warehousing_window.destroy()

    warehousing_window = tk.Toplevel(window)
    warehousing_window.title("Warehousing")

    tk.Label(warehousing_window, text="Barcode:").grid(row=0, column=0)
    barcode_entry = tk.Entry(warehousing_window)
    barcode_entry.grid(row=0, column=1)

    tk.Label(warehousing_window, text="Quantity:").grid(row=1, column=0)
    quantity_entry = tk.Entry(warehousing_window)
    quantity_entry.grid(row=1, column=1)

    tk.Button(warehousing_window, text="Submit", command=submit).grid(row=2, columnspan=2)

# Function to sell product
def sell_product():
    def submit():
        barcode = barcode_entry.get()
        quantity = int(quantity_entry.get())
        products = read_products()

        if barcode in products:
            if products[barcode]['quantity'] >= quantity:
                products[barcode]['quantity'] -= quantity
                write_product(barcode, products[barcode]['name'], products[barcode]['price'], products[barcode]['quantity'])
                messagebox.showinfo('Success', 'Product sold successfully!')
            else:
                messagebox.showerror('Error', 'Not enough quantity in stock!')
        else:
            messagebox.showerror('Error', 'Product not found!')
        sell_product_window.destroy()

    sell_product_window = tk.Toplevel(window)
    sell_product_window.title("Sell Product")

    tk.Label(sell_product_window, text="Barcode:").grid(row=0, column=0)
    barcode_entry = tk.Entry(sell_product_window)
    barcode_entry.grid(row=0, column=1)

    tk.Label(sell_product_window, text="Quantity:").grid(row=1, column=0)
    quantity_entry = tk.Entry(sell_product_window)
    quantity_entry.grid(row=1, column=1)

    tk.Button(sell_product_window, text="Submit", command=submit).grid(row=2, columnspan=2)

# Main window
window = tk.Tk()
window.title("Cashier System")
def add_product():
    add_product_window = tk.Toplevel(window)
    add_product_window.title("Add Product")

    barcode = input(scan_barcode_prompt)
    name = input(input_product_name_prompt)
    price = input(input_sale_price_prompt)\
    # excute insert in sqlite
    # log
tk.Button(window, text="Add Product", command=add_product).pack(pady=10)
tk.Button(window, text="Warehousing", command=warehousing).pack(pady=10)
tk.Button(window, text="Sell Product", command=sell_product).pack(pady=10)

window.mainloop()
