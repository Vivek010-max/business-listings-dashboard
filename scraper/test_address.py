import requests
from collections import Counter

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"
categories = [
    ("amenity", "restaurant"),
]

results = []

for key, value in categories:

    print(f"\nChecking {key}={value}...")

    query = f"""
    [out:json][timeout:40];

    area["name"="Ahmedabad"]["boundary"="administrative"]->.searchArea;

    nwr["{key}"="{value}"]["addr:street"](area.searchArea);

    out center;
    """

    try:

        response = requests.post(
            OVERPASS_URL,
            data=query,
            headers={
                "User-Agent": "BusinessListingsDashboard/1.0"
            },
            timeout=60
        )

        print("Status:", response.status_code)

        response.raise_for_status()

        data = response.json()

        records = data["elements"]

        named_records = [
            r for r in records
            if r.get("tags", {}).get("name")
        ]

        print("Usable named records:", len(named_records))

        results.extend(named_records)

    except Exception as e:

        print("ERROR:", e)


print("\n" + "=" * 50)
print("FINAL RESULTS")
print("=" * 50)

print("Total records:", len(results))

# Remove duplicates
unique = {}

for record in results:

    tags = record.get("tags", {})

    name = tags.get("name", "").strip().lower()
    street = tags.get("addr:street", "").strip().lower()

    key = (name, street)

    if key not in unique:
        unique[key] = record


print("Unique records:", len(unique))

print("\nCategory counts:")

counter = Counter()

for record in unique.values():

    tags = record.get("tags", {})

    category = (
        tags.get("amenity")
        or tags.get("shop")
        or tags.get("tourism")
        or tags.get("leisure")
        or "unknown"
    )

    counter[category] += 1


for category, count in counter.most_common():

    print(f"{category}: {count}")


print("\nFirst 20 records:")

for record in list(unique.values())[:20]:

    tags = record.get("tags", {})

    print({
        "name": tags.get("name"),
        "category": (
            tags.get("amenity")
            or tags.get("shop")
            or tags.get("tourism")
            or tags.get("leisure")
        ),
        "street": tags.get("addr:street"),
        "postcode": tags.get("addr:postcode"),
        "phone": tags.get("phone")
    })