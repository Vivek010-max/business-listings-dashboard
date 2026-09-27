from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from database import get_connection


app = FastAPI(
    title="Business Listings Dashboard API",
    description="FastAPI backend for the Business Listings Dashboard",
    version="1.0.0"
)


# --------------------------------------------------
# Request model for a business listing
# --------------------------------------------------

class Listing(BaseModel):
    business_name: str
    category: str
    city: str
    address: str
    phone: Optional[str] = None
    source: str


# --------------------------------------------------
# 1. BULK INSERT LISTINGS
# --------------------------------------------------

@app.post("/listings/bulk")
def insert_listings(listings: List[Listing]):

    if not listings:
        raise HTTPException(
            status_code=400,
            detail="No listings provided"
        )

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO listing_master
        (business_name, category, city, address, phone, source)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = [
        (
            listing.business_name,
            listing.category,
            listing.city,
            listing.address,
            listing.phone,
            listing.source
        )
        for listing in listings
    ]

    try:
        cursor.executemany(query, values)
        connection.commit()

        return {
            "message": "Listings inserted successfully",
            "inserted_count": cursor.rowcount
        }

    except Exception as e:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# 2. CITY-WISE COUNT
# --------------------------------------------------

@app.get("/dashboard/city")
def city_wise_count():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                city,
                COUNT(*) AS count
            FROM listing_master
            GROUP BY city
            ORDER BY count DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# 3. CATEGORY-WISE COUNT
# --------------------------------------------------

@app.get("/dashboard/category")
def category_wise_count():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                category,
                COUNT(*) AS count
            FROM listing_master
            GROUP BY category
            ORDER BY count DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# 4. SOURCE-WISE COUNT
# --------------------------------------------------

@app.get("/dashboard/source")
def source_wise_count():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                source,
                COUNT(*) AS count
            FROM listing_master
            GROUP BY source
            ORDER BY count DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()