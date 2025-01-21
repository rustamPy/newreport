<img width="800" alt="image" src="https://github.com/user-attachments/assets/c952cbdf-0dd9-4ae4-b995-d74fc3265d5a" />


# Automated Reporting System (ARS) ![Logo](static/imgs/favicon.svg "Logo")

## Project Overview

The goal of this project is to design and implement an Automated Reporting System (ARS) capable of efficiently processing and analyzing data to generate insightful reports. The core database infrastructure for the ARS will utilize **SQLite**, a lightweight and self-contained database solution. SQLite is an ideal choice for local use, offering robust functionality to manage and query relational data without requiring complex server configurations.

The database will feature multiple interconnected tables to store various types of student-related data, such as:
- Names
- Surnames
- Dates of birth
- Other student-specific attributes

All data used in this project has been synthetically generated using artificial intelligence to ensure ethical usage. This means no real personal or sensitive information is involved.

## Key Features

The ARS will interact with the SQLite database using Python's `sqlite3` library, enabling seamless execution of SQL queries and data manipulations. The datasets generated will be used to produce various reports, including:

- **Average Marks Analysis**: Calculating average (mean) marks across different subjects or faculties.
- **Student Progress Reports**: Assessing individual academic success.
- **Comprehensive Student Reports**: Generating detailed, student-specific profiles highlighting academic performance.

The project will include a user-friendly UI that allows users to:
- Retrieve and download reports from the integrated SQLite database.
- Upload custom CSV datasets to generate reports based on user-provided data.

## Getting Started

### Prerequisites
1. Clone the repository:
   ```bash
   git clone https://github.com/rustamPy/newreport.git
   ```
2. Navigate to the project directory:
   ```bash
   cd <project-directory>
   ```
3. Install dependencies with:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Service
1. Run the main script:
   ```bash
   python main.py
   ```
2. Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```

### Running Tests
1. To run the test suite, simply execute:
   ```bash
   pytest
   ```