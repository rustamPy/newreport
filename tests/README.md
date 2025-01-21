## Project Overview

This project implements a robust testing framework and database management system for handling university and student data. It provides various functionalities such as:
- Managing database tables for universities, students, subjects, exams, and grades.
- Implementing a `DatabaseManager` class for seamless database interactions.
- Generating comprehensive reports including student profiles, academic performance, and achievement plots using Python libraries such as `pytest`, `pandas`, `matplotlib`, and `xhtml2pdf`.

## Key Features

### Database Setup and Management
- Uses `sqlite3` for lightweight, file-based database management.
- Database schema includes interconnected tables for universities, students, subjects, exams, and grades.
- Populates tables with initial test data for unit testing and report generation.

### Testing Framework
- Utilizes `pytest` to define fixtures and perform unit tests.
- Covers various scenarios, such as:
  - Fetching university details.
  - Retrieving student data by ID.
  - Linking students to their universities and subjects.
  - Extracting grades and generating comprehensive grade reports.
- Ensures robust testing of both database interactions and report generation logic.

### Report Generation
- `ReportGenerator` class leverages `jinja2`, `xhtml2pdf`, and `matplotlib` to create:
  - PDF reports for student profiles.
  - Academic performance reports.
  - Visual plots of student achievements.
- Supports customization and asynchronous operations for efficient processing.

## File Structure

### Python Files
- `database.py`: Defines the `DatabaseManager` class for SQLite interactions.
- `report_generator.py`: Implements the `ReportGenerator` class for creating and exporting reports.
- `test_database.py`: Contains unit tests for database interactions.
- `test_report_generator.py`: Includes tests for report generation functionality.

### Testing Data
- `mock_db_manager`: A fixture that mocks database operations for testing without altering actual data.

### Example Test Cases
#### Database Tests
1. Verify connection establishment with `sqlite3.Connection`.
2. Fetch university details for a specific student.
3. Retrieve subjects and grades associated with a student.
4. List all students and their details.

#### Report Tests
1. Generate base64-encoded images for plots.
2. Validate PDF generation for student profiles.
3. Ensure correct data retrieval and formatting for academic performance reports.

## Getting Started

### Prerequisites
- Python 3.7+
- Install dependencies with:
  ```bash
  pip install -r requirements.txt
  ```

### Running Tests
1. Set up the database schema and initial data using the provided fixtures.
2. Run tests with:
  ```bash
  pytest
  ```

### Generating Reports
- Use the `ReportGenerator` class to:
  - Generate student profile reports.
  - Create academic performance summaries.
  - Visualize achievements with plots.

## Future Improvements
- Extend database schema for additional reporting needs.
- Enhance UI/UX for report generation and data visualization.
- Optimize report generation for larger datasets.

---
This project showcases the integration of Python, SQLite, and modern libraries to create a scalable and efficient reporting system, emphasizing robust testing and clear documentation.