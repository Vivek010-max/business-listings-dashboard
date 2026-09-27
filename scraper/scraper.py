import requests
import csv

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# ---------------------------------------------------------
# 1. CATEGORY MAPPING
# ---------------------------------------------------------

CATEGORY_MAP = {
    "restaurant": "Restaurant",
    "cafe": "Cafe",
    "fast_food": "Fast Food",

    "hospital": "Hospital",
    "clinic": "Clinic",
    "dentist": "Dentist",
    "pharmacy": "Pharmacy",

    "bank": "Bank",
    "school": "School",

    "hotel": "Hotel",

    "fitness_centre": "Gym",

    "hairdresser": "Salon",
    "beauty": "Beauty",
    "cosmetics": "Cosmetics",

    "supermarket": "Supermarket",
    "convenience": "Convenience Store",
    "bakery": "Bakery",

    "clothes": "Clothing Store",
    "shoes": "Shoe Store",

    "electronics": "Electronics Store",
    "mobile_phone": "Mobile Phone Store",

    "jewelry": "Jewellery Store",
    "books": "Book Store",
    "hardware": "Hardware Store"
}


# ---------------------------------------------------------
# 2. OVERPASS QUERY
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# 3. FETCH DATA
# ---------------------------------------------------------

def fetch_data():

    print("Fetching business data from OpenStreetMap...")

    response = requests.post(
        OVERPASS_URL,
        data=query,
        headers={
            "User-Agent": "BusinessListingsDashboard/1.0"
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    print(f"Raw records received: {len(data['elements'])}")

    return data["elements"]


# ---------------------------------------------------------
# 4. BUILD ADDRESS
# ---------------------------------------------------------

def build_address(tags):

    address_parts = []

    fields = [
        "addr:housenumber",
        "addr:street",
        "addr:suburb",
        "addr:neighbourhood",
        "addr:postcode"
    ]

    for field in fields:

        value = tags.get(field)

        if value:
            address_parts.append(value)

    return ", ".join(address_parts)


# ---------------------------------------------------------
# 5. GET CATEGORY
# ---------------------------------------------------------

def get_category(tags):

    possible_categories = [
        tags.get("amenity"),
        tags.get("leisure"),
        tags.get("shop"),
        tags.get("tourism")
    ]

    for category in possible_categories:

        if category in CATEGORY_MAP:
            return CATEGORY_MAP[category]

    return None


# ---------------------------------------------------------
# 6. GET COORDINATES
# ---------------------------------------------------------

def get_coordinates(element):

    # Nodes
    latitude = element.get("lat")
    longitude = element.get("lon")

    # Ways / Relations
    if latitude is None or longitude is None:

        center = element.get("center", {})

        latitude = center.get("lat")
        longitude = center.get("lon")

    return latitude, longitude


# ---------------------------------------------------------
# 7. CLEAN RECORDS
# ---------------------------------------------------------

def clean_records(raw_records):

    cleaned = []

    seen = set()

    for element in raw_records:

        tags = element.get("tags", {})

        # -------------------------------------------------
        # Business name
        # -------------------------------------------------

        name = tags.get("name")

        if not name:
            continue

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        category = get_category(tags)

        if not category:
            continue

        # -------------------------------------------------
        # Address
        # -------------------------------------------------

        address = build_address(tags)

        # We require at least some address information
        if not address:
            continue

        # -------------------------------------------------
        # City
        # -------------------------------------------------

        city = tags.get("addr:city") or "Ahmedabad"

        # -------------------------------------------------
        # Phone
        # -------------------------------------------------

        phone = (
            tags.get("phone")
            or tags.get("contact:phone")
            or ""
        )

        # -------------------------------------------------
        # Coordinates
        # -------------------------------------------------

        latitude, longitude = get_coordinates(element)

        # -------------------------------------------------
        # Duplicate detection
        # -------------------------------------------------

        unique_key = (
            name.strip().lower(),
            address.strip().lower()
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        # -------------------------------------------------
        # Add cleaned record
        # -------------------------------------------------

        cleaned.append({
            "business_name": name.strip(),
            "category": category,
            "city": city.strip(),
            "address": address.strip(),
            "phone": phone.strip(),
            "latitude": latitude,
            "longitude": longitude,
            "source": "OpenStreetMap"
        })

    return cleaned


# ---------------------------------------------------------
# 8. SAVE CSV
# ---------------------------------------------------------

def save_csv(records):

    filename = "business_listings.csv"

    fields = [
        "business_name",
        "category",
        "city",
        "address",
        "phone",
        "latitude",
        "longitude",
        "source"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(records)

    print(f"\nCSV created successfully: {filename}")
    print(f"Final records: {len(records)}")


# ---------------------------------------------------------
# 9. MAIN
# ---------------------------------------------------------

def main():

    raw_records = fetch_data()

    cleaned_records = clean_records(raw_records)

    print(f"Clean records: {len(cleaned_records)}")

    save_csv(cleaned_records)


# ---------------------------------------------------------
# 10. RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()