import csv
import random

from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)

OUTPUT_DIRECTORY = Path(__file__).parent / "generated"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


products = [
    ("P1001", "Wireless Mouse", "Accessories", "TechSource", 18.50, 20),
    ("P1002", "Mechanical Keyboard", "Accessories", "KeyWorks", 55.00, 15),
    ("P1003", "USB-C Dock", "Accessories", "TechSource", 72.00, 12),
    ("P1004", "USB-C Cable", "Accessories", "CableDirect", 8.50, 30),

    ("P2001", "27-inch Monitor", "Displays", "VisionTech", 185.00, 10),
    ("P2002", "34-inch Ultrawide Monitor", "Displays", "VisionTech", 370.00, 6),
    ("P2003", "Portable Monitor", "Displays", "DisplayPro", 135.00, 8),

    ("P3001", "Business Laptop", "Computers", "ComputeCorp", 720.00, 8),
    ("P3002", "Gaming Laptop", "Computers", "ComputeCorp", 1050.00, 5),
    ("P3003", "Mini PC", "Computers", "MicroSystems", 420.00, 7),

    ("P4001", "Webcam", "Peripherals", "VisionTech", 48.00, 15),
    ("P4002", "USB Headset", "Peripherals", "AudioWorks", 38.00, 18),
    ("P4003", "Conference Speaker", "Peripherals", "AudioWorks", 95.00, 8),

    ("P5001", "External SSD 1TB", "Storage", "DataStore", 68.00, 12),
    ("P5002", "External SSD 2TB", "Storage", "DataStore", 115.00, 8),
]


warehouses = [
    "San Jose",
    "Cartago",
    "Heredia"
]


transaction_types = [
    "RECEIPT",
    "SALE",
    "RETURN",
    "ADJUSTMENT"
]


# ---------------------------------------------------------
# Product catalog
# ---------------------------------------------------------

product_file = OUTPUT_DIRECTORY / "product_catalog.csv"

with product_file.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "product_id",
        "product_name",
        "category",
        "supplier",
        "unit_cost",
        "reorder_level"
    ])

    writer.writerows(products)


print(
    f"Created product_catalog.csv "
    f"with {len(products)} records."
)


# ---------------------------------------------------------
# Inventory transactions
# ---------------------------------------------------------

transaction_file = (
    OUTPUT_DIRECTORY /
    "inventory_transactions.csv"
)

start_date = datetime(2026, 8, 1, 8, 0, 0)

transactions = []


for transaction_number in range(1, 501):

    product = random.choice(products)

    transaction_type = random.choices(
        transaction_types,
        weights=[25, 55, 10, 10],
        k=1
    )[0]

    if transaction_type == "RECEIPT":
        quantity = random.randint(10, 50)

    elif transaction_type == "SALE":
        quantity = random.randint(1, 8)

    elif transaction_type == "RETURN":
        quantity = random.randint(1, 5)

    else:
        quantity = random.randint(-5, 5)

    transactions.append([
        f"TRX-{transaction_number:05d}",
        (
            start_date
            + timedelta(
                hours=random.randint(0, 1000),
                minutes=random.randint(0, 59)
            )
        ).isoformat(),
        product[0],
        random.choice(warehouses),
        transaction_type,
        quantity
    ])


# Intentional data-quality issues.

transactions[100][2] = None
transactions[200][5] = "INVALID"
transactions[300][3] = None
transactions[400][4] = "UNKNOWN"


with transaction_file.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "transaction_id",
        "transaction_timestamp",
        "product_id",
        "warehouse",
        "transaction_type",
        "quantity"
    ])

    writer.writerows(transactions)


print(
    f"Created inventory_transactions.csv "
    f"with {len(transactions)} records."
)

print("\nDataset generation completed.")
print(f"Output directory: {OUTPUT_DIRECTORY}")