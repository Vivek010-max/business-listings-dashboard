\# Business Listings Dashboard



A full-stack business listings dashboard built using React.js, FastAPI, MySQL, and Python-based data collection.



The application collects real business listings from OpenStreetMap, processes and validates the data, stores it in MySQL, exposes analytical APIs through FastAPI, and visualizes the results through an interactive React dashboard.



\---



\## Project Overview



The Business Listings Dashboard provides city-wise, category-wise, and source-wise analysis of business listings collected from OpenStreetMap.



\### Final Dataset



\- \*\*13,250 unique business listings\*\*

\- \*\*5 cities\*\*

&#x20; - Ahmedabad

&#x20; - Mumbai

&#x20; - Delhi

&#x20; - Bengaluru

&#x20; - Pune

\- \*\*24 business categories\*\*

\- \*\*Source:\*\* OpenStreetMap

\- Records without an available address were excluded.

\- Duplicate business listings were removed.

\- Phone numbers are included when available.



\---



\## Features



\### Data Collection



\- Collects business listings using the OpenStreetMap Overpass API.

\- Supports multiple cities.

\- Collects businesses across multiple categories.

\- Extracts:

&#x20; - Business name

&#x20; - Category

&#x20; - City

&#x20; - Address

&#x20; - Phone

&#x20; - Latitude

&#x20; - Longitude

&#x20; - Source



\### Backend



\- REST API built with FastAPI.

\- MySQL database integration.

\- Bulk listing insertion.

\- City-wise business counts.

\- Category-wise business counts.

\- Source-wise business counts.

\- CORS enabled for the React frontend.



\### Frontend



\- React.js dashboard.

\- Recharts-based data visualizations.

\- KPI cards.

\- City-wise analysis.

\- Category-wise analysis.

\- Source-wise analysis.

\- Loading and error states.

\- Responsive dashboard interface.



\---



\## Architecture



