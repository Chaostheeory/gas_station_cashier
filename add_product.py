

scan_barcode_prompt = "请扫描条形码："
input_product_name_prompt = "请输入产品名称"
input_sale_price_prompt = "请输入产品零售价"


def add_product():
    barcode = input(scan_barcode_prompt)
    name = input(input_product_name_prompt)
    price = input(input_sale_price_prompt)\
    # excute insert in sqlite
    # log

add_product()

