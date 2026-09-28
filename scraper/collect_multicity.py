import csv
import os
import time
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OUTPUT_FILE = "multicity_raw.csv"

USER_AGENT = "BusinessListingsDashboard/1.0"

CITIES = [
    "Ahmedabad",
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Hyderabad",
    "Pune",
]

# OSM tags -> dashboard categories
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
    "hardware": "Hardware Store",
}


# ---------------------------------------------------------
# BUILD OVERPASS QUERY
# ---------------------------------------------------------

def build_query(city):

    return f"""
    [out:json][timeout:120];

    area["name"="{city}"]["boundary"="administrative"]->.searchArea;

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
# FETCH ONE CITY
# ---------------------------------------------------------

def fetch_city(city, max_retries=4):

    query = build_query(city)

    for attempt in range(1, max_retries + 1):

        print()
        print("=" * 60)
        print(f"Fetching: {city}")
        print(f"Attempt: {attempt}/{max_retries}")
        print("=" * 60)

        try:

            response = requests.post(
                OVERPASS_URL,
                data=query,
                headers={
                    "User-Agent": USER_AGENT
                },
                timeout=150
            )

            if response.status_code == 429:

                wait_time = 30 * attempt

                print(
                    f"Rate limited by Overpass. "
                    f"Waiting {wait_time} seconds..."
                )

                time.sleep(wait_time)
                continue

            response.raise_for_status()

            data = response.json()

            elements = data.get("elements", [])

            print(
                f"{city}: received {len(elements)} raw records"
            )

            return elements

        except requests.exceptions.Timeout:

            wait_time = 20 * attempt

            print(
                f"Request timed out. "
                f"Waiting {wait_time} seconds..."
            )

            time.sleep(wait_time)

        except requests.exceptions.RequestException as error:

            print(f"Request failed: {error}")

            if attempt < max_retries:

                wait_time = 20 * attempt

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

    print(f"FAILED: Could not collect {city}")

    return []


# ---------------------------------------------------------
# CATEGORY
# ---------------------------------------------------------

def get_category(tags):

    possible_categories = [
        tags.get("amenity"),
        tags.get("leisure"),
        tags.get("shop"),
        tags.get("tourism"),
    ]

    for category in possible_categories:

        if category in CATEGORY_MAP:
            return CATEGORY_MAP[category]

    return None


# ---------------------------------------------------------
# ADDRESS
# ---------------------------------------------------------

def build_address(tags):

    address_parts = []

    fields = [
        "addr:housenumber",
        "addr:street",
        "addr:suburb",
        "addr:neighbourhood",
        "addr:postcode",
    ]

    for field in fields:

        value = tags.get(field)

        if value:
            address_parts.append(value)

    return ", ".join(address_parts)


# ---------------------------------------------------------
# COORDINATES
# ---------------------------------------------------------

def get_coordinates(element):

    latitude = element.get("lat")
    longitude = element.get("lon")

    if latitude is None or longitude is None:

        center = element.get("center", {})

        latitude = center.get("lat")
        longitude = center.get("lon")

    return latitude, longitude


# ---------------------------------------------------------
# CLEAN ONE CITY
# ---------------------------------------------------------

def clean_records(raw_records, city):

    cleaned = []

    seen = set()

    for element in raw_records:

        tags = element.get("tags", {})

        name = tags.get("name")

        if not name:
            continue

        category = get_category(tags)

        if not category:
            continue

        address = build_address(tags)

        phone = (
            tags.get("phone")
            or tags.get("contact:phone")
            or ""
        )

        latitude, longitude = get_coordinates(element)

        if latitude is None or longitude is None:
            continue

        # Prefer the city's name from our query.
        final_city = city

        unique_key = (
            name.strip().lower(),
            address.strip().lower(),
            category.lower(),
            round(float(latitude), 5),
            round(float(longitude), 5),
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        cleaned.append({
            "business_name": name.strip(),
            "category": category,
            "city": final_city,
            "address": address.strip(),
            "phone": phone.strip(),
            "latitude": latitude,
            "longitude": longitude,
            "source": "OpenStreetMap",
        })

    return cleaned


# ---------------------------------------------------------
# SAVE PROGRESS
# ---------------------------------------------------------

def save_records(records):

    fields = [
        "business_name",
        "category",
        "city",
        "address",
        "phone",
        "latitude",
        "longitude",
        "source",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(records)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    all_records = []

    print()
    print("=" * 60)
    print("MULTI-CITY BUSINESS DATA COLLECTION")
    print("=" * 60)
    print()

    for index, city in enumerate(CITIES, start=1):

        print(
            f"\nCity {index}/{len(CITIES)}: {city}"
        )

        raw_records = fetch_city(city)

        city_records = clean_records(
            raw_records,
            city
        )

        print(
            f"{city}: {len(city_records)} clean records"
        )

        all_records.extend(city_records)

        # Save after every city.
        # If a later city fails, previous data is safe.
        save_records(all_records)

        print(
            f"Total collected so far: "
            f"{len(all_records)}"
        )

        # Be polite to the public API.
        if index < len(CITIES):

            print(
                "\nWaiting 15 seconds before next city..."
            )

            time.sleep(15)

    print()
    print("=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)

    print(
        f"Total raw cleaned records: {len(all_records)}"
    )

    # City summary
    city_counts = {}

    for record in all_records:

        city = record["city"]

        city_counts[city] = (
            city_counts.get(city, 0) + 1
        )

    print("\nCITY COUNTS:")

    for city in CITIES:

        print(
            f"  {city}: "
            f"{city_counts.get(city, 0)}"
        )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()