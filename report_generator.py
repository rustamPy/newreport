import os
import matplotlib.pyplot as plt
import matplotlib
from typing import List
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io
import base64
import pandas as pd
from database import DatabaseManager
from datetime import datetime
import numpy as np

matplotlib.use('Agg')

class ReportGenerator:
    def __init__(self, db_manager):
        self.db_manager: DatabaseManager = db_manager
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        self.static_dir = 'static'

    def _save_plot_to_base64(self, plt=None, image = None):
        """
        Save matplotlib plot to base64 encoded image
        
        Args:
            plt (matplotlib.pyplot): Current plot
        
        Returns:
            str: Base64 encoded image
        """
        if image:
            return base64.b64encode(image).decode('utf-8')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _html_to_pdf(self, html_content, output_path):
        """Convert HTML to PDF"""
        with open(output_path, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        return pisa_status.err
    
    def _create_student_achievements_plots(self, grades_df: pd.DataFrame):
        """
        Generates a figure with multiple plots to visualize student achievements.
        Parameters:
        -----------
        grades_df : pd.DataFrame
            DataFrame containing student grades with columns 'SubjectName', 'StudentMarks', 'MaxMarks', and 'ExamDate'.
        Returns:
        --------
        fig : matplotlib.figure.Figure
            The generated figure containing the following subplots:
            - Bar chart comparing obtained and maximum marks by subject.
            - Line plot showing performance trend over time.
            - Radar chart displaying average marks distribution across subjects.
            - Pie chart representing overall achievement percentage.
        """
        fig = plt.figure(figsize=(15, 10))
        
        # Plot 1: Bar Chart
        ax1 = plt.subplot(221)
        subjects = grades_df['SubjectName'].unique()
        x = np.arange(len(subjects))
        width = 0.35
        ax1.bar(x - width/2, grades_df.groupby('SubjectName')['StudentMarks'].mean(), width, label='Obtained')
        ax1.bar(x + width/2, grades_df.groupby('SubjectName')['MaxMarks'].mean(), width, label='Maximum')
        ax1.set_xticks(x)
        ax1.set_xticklabels(subjects, rotation=45)
        ax1.set_title('Grades by Subject')
        ax1.legend()

        # Plot 2: Performance Trend
        ax2 = plt.subplot(222)
        grades_df['ExamDate'] = pd.to_datetime(grades_df['ExamDate'])
        grades_df.sort_values('ExamDate', inplace=True)
        ax2.plot(grades_df['ExamDate'], grades_df['StudentMarks']/grades_df['MaxMarks']*100, marker='o')
        ax2.set_title('Grade Performance Trend')
        ax2.set_ylabel('Achievement (%)')
        plt.xticks(rotation=45)

        # Plot 3: Radar Chart
        ax3 = plt.subplot(223, projection='polar')
        avg_marks = grades_df.groupby('SubjectName')['StudentMarks'].mean()
        angles = np.linspace(0, 2*np.pi, len(subjects), endpoint=False)
        values = avg_marks.values
        values = np.concatenate((values, [values[0]]))
        angles = np.concatenate((angles, [angles[0]]))
        ax3.plot(angles, values)
        ax3.fill(angles, values, alpha=0.25)
        ax3.set_xticks(angles[:-1])
        ax3.set_xticklabels(subjects)
        ax3.set_title('Subject Performance Distribution', pad=40)

        # Plot 4: Achievement Percentage
        ax4 = plt.subplot(224)
        achievement = (grades_df['StudentMarks']/grades_df['MaxMarks']*100).mean()
        colors = ['#ff9999' if achievement < 60 else '#66b3ff' if achievement < 80 else '#99ff99']
        ax4.pie([achievement, 100-achievement], colors=colors + ['#f0f0f0'],
                labels=[f'{achievement:.1f}%', ''], startangle=90)
        ax4.set_title('Overall Exam Achievement')

        plt.tight_layout()
        return fig

    # Generate Reports - 2 reports
    def generate_student_profile_report(self, student_id):
        """
        Generate a comprehensive student profile report.
        This method retrieves student details, performance data, and university details
        to generate a student profile report in PDF format.
        Args:
            student_id (int): The unique identifier of the student.
        Returns:
            str: The file path to the generated PDF report.
        """

        # Get student details
        student_details: pd.Series = self.db_manager.get_student_data_by_id(student_id)

        # Get subjects taken by students
        student_subjects: List = self.db_manager.get_subjects_per_student(student_id).to_dict("records")

        # Generate visualizations in the form of base64 encoded images
        grades_df: pd.DataFrame = self.db_manager.get_grades_per_student(student_id)
        general_achievements_base_64 = self._save_plot_to_base64(plt=self._create_student_achievements_plots(grades_df))

        # Get university details for branding
        university_details: pd.Series = self.db_manager.get_university_per_student(student_id)

        metadata = {
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'academic_year': student_details.AcademicYear,
            'general_achievements': f'data:image/png;base64,{general_achievements_base_64}',
            
            'university': {
                'logo_url': university_details.LogoURL,
                'name': university_details.UniversityName,
            },
            'student': {
                'id': student_id,
                'photo_url': student_details.ImageURL,
                'name': f'{student_details.FirstName} {student_details.LastName}',
                'dob': student_details.DateOfBirth,
                'email': student_details.Email,
                'subjects': student_subjects,
            }
        }
        
        # Render template
        template = self.template_env.get_template('student_individual_report.html')
        html_out = template.render(
            **metadata
        )

        # Generate PDF
        pdf_path = f'reports/student_{student_id}_profile.pdf'
        os.makedirs('reports', exist_ok=True)
        self._html_to_pdf(html_out, pdf_path)
        
        return pdf_path
    
    def generate_academic_performance_report(self):
        """Generate comprehensive academic performance report"""
        

        # Generate PDF
        pdf_path = 'reports/academic_performance_report.pdf'
        
        return pdf_path
