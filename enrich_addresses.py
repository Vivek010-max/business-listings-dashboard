import csv
import os
import re
import time
import requests

INPUT_FILE = "business_listings.csv"
OUTPUT_FILE = "business_listings_enriched.csv"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

# IMPORTANT:
# Identify your application clearly.
USER_AGENT = "BusinessListingsDashboard/1.0"

# Nominatim policy requires no more than 1 request per second.
REQUEST_DELAY = 1.1


# ---------------------------------------------------------
# 1. CHECK IF ADDRESS NEEDS ENRICHMENT
# ---------------------------------------------------------

def is_postcode_only(address):
    """
    Returns True if the address is basically just a
    6-digit Indian postcode.
    """

    if not address:
        return True

    cleaned = address.strip()

    return bool(re.fullmatch(r"\d{6}", cleaned))


# ---------------------------------------------------------
# 2. REVERSE GEOCODE
# ---------------------------------------------------------

def reverse_geocode(latitude, longitude):

    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "addressdetails": 1,
        "zoom": 18
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    try:

        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=headers,
            timeout=30
        )

        if response.status_code == 429:
            print("Rate limited by Nominatim. Waiting 10 seconds...")
            time.sleep(10)
            return None

        response.raise_for_status()

        data = response.json()

        return data

    except requests.RequestException as e:

        print(f"Request failed: {e}")

        return None


# ---------------------------------------------------------
# 3. BUILD A CLEAN BUSINESS ADDRESS
# ---------------------------------------------------------

def build_address_from_nominatim(data):

    if not data:
        return None

    address = data.get("address", {})

    parts = []

    # House/building information
    for key in [
        "house_number",
        "building"
    ]:

        value = address.get(key)

        if value and value not in parts:
            parts.append(value)

    # Street
    for key in [
        "road",
        "pedestrian",
        "residential",
        "footway"
    ]:

        value = address.get(key)

        if value and value not in parts:
            parts.append(value)
            break

    # Locality
    for key in [
        "neighbourhood",
        "suburb",
        "quarter"
    ]:

        value = address.get(key)

        if value and value not in parts:
            parts.append(value)
            break

    # City
    city = (
        address.get("city")
        or address.get("town")
        or address.get("municipality")
    )

    if city and city not in parts:
        parts.append(city)

    # State
    state = address.get("state")

    if state and state not in parts:
        parts.append(state)

    # Postcode
    postcode = address.get("postcode")

    if postcode and postcode not in parts:
        parts.append(postcode)

    if not parts:
        return None

    return ", ".join(parts)


# ---------------------------------------------------------
# 4. DETERMINE ADDRESS PRECISION
# ---------------------------------------------------------

def determine_precision(address):

    if not address:
        return "unavailable"

    if is_postcode_only(address):
        return "postcode"

    return "street"


# ---------------------------------------------------------
# 5. LOAD CSV
# ---------------------------------------------------------

def load_records():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


# ---------------------------------------------------------
# 6. SAVE CSV
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
        "original_address",
        "address_precision"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(records)


# ---------------------------------------------------------
# 7. MAIN ENRICHMENT PROCESS
# ---------------------------------------------------------

def main():

    print("Loading business listings...")

    records = load_records()

    print(f"Total records: {len(records)}")

    # -----------------------------------------------------
    # Identify records needing enrichment
    # -----------------------------------------------------

    needs_enrichment = []

    for index, record in enumerate(records):

        if is_postcode_only(record["address"]):
            needs_enrichment.append(index)

    print(
        f"Records requiring reverse geocoding: "
        f"{len(needs_enrichment)}"
    )

    print(
        f"Records already having usable addresses: "
        f"{len(records) - len(needs_enrichment)}"
    )

    # -----------------------------------------------------
    # Resume support
    # -----------------------------------------------------

    # If an output file already exists, load it so we can
    # resume instead of starting again.

    if os.path.exists(OUTPUT_FILE):

        print("\nExisting enriched file found.")
        print("Loading previous progress...")

        enriched_records = load_records()

        if len(enriched_records) == len(records):

            records = enriched_records

            print("Previous progress loaded.")

    # -----------------------------------------------------
    # Process records
    # -----------------------------------------------------

    total = len(needs_enrichment)

    for position, index in enumerate(needs_enrichment, start=1):

        record = records[index]

        # Skip if already enriched
        if record.get("address_precision") == "street":
            continue

        latitude = record.get("latitude")
        longitude = record.get("longitude")

        print(
            f"\n[{position}/{total}] "
            f"{record['business_name']}"
        )

        print(
            f"Coordinates: {latitude}, {longitude}"
        )

        if not latitude or not longitude:

            print("Missing coordinates. Skipping.")

            record["original_address"] = record["address"]
            record["address_precision"] = "postcode"

            continue

        data = reverse_geocode(
            latitude,
            longitude
        )

        if data:

            new_address = build_address_from_nominatim(data)

            if new_address:

                print(
                    f"New address: {new_address}"
                )

                record["original_address"] = record["address"]

                record["address"] = new_address

                record["address_precision"] = (
                    determine_precision(new_address)
                )

            else:

                print("No usable address returned.")

                record["original_address"] = record["address"]

                record["address_precision"] = "postcode"

        else:

            print("Reverse geocoding failed.")

            record["original_address"] = record["address"]

            record["address_precision"] = "postcode"

        # -------------------------------------------------
        # SAVE AFTER EVERY REQUEST
        # -------------------------------------------------

        save_records(records)

        print("Progress saved.")

        # Respect Nominatim's rate limit
        time.sleep(REQUEST_DELAY)

    # -----------------------------------------------------
    # FINAL SAVE
    # -----------------------------------------------------

    save_records(records)

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    street_count = 0
    postcode_count = 0
    unavailable_count = 0

    for record in records:

        precision = record.get("address_precision")

        if precision == "street":
            street_count += 1

        elif precision == "postcode":
            postcode_count += 1

        else:
            unavailable_count += 1

    print("\n" + "=" * 60)
    print("ADDRESS ENRICHMENT COMPLETE")
    print("=" * 60)

    print(f"Total records:       {len(records)}")
    print(f"Street-level:        {street_count}")
    print(f"Postcode-level:      {postcode_count}")
    print(f"Unavailable:         {unavailable_count}")

    print(
        f"\nOutput file: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()