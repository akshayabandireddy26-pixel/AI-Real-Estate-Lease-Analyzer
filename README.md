# AI-Real-Estate-Lease-Analyzer

**Python, Streamlit, and Groq AI** technologies have been used in the creation of a web application powered by AI technology aimed at analyzing and evaluating different types of commercial lease agreements.

## Features

- **PDF Text Extraction:** PDF documents can be uploaded to extract descriptive texts of lease agreements.
- **Automatic Information Extraction:** landlord-tenant and other information concerning properties, as well as the specifics of rent and lease agreements, is extracted automatically.
- **Lease Analytics Dashboard:** a web page featuring the data regarding monthly rents, deposit amounts, total rent paid, and the information pertaining to annual escalations.
- **Annual Rent Calculations:** this function provides the data about the rent costs during the given year as well as the illustrative figures depicting the rent rate growth.
- **Lease Expiration Monitoring**: the application allows users to find out the remaining time till the expiry date of the lease.
- **AI Lease Assistant:** makes it possible for the users to obtain answers to all questions concerning leases.
- **AI Risk Analysis:** this function detects missed clauses and ambiguous key terms of the lease agreements.
- **Data Export to CSV:** the lease information can be downloaded after using the application for further processing and examination.

## Technical Stack
-Python
-Streamlit
-Pandas
-PyPDF
-Groq API
-python-dotenv

## Project Layout

AI-Real-Estate-Lease-Analyzer/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore

## Safety Measures

- **API keys are stored in the environment variables.
- **Files that are important, such as .env and Streamlit secrets, are not included in the project by utilizing the .gitignore mechanism.

## Project Information
-Name of Project: AI Real Estate Lease Analyzer
-Type of Project: AI-Powered Web Application
-Field of Work: AI | Real Estate | Document Analysis
-Educational Prototype Project
