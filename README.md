![Logo](static/imgs/dfavicon.svg "Logo")

# Automated Reporting System (ARS)

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

## Development Plan

The following steps outline the systematic development of the ARS:

### 1. Define Scope and Objectives (4.1)
- Identify report types to generate (e.g., Student Progress Reports with graphs, academic performance summaries, risky performance detection).
- Document requirements and use cases for clarity and focus, with GitHub links to the documentation.

### 2. Design and Set Up the Database (4.2)
- Create a database schema with well-defined tables, relationships, and constraints.
- Populate the database with synthetic datasets.
- Ensure alignment between the database structure and reporting requirements.

### 3. Implement the Database Interaction Layer (4.3)
- Use Python's `sqlite3` library for database connections and operations.
- Implement and test functions for inserting, updating, and retrieving data.
- Ensure the interaction layer operates efficiently and handles data accurately.

### 4. Develop the Report Generation Process and API (4.4)
- Write Python scripts to compute metrics like averages, success rates, and other insights.
- Develop algorithms for detailed reports, including individual student profiles.
- Integrate APIs for both internal and external use.
- Validate computations for correctness and reliability.

### 5. Design the User Interface (4.5)
- Create an intuitive interface for report selection and generation.
- Include functionality to review tables on the homepage.
- Design the interface to function locally (e.g., `localhost:8000`).

### 6. Test and Validate the System (4.6)
- Conduct extensive testing to identify bugs, optimize performance, and validate report outputs.
- Perform user acceptance testing to gather feedback and refine the tool.
- Ensure the ARS meets its objectives and functions seamlessly.

## Project Objectives

By following this structured approach, the ARS will demonstrate:
- The potential of **SQLite**, **Python**, and **CSV** for efficient data analysis and reporting.
- A scalable, ethical, and cost-effective method for building versatile reporting tools.

## Let's Get Started

With the above roadmap, this project aims to deliver a fully functional and user-friendly ARS system that meets the specified objectives and highlights the power of lightweight database solutions.