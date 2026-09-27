import csv
import re
from collections import Counter

FILE = "business_listings.csv"

records = []

with open(FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        records.append(row)


print("========== DATASET VALIDATION ==========\n")

print("Total records:", len(records))


# --------------------------------------------------
# Required fields
# --------------------------------------------------

required_fields = [
    "business_name",
    "category",
    "city",
    "address",
    "source"
]

print("\nMissing required fields:")

for field in required_fields:

    missing = sum(
        1 for row in records
        if not row[field].strip()
    )

    print(f"{field}: {missing}")


# --------------------------------------------------
# Address quality
# --------------------------------------------------

postcode_only = 0
proper_address = 0

for row in records:

    address = row["address"].strip()

    # Indian PIN code only
    if re.fullmatch(r"\d{6}", address):
        postcode_only += 1
    elif address:
        proper_address += 1


print("\nAddress quality:")
print("Proper address:", proper_address)
print("Postcode only:", postcode_only)


# --------------------------------------------------
# Phone numbers
# --------------------------------------------------

with_phone = sum(
    1 for row in records
    if row["phone"].strip()
)

print("\nPhone numbers:")
print("With phone:", with_phone)
print("Without phone:", len(records) - with_phone)


# --------------------------------------------------
# Duplicate detection
# --------------------------------------------------

keys = [
    (
        row["business_name"].strip().lower(),
        row["address"].strip().lower()
    )
    for row in records
]

duplicate_count = len(keys) - len(set(keys))

print("\nDuplicates:")
print("Duplicate records:", duplicate_count)


# --------------------------------------------------
# Category distribution
# --------------------------------------------------

categories = Counter(
    row["category"].strip()
    for row in records
)

print("\n========== CATEGORIES ==========\n")

for category, count in categories.most_common():

    print(f"{category:25} {count}")


# --------------------------------------------------
# Source distribution
# --------------------------------------------------

sources = Counter(
    row["source"].strip()
    for row in records
)

print("\n========== SOURCES ==========\n")

for source, count in sources.items():

    print(f"{source:25} {count}")


print("\n========================================")