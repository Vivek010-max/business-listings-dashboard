import pandas as pd

INPUT_FILE = "multicity_raw.csv"
OUTPUT_FILE = "business_listings_final.csv"

CITIES = [
    "Ahmedabad",
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Pune"
]

TARGET_PER_CITY = 200

# Categories we want represented when enough real records exist
CATEGORY_PRIORITY = [
    "Restaurant",
    "Hospital",
    "Fast Food",
    "Bank",
    "School",
    "Clinic",
    "Cafe",
    "Clothing Store",
    "Pharmacy",
    "Hotel",
    "Supermarket",
    "Bakery",
    "Dentist",
    "Gym",
    "Electronics Store",
    "Shoe Store",
    "Mobile Phone Store",
    "Salon",
    "Beauty",
    "Jewellery Store",
    "Convenience Store",
    "Hardware Store",
    "Book Store",
    "Cosmetics"
]


def select_city_data(city_df):
    """
    Select approximately 200 genuine listings from one city.

    We first give each available category a chance to contribute
    listings, then fill remaining slots proportionally.
    """

    city_df = city_df.copy()

    # Remove duplicate businesses
    city_df = city_df.drop_duplicates(
        subset=["business_name", "address"],
        keep="first"
    )

    if len(city_df) <= TARGET_PER_CITY:
        return city_df

    selected_parts = []
    remaining = city_df.copy()

    # Give each category an initial allocation.
    # Maximum 12 listings per category in the first pass.
    INITIAL_PER_CATEGORY = 12

    for category in CATEGORY_PRIORITY:

        category_df = remaining[
            remaining["category"] == category
        ]

        if category_df.empty:
            continue

        take = min(INITIAL_PER_CATEGORY, len(category_df))

        selected = category_df.sample(
            n=take,
            random_state=42
        )

        selected_parts.append(selected)

        remaining = remaining.drop(selected.index)

    selected_count = sum(len(x) for x in selected_parts)
    remaining_needed = TARGET_PER_CITY - selected_count

    # Fill remaining slots from the records that were not selected.
    if remaining_needed > 0 and not remaining.empty:

        remaining_needed = min(
            remaining_needed,
            len(remaining)
        )

        additional = remaining.sample(
            n=remaining_needed,
            random_state=42
        )

        selected_parts.append(additional)

    result = pd.concat(
        selected_parts,
        ignore_index=True
    )

    # Safety limit
    result = result.head(TARGET_PER_CITY)

    return result


def main():

    print("Loading raw dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Raw records: {len(df)}")

    final_parts = []

    for city in CITIES:

        city_df = df[df["city"] == city].copy()

        print("\n" + "=" * 60)
        print(f"{city}")
        print("=" * 60)

        print(f"Available records: {len(city_df)}")

        if city_df.empty:
            print("WARNING: No records found.")
            continue

        selected = select_city_data(city_df)

        print(f"Selected records: {len(selected)}")

        print("\nCategory distribution:")

        print(
            selected["category"]
            .value_counts()
            .to_string()
        )

        final_parts.append(selected)

    if not final_parts:
        print("No data selected.")
        return

    final_df = pd.concat(
        final_parts,
        ignore_index=True
    )

    # Final cleanup
    final_df = final_df.drop_duplicates(
        subset=["business_name", "city", "address"],
        keep="first"
    )

    # Keep the important columns
    columns = [
        "business_name",
        "category",
        "city",
        "address",
        "phone",
        "latitude",
        "longitude",
        "source"
    ]

    final_df = final_df[columns]

    final_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("FINAL DATASET CREATED")
    print("=" * 60)

    print(f"Total records: {len(final_df)}")

    print("\nCITY COUNTS:")
    print(final_df["city"].value_counts().to_string())

    print("\nCATEGORY COUNTS:")
    print(final_df["category"].value_counts().to_string())

    print("\nCITY + CATEGORY:")
    print(
        pd.crosstab(
            final_df["city"],
            final_df["category"]
        ).to_string()
    )

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()