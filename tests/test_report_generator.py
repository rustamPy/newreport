import pytest
import pandas as pd
import matplotlib.pyplot as plt
import base64
from report_generator import ReportGenerator
from unittest.mock import Mock, patch, mock_open

@pytest.fixture
def mock_db_manager():
    """Fixture to create a mock database manager"""
    mock_db = Mock()

    # Mock student data
    mock_db.get_student_data_by_id.return_value = pd.Series(
        {
            "FirstName": "John",
            "LastName": "Doe",
            "DateOfBirth": "2000-01-01",
            "Email": "john.doe@example.com",
            "ImageURL": "http://example.com/photo.jpg",
            "AcademicYear": "2025",
        }
    )

    # Mock subjects data
    mock_db.get_subjects_per_student.return_value = pd.DataFrame([
        {'SubjectName': 'Math', 'Credits': 3},
        {'SubjectName': 'Physics', 'Credits': 4}
    ])

    # Mock grades data
    mock_db.get_grades_per_student.return_value = pd.DataFrame(
        {
            "SubjectName": ["Math", "Physics"] * 2,
            "StudentMarks": [85, 90, 88, 92],
            "MaxMarks": [100, 100, 100, 100],
            "ExamDate": ["2025-01-01", "2025-01-02", "2025-02-01", "2025-02-02"],
        }
    )

    # Mock university data
    mock_db.get_university_per_student.return_value = pd.Series({
        'UniversityName': 'Test University',
        'LogoURL': 'http://example.com/logo.png'
    })

    # Mock all grades data
    mock_db.get_all_grades.return_value = pd.DataFrame(
        {
            "StudentID": [1, 2, 3, 1, 2, 3],
            "SubjectName": [
                "Math",
                "Physics",
                "Chemistry",
                "Math",
                "Physics",
                "Chemistry",
            ],
            "StudentMarks": [85, 90, 88, 75, 80, 78],
            "MaxMarks": [100, 100, 100, 100, 100, 100],
            "ExamDate": [
                "2025-01-01",
                "2025-01-02",
                "2025-01-03",
                "2025-02-01",
                "2025-02-02",
                "2025-02-03",
            ],
            "Department": [
                "Science",
                "Science",
                "Science",
                "Science",
                "Science",
                "Science",
            ],
        }
    )

    # Mock all students data
    mock_db.get_all_students.return_value = pd.DataFrame(
        {
            "StudentID": [1, 2, 3],
            "FirstName": ["John", "Jane", "Jim"],
            "LastName": ["Doe", "Smith", "Beam"],
            "ImageURL": [
                "http://example.com/photo1.jpg",
                "http://example.com/photo2.jpg",
                "http://example.com/photo3.jpg",
            ],
        }
    )

    # Mock university details
    mock_db.get_universities_details.return_value = pd.Series(
        {"UniversityName": "Test University", "LogoURL": "http://example.com/logo.png"}
    )

    return mock_db

@pytest.fixture
def report_generator(mock_db_manager):
    """Fixture to create a ReportGenerator instance with mocked dependencies"""
    with patch('jinja2.Environment') as mock_env:
        mock_template = Mock()
        mock_template.render.return_value = '<html>Test Template</html>'
        mock_env.return_value.get_template.return_value = mock_template
        
        return ReportGenerator(mock_db_manager)

def test_save_plot_to_base64_with_plt():
    """Test _save_plot_to_base64 method with matplotlib plot"""
    generator = ReportGenerator(Mock())
    
    # Create a simple plot
    plt.figure()
    plt.plot([1, 2, 3], [1, 2, 3])
    
    # Get base64 string
    result = generator._save_plot_to_base64(plt)
    
    assert isinstance(result, str)
    assert result.startswith('iVBOR') # Common PNG header in base64

def test_save_plot_to_base64_with_image():
    """Test _save_plot_to_base64 method with raw image data"""
    generator = ReportGenerator(Mock())
    
    # Create dummy image data
    image_data = b'test image data'
    result = generator._save_plot_to_base64(image=image_data)
    
    assert isinstance(result, str)
    assert result == base64.b64encode(image_data).decode('utf-8')

def test_html_to_pdf():
    """Test _html_to_pdf method"""
    generator = ReportGenerator(Mock())
    
    with patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
        mock_create_pdf.return_value.err = 0
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = generator._html_to_pdf('<html>Test</html>', 'test.pdf')
            
            mock_create_pdf.assert_called_once()
            mock_file.assert_called_once_with('test.pdf', 'w+b')
            assert result == 0

def test_create_student_achievements_plots():
    """Test _create_student_achievements_plots method"""
    generator = ReportGenerator(Mock())

    # Create test data
    grades_df = pd.DataFrame(
        {
            "SubjectName": ["Math", "Physics"] * 2,
            "StudentMarks": [85, 90, 88, 92],
            "MaxMarks": [100, 100, 100, 100],
            "ExamDate": ["2025-01-01", "2025-01-02", "2025-02-01", "2025-02-02"],
        }
    )

    fig = generator._create_student_achievements_plots(grades_df)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 4  # Should have 4 subplots

@pytest.mark.asyncio
async def test_generate_student_profile_report(report_generator, mock_db_manager):
    """Test generate_student_profile_report method"""
    with patch('os.makedirs') as mock_makedirs:
        with patch('builtins.open', mock_open()):
            with patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
                mock_create_pdf.return_value.err = 0

                result = report_generator.generate_student_profile_report(1)

                # Verify all database calls were made
                mock_db_manager.get_student_data_by_id.assert_called_once_with(1)
                mock_db_manager.get_subjects_per_student.assert_called_once_with(1)
                mock_db_manager.get_grades_per_student.assert_called_once_with(1)
                mock_db_manager.get_university_per_student.assert_called_once_with(1)

                # Verify PDF was created
                mock_makedirs.assert_called_once_with('reports', exist_ok=True)
                assert result == 'reports/student_1_profile.pdf'


def test_create_student_achievements_plots():
    """Test _create_student_achievements_plots method"""
    generator = ReportGenerator(Mock())

    # Create test data
    grades_df = pd.DataFrame(
        {
            "SubjectName": ["Math", "Physics"] * 2,
            "StudentMarks": [85, 90, 88, 92],
            "MaxMarks": [100, 100, 100, 100],
            "ExamDate": ["2025-01-01", "2025-01-02", "2025-02-01", "2025-02-02"],
        }
    )

    fig = generator._create_student_achievements_plots(grades_df)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 4  # Should have 4 subplots


@pytest.mark.asyncio
async def test_generate_academic_performance_report(report_generator, mock_db_manager):
    """Test generate_academic_performance_report method"""
    with patch('os.makedirs') as mock_makedirs:
        with patch('builtins.open', mock_open()):
            with patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
                mock_create_pdf.return_value.err = 0

                result = report_generator.generate_academic_performance_report()

                # Verify all database calls were made
                mock_db_manager.get_all_grades.assert_called_once()
                mock_db_manager.get_all_students.assert_called_once()
                mock_db_manager.get_universities_details.assert_called_once()

                # Verify PDF was created
                mock_makedirs.assert_called_once_with('reports', exist_ok=True)
                assert result == 'reports/academic_performance_report.pdf'
