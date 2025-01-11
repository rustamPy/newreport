import sqlite3
from database import DatabaseManager
import pytest
import os
import pandas as pd

@pytest.fixture
def db_manager():
    db_path = "tests.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    manager = DatabaseManager(db_path=db_path, initialize=False)

    # Set up the database schema and initial data
    with manager.get_connection() as connection:

        cursor = connection.cursor()
        
        # Create tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS Universities (UniversityID INTEGER PRIMARY KEY, UniversityName TEXT, Address TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Students (StudentID INTEGER PRIMARY KEY, FirstName TEXT, LastName TEXT, UniversityID INTEGER, SubjectsTaken TEXT, Email TEXT, DateOfBirth Date, AcademicYear INTEGER, ImageURL TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Subjects (SubjectID INTEGER PRIMARY KEY, SubjectName TEXT, Department TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Exams (ExamID INTEGER PRIMARY KEY, SubjectID INTEGER, ExamName TEXT, ExamDate TEXT, MaximumMarks INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Grades (GradeID INTEGER PRIMARY KEY, StudentID INTEGER, ExamID INTEGER, MarksObtained INTEGER)''')

        # Insert initial data
        cursor.execute('''INSERT INTO Universities (UniversityID, UniversityName, Address) VALUES (1,"Test University","ABC")''')
        cursor.execute('''INSERT INTO Students (StudentID, FirstName, LastName, UniversityID, SubjectsTaken) VALUES (1,"Test","Student",1,"1")''')
        cursor.execute('''INSERT INTO Subjects (SubjectID, SubjectName, Department) VALUES (1, "Test Subject", "TestDepartment")''')
        cursor.execute('''INSERT INTO Exams (ExamID, SubjectID, ExamName, ExamDate, MaximumMarks) VALUES (1, 1, "Test Exam", "1999-01-01", 100)''')
        cursor.execute('''INSERT INTO Grades (GradeID, StudentID, ExamID, MarksObtained) VALUES (1, 1, 1, 80)''')
        
        connection.commit()

    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)

def test_get_connection(db_manager):
    connection = db_manager.get_connection()
    expected = sqlite3.Connection

    assert isinstance(connection, expected)
    connection.close()

def test_get_university_details(db_manager):
    details: pd.Series = db_manager.get_university_details(1)
    expected = pd.Series({
        'UniversityID': 1, 
        'UniversityName': 'Test University', 
        'Address': 'ABC'
        })

    assert details.equals(expected)

def test_get_student_data_by_id(db_manager):
    student_data: pd.Series = db_manager.get_student_data_by_id(1)
    expected = pd.Series({
        'StudentID': 1, 
        'FirstName': 'Test', 
        'LastName': 'Student', 
        'UniversityID': 1, 
        'SubjectsTaken': '1',
        'Email': None,
        'DateOfBirth': None,
        'AcademicYear': None,
        'ImageURL': None
        })
    
    assert student_data.equals(expected)

def test_get_university_per_student(db_manager):
    university_details: pd.Series = db_manager.get_university_per_student(1)
    expected = pd.Series({
        'UniversityID': 1, 
        'UniversityName': 'Test University', 
        'Address': 'ABC'
        })

    assert university_details.equals(expected)

def test_get_subjects_per_student(db_manager):
    subjects: pd.Series = db_manager.get_subjects_per_student(1)
    expected = pd.DataFrame({
        'SubjectID': [1], 
        'SubjectName': ['Test Subject'],
        'Department': 'TestDepartment'
        })

    assert subjects.equals(expected)

def test_get_grades_per_student(db_manager):
    grades: pd.Series = db_manager.get_grades_per_student(1)
    expected = pd.DataFrame({
        'SubjectName': ["Test Subject"],
        'ExamName': ["Test Exam"], 
        'ExamDate': ["1999-01-01"],
        'StudentMarks': [80],
        'MaxMarks': [100]
        })
    assert grades.equals(expected)
    
def test_get_all_grades(db_manager):
    all_grades: pd.DataFrame = db_manager.get_all_grades()
    expected = pd.DataFrame({
        'StudentID': [1],
        'SubjectName': ["Test Subject"],
        'Department': ["TestDepartment"],
        'StudentMarks': [80],
        'MaxMarks': [100],
        'ExamDate': ["1999-01-01"],
        'ExamName': ["Test Exam"]
    })
    
    assert all_grades.equals(expected)

def test_get_all_students(db_manager):
    all_students: pd.DataFrame = db_manager.get_all_students()
    expected = pd.DataFrame({
        'StudentID': [1],
        'FirstName': ["Test"],
        'LastName': ["Student"],
        'Email': [None],  # Assuming no email data in the test setup
        'DateOfBirth': [None],  # Assuming no date of birth data in the test setup
        'AcademicYear': [None],  # Assuming no academic year data in the test setup
        'ImageURL': [None],  # Assuming no image URL data in the test setup
        'UniversityID': [1],
        'SubjectsTaken': ["1"]
    })
    
    assert all_students.equals(expected)