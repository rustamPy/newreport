import os
import matplotlib.pyplot as plt
import matplotlib
from typing import List
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io
import base64
import requests
from io import BytesIO
from PIL import Image

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

    def _get_image_as_base64(self, image_url, default_image_path='static/default_student.png'):
        try:
            # Try to get image from URL
            response = requests.get(image_url)
            if response.status_code == 200:
                # Open image using PIL
                img = Image.open(BytesIO(response.content))
                
                # Resize image to reasonable dimensions for PDF
                img.thumbnail((300, 300))
                
                # Convert to RGB if necessary (in case of RGBA images)
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Save to bytes
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                
                # Convert to base64
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error processing image for URL {image_url}: {str(e)}")
            try:
                # Use default image if URL fails
                with open(default_image_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('utf-8')
            except Exception as e:
                print(f"Error loading default image: {str(e)}")
                return None
    
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

    def _generate_performance_trend_plot(self, ax2, all_grades_df):
        """
        Generate an enhanced performance trend plot with improved readability and styling.
        
        Parameters:
        ax2 (matplotlib.axes.Axes): The subplot axis to plot on
        all_grades_df (pd.DataFrame): DataFrame containing grade data with ExamDate column
        """
        # Convert ExamDate to datetime if not already
        all_grades_df['ExamDate'] = pd.to_datetime(all_grades_df['ExamDate'])
        
        # Calculate monthly averages
        monthly_avg = all_grades_df.groupby(all_grades_df['ExamDate'].dt.strftime('%Y-%m'))['percentage'].agg(['mean', 'std']).reset_index()
        monthly_avg.columns = ['date', 'mean', 'std']
        
        # Convert date strings to datetime for proper sorting
        monthly_avg['date'] = pd.to_datetime(monthly_avg['date'] + '-01')
        monthly_avg = monthly_avg.sort_values('date')
        
        # Create the line plot with enhanced styling
        line = ax2.plot(range(len(monthly_avg)), monthly_avg['mean'].values, 
                    marker='o', markersize=6, linewidth=2, 
                    color='#1f77b4', label='Monthly Average')
        
        # Add confidence interval
        ax2.fill_between(range(len(monthly_avg)),
                        monthly_avg['mean'] - monthly_avg['std'],
                        monthly_avg['mean'] + monthly_avg['std'],
                        alpha=0.2, color='#1f77b4',
                        label='±1 Standard Deviation')
        
        # Customize x-axis
        ax2.set_xticks(range(len(monthly_avg)))
        date_labels = monthly_avg['date'].dt.strftime('%b\n%Y')  # Split month and year into two lines
        ax2.set_xticklabels(date_labels, fontsize=8)
        
        # Add grid for better readability
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Customize y-axis
        ax2.set_ylabel('Average Percentage', fontsize=10)
        ax2.set_ylim(0, 100)  # Set y-axis from 0 to 100 for percentage
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}%'))
        
        # Add title with styling
        ax2.set_title('Average Performance Trend Over Time', 
                    fontsize=12, pad=15, fontweight='bold')
        
        # Add legend
        ax2.legend(loc='upper right', fontsize=8)
        
        # Add value labels on the points
        for i, value in enumerate(monthly_avg['mean']):
            ax2.annotate(f'{value:.1f}%', 
                        (i, value),
                        textcoords="offset points",
                        xytext=(0,10),
                        ha='center',
                        fontsize=8)
        
        # Adjust layout to prevent label cutoff
        ax2.margins(x=0.05)
        
        return ax2
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
        """
        Generate a comprehensive academic performance report across all students.
        
        Returns:
            str: The file path to the generated PDF report.
        """
        # Get overall academic statistics
        all_grades_df: pd.DataFrame = self.db_manager.get_all_grades()
        all_students_df: pd.DataFrame = self.db_manager.get_all_students()
        
        # Create performance visualizations
        fig = plt.figure(figsize=(15, 10))
        
        # Calculate percentages correctly for each exam
        all_grades_df['percentage'] = (all_grades_df['StudentMarks'] / all_grades_df['MaxMarks'] * 100)
        
        # Plot 1: Improved Overall Grade Distribution
        ax1 = plt.subplot(221)
        # Define grade ranges and labels
        grade_ranges = [(0, 40), (40, 60), (60, 75), (75, 90), (90, 100)]
        grade_labels = ['F (0-40)', 'D (40-60)', 'C (60-75)', 'B (75-90)', 'A (90-100)']
        
        # Calculate frequencies for each grade range
        grade_counts = []
        for low, high in grade_ranges:
            count = len(all_grades_df[(all_grades_df['percentage'] >= low) & 
                                    (all_grades_df['percentage'] < high)])
            grade_counts.append(count)
        
        # Create bar plot with improved styling
        bars = ax1.bar(grade_labels, grade_counts, color='skyblue', edgecolor='black')
        ax1.set_title('Grade Distribution', fontsize=12, pad=15)
        ax1.set_xlabel('Grade Ranges', fontsize=10)
        ax1.set_ylabel('Number of Students', fontsize=10)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        # Rotate x-labels for better readability
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Plot 2: Performance Trend Over Time
        ax2 = plt.subplot(222)
        ax2 = self._generate_performance_trend_plot(ax2, all_grades_df)
        
        # Plot 3: Subject-wise Performance
        ax3 = plt.subplot(223)
        subject_avg = all_grades_df.groupby('SubjectName')['percentage'].mean()
        subject_avg.plot(kind='bar', ax=ax3)
        ax3.set_title('Subject-wise Average Performance')
        ax3.set_xticklabels(subject_avg.index, rotation=45)
        ax3.set_ylabel('Average Percentage')
        
        # Plot 4: Department-wise Performance
        ax4 = plt.subplot(224)
        dept_avg = all_grades_df.groupby('Department')['percentage'].mean()
        dept_avg.plot(kind='pie', ax=ax4, autopct='%1.1f%%')
        ax4.set_title('Department-wise Performance Distribution')
        
        plt.tight_layout()
        performance_plots_base64 = self._save_plot_to_base64(plt)
        plt.close()
        
        # Calculate summary statistics
        total_students = len(all_students_df)
        avg_performance = all_grades_df['percentage'].mean()
        passing_students = len(all_grades_df[all_grades_df['percentage'] >= 40].groupby('StudentID'))
        top_performers = len(all_grades_df[all_grades_df['percentage'] >= 75].groupby('StudentID'))
        
        # Get top 3 performing students
        student_avg = all_grades_df.groupby('StudentID')['percentage'].mean().reset_index()
        top_3_ids = student_avg.nlargest(3, 'percentage')['StudentID'].tolist()

        top_3_students = []
        for student_id in top_3_ids:
            student_data = all_students_df[all_students_df['StudentID'] == student_id].iloc[0]
            student_grades = all_grades_df[all_grades_df['StudentID'] == student_id]
            avg_percentage = student_grades['percentage'].mean()
            
            # Get and process student image
            image_base64 = self._get_image_as_base64(
                student_data['ImageURL'],
                default_image_path='static/default_student.png'  # Provide path to your default image
            )
            
            top_3_students.append({
                'name': f"{student_data['FirstName']} {student_data['LastName']}",
                'average': f"{avg_percentage:.1f}%",
                'subjects': len(student_grades['SubjectName'].unique()),
                'top_subject': student_grades.loc[student_grades['percentage'].idxmax()]['SubjectName'],
                'image': image_base64  # Add the base64 encoded image
            })
                
        # Get university details
        university_details = self.db_manager.get_universities_details()
        
        # Prepare template data
        template_data = {
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'academic_year': '2024',
            'performance_data': f'data:image/png;base64,{performance_plots_base64}',
            'university': {
                'logo_url': university_details.LogoURL,
                'name': university_details.UniversityName,
            },
            'statistics': {
                'total_students': f"{total_students:,}",
                'average_performance': f"{avg_performance:.1f}%",
                'passing_students': f"{(passing_students/total_students*100):.1f}%",
                'top_performers': f"{(top_performers/total_students*100):.1f}%",
                'top_3_students': top_3_students,
                'departments': [{'Department': dept, 'percentage': avg} 
                            for dept, avg in dept_avg.items()],
                'subjects': [{'SubjectName': subj, 'percentage': avg} 
                            for subj, avg in subject_avg.items()]
            }
        }
        
        # Render template
        template = self.template_env.get_template('academic_performance_report.html')
        html_out = template.render(**template_data)
        
        # Generate PDF
        pdf_path = 'reports/academic_performance_report.pdf'
        os.makedirs('reports', exist_ok=True)
        print(html_out)
        self._html_to_pdf(html_out, pdf_path)
        
        return pdf_path