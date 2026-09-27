import requests
from collections import Counter

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

query = """
[out:json][timeout:90];

area["name"="Ahmedabad"]["boundary"="administrative"]->.searchArea;

(
  nwr["amenity"="restaurant"](area.searchArea);
  nwr["amenity"="cafe"](area.searchArea);
  nwr["amenity"="fast_food"](area.searchArea);
  nwr["amenity"="hospital"](area.searchArea);
  nwr["amenity"="clinic"](area.searchArea);
  nwr["amenity"="dentist"](area.searchArea);
  nwr["amenity"="pharmacy"](area.searchArea);
  nwr["amenity"="bank"](area.searchArea);
  nwr["amenity"="school"](area.searchArea);

  nwr["tourism"="hotel"](area.searchArea);

  nwr["leisure"="fitness_centre"](area.searchArea);

  nwr["shop"="hairdresser"](area.searchArea);
  nwr["shop"="beauty"](area.searchArea);
  nwr["shop"="cosmetics"](area.searchArea);
  nwr["shop"="supermarket"](area.searchArea);
  nwr["shop"="convenience"](area.searchArea);
  nwr["shop"="bakery"](area.searchArea);
  nwr["shop"="clothes"](area.searchArea);
  nwr["shop"="shoes"](area.searchArea);
  nwr["shop"="electronics"](area.searchArea);
  nwr["shop"="mobile_phone"](area.searchArea);
  nwr["shop"="jewelry"](area.searchArea);
  nwr["shop"="books"](area.searchArea);
  nwr["shop"="hardware"](area.searchArea);
);

out center;
"""

print("Fetching data...")

response = requests.post(
    OVERPASS_URL,
    data=query,
    headers={
        "User-Agent": "BusinessListingsDashboard/1.0"
    },
    timeout=90
)

print("Status:", response.status_code)

response.raise_for_status()

data = response.json()
records = data["elements"]

print("\n========== DATA QUALITY REPORT ==========\n")

print("Total raw records:", len(records))

# Counters
named = 0
unnamed = 0
with_phone = 0
with_address = 0
with_city = 0

categories = Counter()

for element in records:

    tags = element.get("tags", {})

    # Name
    name = tags.get("name")

    if name:
        named += 1
    else:
        unnamed += 1

    # Phone
    phone = tags.get("phone") or tags.get("contact:phone")

    if phone:
        with_phone += 1

    # City
    city = tags.get("addr:city")

    if city:
        with_city += 1

    # Address
    address_fields = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb"),
        tags.get("addr:postcode"),
    ]

    if any(address_fields):
        with_address += 1

    # Category
    category = (
        tags.get("amenity")
        or tags.get("leisure")
        or tags.get("shop")
        or "unknown"
    )

    categories[category] += 1


print("Named businesses:", named)
print("Unnamed records:", unnamed)

print("\nPhone information:")
print("With phone:", with_phone)
print("Without phone:", len(records) - with_phone)

print("\nAddress information:")
print("With address:", with_address)
print("Without address:", len(records) - with_address)

print("\nCity information:")
print("With city:", with_city)
print("Without city:", len(records) - with_city)

print("\n========== CATEGORIES ==========\n")

for category, count in categories.most_common():
    print(f"{category:25} {count}")

print("\n================================")