import csv
import os

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
            products[row['barcode']] = {'name': row['name'], 'price': float(row['price']),
                                        'quantity': int(row['quantity'])}
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


# Function to add a product (command-line based)
def add_product():
    barcode = input("Enter product barcode: ")  # Prompt for barcode
    name = input("Enter product name: ")  # Prompt for product name
    while True:
        try:
            price = float(input("Enter product price: "))  # Prompt for product price
            break
        except ValueError:
            print("Invalid input. Please enter a valid price.")

    quantity = 0  # Initial quantity is zero
    write_product(barcode, name, price, quantity)
    print(
        f"Product '{name}' with barcode '{barcode}' has been added successfully with price {price} and quantity {quantity}.")


# Example usage:
if __name__ == "__main__":
    add_product()
