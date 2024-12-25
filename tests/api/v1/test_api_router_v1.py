from fastapi.testclient import TestClient
from main import app
import os
import pytest

CLIENT = TestClient(app)
STUDENT_ID = 17915
TABLE_PARAMS = [
    # (table name, expected columns_count, primary key)
    ("students", 9, 'StudentID'),  
    ("subjects", 3, 'SubjectID'),
    ("exams", 7, 'ExamID'),
    ("universities", 5, 'UniversityID'),
    ("grades", 4, 'GradeID')
]

def test_api_health_check():
    """
    Test the API health check endpoint.

    This test sends a GET request to the specified API endpoint and asserts that the response status code is 200.

    Raises:
        AssertionError: If the response status code is not 200.
    """
    response = CLIENT.get("/health")
    assert response.status_code == 200

def test_api_connection():
    """
    Test the API connection to the student profile endpoint.

    This test sends a GET request to the specified API endpoint and asserts that the response status code is 200.

    Raises:
        AssertionError: If the response status code is not 200.
    """
    response = CLIENT.get(f"/api/v1/reports/student-profile/{STUDENT_ID}")
    assert response.status_code == 200

def test_file_creation():
    """
    Test the creation of a student profile report file.

    This test ensures that the API connection test passes first, and then
    checks if the file for the student profile report is created successfully.

    Steps:
    1. Call the `test_api_connection` function to ensure the API connection is working.
    2. Define the expected file path for the student profile report.
    3. Assert that the file exists at the specified path.

    Raises:
        AssertionError: If the file does not exist at the specified path.
    """
    test_api_connection()
    file_path = f"reports/student_{STUDENT_ID}_profile.pdf"
    assert os.path.isfile(file_path)

@pytest.mark.parametrize("table, expected_columns_count, primary_key", TABLE_PARAMS)
def test_table_data(table, expected_columns_count, primary_key):
    """
    Test the retrieval of data from all tables.

    This test sends a GET request to the specified API endpoint and asserts that the response status code is 200.

    Raises:
        AssertionError: If the response status code is not 200.
    """
    response = CLIENT.get(f"/api/v1/table/{table}")
    data = response.json()

    assert response.status_code == 200
    # The table should have at least one row
    assert len(data) > 0

    # The table should have the expected number of columns
    assert len(data[0]) == expected_columns_count

    # The first column should be the primary key
    assert data[0].get(primary_key) is not None

    """
    Test the retrieval of the grades table.

    This test sends a GET request to the specified API endpoint and asserts that the response status code is 200.

    Raises:
        AssertionError: If the response status code is not 200.
    """
    table = "grades"
    response = CLIENT.get(f"/api/v1/table/{table}")
    data = response.json()

    # The table should have at least one grade and 4 columns
    assert len(data) > 0
    assert len(data[0]) == 4