```text

OpenStreetMap

&#x20;     |

&#x20;     v

Overpass API

&#x20;     |

&#x20;     v

Python Data Collection

&#x20;     |

&#x20;     v

CSV Dataset

&#x20;     |

&#x20;     v

Data Cleaning \& Validation

&#x20;     |

&#x20;     v

MySQL Database

&#x20;     |

&#x20;     v

FastAPI REST API

&#x20;     |

&#x20;     v

React Dashboard

Technology Stack

Frontend

React.js

Vite

Recharts

CSS

Backend

Python

FastAPI

Pydantic

Uvicorn

MySQL Connector

python-dotenv

Database

MySQL 8

Data Collection

Python

Requests

OpenStreetMap

Overpass API

Development Tools

Visual Studio Code

Git

GitHub

Data Collection



The data collection process uses the OpenStreetMap Overpass API.



The scraper collects businesses from five Indian cities:



Ahmedabad

Mumbai

Delhi

Bengaluru

Pune



The collection process covers categories such as:



Restaurants

Hospitals

Clinics

Fast Food

Banks

Schools

Cafes

Pharmacies

Hotels

Supermarkets

Clothing Stores

Bakeries

Dentists

Gyms

Electronics Stores

Mobile Phone Stores

Shoe Stores

Jewellery Stores

Salons

Beauty

Hardware Stores

Book Stores

Convenience Stores

Cosmetics



The initial collection produced 41,538 records.



During validation, records without an available address were excluded and duplicate records were removed.



The final dataset contains 13,250 unique listings.



Data Quality



The final dataset was validated for the required fields.



Field	Validation

Business Name	No missing values

Category	No missing values

City	No missing values

Address	No missing values

Source	No missing values

Duplicate businesses	0

Phone	Included when available



Phone numbers were not required for every listing because they were collected only when available in the source data.



Final City Distribution

City	Listings

Bengaluru	5,118

Pune	2,572

Mumbai	2,394

Delhi	2,235

Ahmedabad	991

Total	13,250

API Endpoints



The FastAPI backend provides the following endpoints.



Bulk Insert

POST /listings/bulk



Used to insert multiple business listings into the database.



City-wise Report

GET /dashboard/city



Returns the number of listings grouped by city.



Category-wise Report

GET /dashboard/category



Returns the number of listings grouped by business category.



Source-wise Report

GET /dashboard/source



Returns the number of listings grouped by data source.



Database



The application uses MySQL with the following database:



business\_dashboard



Main table:



listing\_master

Table Structure

Column	Type

id	INT

business\_name	VARCHAR

category	VARCHAR

city	VARCHAR

address	VARCHAR

phone	VARCHAR

source	VARCHAR

created\_at	TIMESTAMP



A database dump is included in:



database/business\_dashboard.sql

Project Structure

business-listings-dashboard/

│

├── frontend/

│   ├── src/

│   │   ├── components/

│   │   │   ├── Dashboard.jsx

│   │   │   └── dashboard.css

│   │   ├── App.jsx

│   │   ├── api.js

│   │   ├── index.css

│   │   └── main.jsx

│   ├── package.json

│   └── ...

│

├── backend/

│   ├── main.py

│   ├── database.py

│   ├── import\_data.py

│   └── requirements.txt

│

├── scraper/

│   ├── collect\_multicity.py

│   ├── create\_final\_dataset.py

│   └── business\_listings\_final.csv

│

├── database/

│   └── business\_dashboard.sql

│

├── README.md

└── .gitignore

Setup Instructions

Prerequisites



Install the following:



Python 3

Node.js

MySQL 8

Git

Backend Setup



Navigate to the project directory:



cd "Bussiness listing full stack"



Create a Python virtual environment:



python -m venv .venv



Activate it on Windows:



.\\.venv\\Scripts\\Activate.ps1



Install backend dependencies:



pip install -r backend/requirements.txt

Environment Variables



Create:



backend/.env



with the MySQL configuration:



DB\_HOST=localhost

DB\_USER=root

DB\_PASSWORD=your\_mysql\_password

DB\_NAME=business\_dashboard



Do not commit .env to GitHub.



Database Setup



Create the database and table using the provided SQL dump:



database/business\_dashboard.sql



The SQL dump contains the final database structure and dataset.



Alternatively, the database can be created manually according to the backend configuration.



Importing the Dataset



The final dataset is located at:



scraper/business\_listings\_final.csv



Run the importer from the backend directory:



cd backend

python import\_data.py

Running the Backend



From the backend directory:



uvicorn main:app --reload



The API will be available at:



http://127.0.0.1:8000



FastAPI interactive documentation:



http://127.0.0.1:8000/docs

Frontend Setup



Open a new terminal and navigate to:



cd frontend



Install dependencies:



npm install



Start the development server:



npm run dev



The frontend will normally be available at:



http://localhost:5173



The frontend communicates with the FastAPI backend to retrieve dashboard statistics.



Dashboard Reports



The dashboard provides three main analytical views:



City-wise



Shows the number of business listings available in each city.



Category-wise



Shows the distribution of businesses across different categories.



Source-wise



Shows the number of listings collected from each source.



The dashboard also provides summary metrics including:



Total listings

Number of cities

Number of categories

Number of sources

Challenges Faced

1\. Overpass API Timeouts



Large OpenStreetMap queries can take significant time and may occasionally result in timeouts or rate limiting.



The scraper therefore processes cities separately and includes retry handling.



2\. Different Data Availability Across Cities



The number of businesses available in OpenStreetMap differs significantly between cities.



The final dataset therefore reflects the records that passed the address and duplicate validation rather than artificially generating or fabricating listings.



3\. Missing Addresses



A significant portion of the initially collected records did not contain an address.



Rather than inserting incomplete records into the final database, those records were excluded from the final validated dataset.



4\. Duplicate Listings



Duplicate businesses were identified using business name, city, and address and removed before creating the final dataset.



5\. Large Dataset Processing



The initial collection contained more than 41,000 records. The data was cleaned and validated before being imported into MySQL.



Data Source and Attribution



Business listing data was collected from OpenStreetMap through the Overpass API.



OpenStreetMap data is provided under the Open Database License (ODbL).



OpenStreetMap contributors should be credited when using the data.



Future Improvements



Possible future improvements include:



Adding more data sources.

Adding search and filtering functionality.

Adding pagination for business listings.

Adding detailed business-level pages.

Adding map-based visualization.

Adding authentication and user management.

Deploying the frontend, backend, and database to cloud infrastructure.

Adding scheduled data updates.

License



This project was developed as a technical assignment and demonstration project.

