import csv
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

CSV_FILE = "../scraper/business_listings_final.csv"

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


def import_listings():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    query = """
        INSERT INTO listing_master
        (business_name, category, city, address, phone, source)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    records = []

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            phone = row["phone"].strip() if row["phone"] else None

            records.append((
                row["business_name"].strip(),
                row["category"].strip(),
                row["city"].strip(),
                row["address"].strip(),
                phone,
                row["source"].strip()
            ))

    cursor.executemany(query, records)
    connection.commit()

    print(f"Successfully imported {cursor.rowcount} listings.")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    import_listings()