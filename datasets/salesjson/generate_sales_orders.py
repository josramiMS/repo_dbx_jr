import json
import random

from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)

OUTPUT_DIRECTORY = Path(__file__).parent / "generated"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


products = [
    {
        "product_id": "P1001",
        "product_name": "Wireless Mouse",
        "category": "Accessories",
        "unit_price": 29.99,
    },
    {
        "product_id": "P1002",
        "product_name": "Mechanical Keyboard",
        "category": "Accessories",
        "unit_price": 89.99,
    },
    {
        "product_id": "P1003",
        "product_name": "USB-C Dock",
        "category": "Accessories",
        "unit_price": 119.99,
    },
    {
        "product_id": "P2001",
        "product_name": "27-inch Monitor",
        "category": "Displays",
        "unit_price": 299.99,
    },
    {
        "product_id": "P2002",
        "product_name": "34-inch Ultrawide Monitor",
        "category": "Displays",
        "unit_price": 549.99,
    },
    {
        "product_id": "P3001",
        "product_name": "Business Laptop",
        "category": "Computers",
        "unit_price": 1099.99,
    },
    {
        "product_id": "P3002",
        "product_name": "Gaming Laptop",
        "category": "Computers",
        "unit_price": 1599.99,
    },
]


locations = [
    ("Costa Rica", "San Jose"),
    ("Costa Rica", "Cartago"),
    ("Costa Rica", "Heredia"),
    ("United States", "Miami"),
    ("United States", "Austin"),
    ("Mexico", "Mexico City"),
    ("Colombia", "Bogota"),
]


payment_methods = [
    "Credit Card",
    "Debit Card",
    "PayPal",
    "Bank Transfer",
]


statuses = [
    "Completed",
    "Processing",
    "Shipped",
    "Cancelled",
]


shipping_priorities = [
    "Standard",
    "Express",
    "Urgent",
]


start_date = datetime(2026, 9, 1, 8, 0, 0)

order_counter = 1


for file_number in range(1, 16):

    records = []

    for _ in range(10):

        product = random.choice(products)
        country, city = random.choice(locations)

        order = {
            "order_id": f"ORD-{order_counter:05d}",
            "customer_id": f"CUST-{random.randint(1, 40):04d}",
            "order_timestamp": (
                start_date
                + timedelta(
                    hours=random.randint(0, 450),
                    minutes=random.randint(0, 59),
                )
            ).isoformat(),
            "country": country,
            "city": city,
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "quantity": random.randint(1, 5),
            "unit_price": product["unit_price"],
            "discount": round(
                random.choice(
                    [0.0, 0.05, 0.10, 0.15, 0.20]
                ),
                2,
            ),
            "payment_method": random.choice(payment_methods),
            "status": random.choice(statuses),
        }

        # Introduce schema evolution in the final five files.
        if file_number >= 11:
            order["shipping_priority"] = random.choice(
                shipping_priorities
            )

        records.append(order)

        order_counter += 1

    # Introduce a few business-quality issues.
    if file_number == 7:
        records[2]["quantity"] = 0

    if file_number == 8:
        records[4]["unit_price"] = -25.00

    if file_number == 9:
        records[6]["discount"] = 1.25

    if file_number == 10:
        records[8]["customer_id"] = None

    output_file = (
        OUTPUT_DIRECTORY
        / f"orders_{file_number:03d}.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:
            file.write(json.dumps(record) + "\n")

    print(
        f"Created {output_file.name}: "
        f"{len(records)} records"
    )


print("\nDataset generation completed.")
print(f"Output directory: {OUTPUT_DIRECTORY}")