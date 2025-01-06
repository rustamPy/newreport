import sqlite3
import pandas as pd
import os
from utils import ID_TO_TABLE, TABLE_TO_ID


class DatabaseManager:
    def __init__(self, db_path='academic_database.db', csv_dir='assets/', initialize=True):
        self.db_path = db_path
        self.csv_dir = csv_dir
        self.data_type_map = {
            'ExamDate': 'DATE',
            'DateOfBirth': 'DATE',
            'Date': 'DATE',

        }
        if initialize:
            self.initialize_database()
    def get_connection(self):
        """
        Returns a database connection that remains open.
        Caller is responsible for closing the connection.
        """
        return sqlite3.connect(self.db_path)

    def infer_data_type(self, column):
        """Infer SQLite data type from pandas data type"""
        return self.data_type_map.get(column, 'TEXT')

    def create_table_from_csv(self, csv_path, table_name):
        """Create a table dynamically from the structure of a CSV file with foreign keys"""
        df = pd.read_csv(csv_path)
        columns = df.columns

        # Build the CREATE TABLE statement
        create_statement = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        create_statement += f"{columns[0]} INTEGER PRIMARY KEY, "

        for column in columns[1:]:
            column_type = self.infer_data_type(column)
            create_statement += f"{column} {column_type}, "


        create_statement = create_statement.rstrip(', ') + ')'

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_statement)
            conn.commit()

    def import_data_from_csv(self, csv_path, table_name):
        """Import data into the table from the CSV file"""
        df = pd.read_csv(csv_path)
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)

    def initialize_database(self):
        """Initialize database by creating tables and importing data"""
        for file_name in os.listdir(self.csv_dir):
            if file_name.endswith('.csv'):
                table_name = os.path.splitext(file_name)[0]  # Use file name (without extension) as table name
                csv_path = os.path.join(self.csv_dir, file_name)

                self.create_table_from_csv(csv_path, table_name)
                self.import_data_from_csv(csv_path, table_name)

    def _get_table_data(self, table_name: str, limit = 100, id = None):
        """Retrieve data from specified table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if id:
                    query = f'select * from {table_name} where {TABLE_TO_ID[table_name]} = {int(id)}  LIMIT {limit}'
                else:
                    query = f'select * from {table_name} LIMIT {limit}'
                return pd.read_sql(query, conn).to_dict('records')
        except Exception as e:
            raise e

    def import_csv(self, df: pd.DataFrame):
        """Import data from CSV file with enhanced structure"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing data before importing
            table_to_clear = ID_TO_TABLE.get(df.columns[0], None)

            if table_to_clear:
                conn.execute(f'DELETE FROM {table_to_clear}')

            existing_table_columns = self._get_table_data(table_to_clear, limit=1)[0].keys() if table_to_clear else []
            importing_table_columns = df.columns

            assert set(existing_table_columns) == set(importing_table_columns), 'Columns do not match. Please review the input CSV once again.'

            # Import Grades
            if 'GradeID' in df.columns:
                grades_df = df[['FirstName', 'LastName', 'SubjectName', 'ExamName', 'MarksObtained']]

                # Join to get StudentID and ExamID
                grades_df = grades_df.merge(
                    conn.execute('SELECT StudentID, FirstName, LastName FROM Students').fetchdf(), 
                    on=['FirstName', 'LastName']
                )
                grades_df = grades_df.merge(
                    conn.execute('SELECT ExamID, SubjectName, ExamName FROM Exams').fetchdf(), 
                    on=['SubjectName', 'ExamName']
                )
                
                grades_df.to_sql('Grades', conn, if_exists='append', index=False)
            
            elif 'ID' in df.columns[0]:
                importing_df = df[importing_table_columns].drop_duplicates()
                importing_df.to_sql(table_to_clear, conn, if_exists='append', index=False)
            
            conn.commit()

    # TESTED
    def get_student_data_by_id(self, student_id) -> pd.DataFrame:
        """
        Retrieve student data by ID.

        Args:
            student_id (int): The ID of the student whose data is to be retrieved.
            

        Returns:
            pandas.Series: A series containing the student data for the given ID.

        Raises:
        IndexError: If no student data is found for the given ID.
        """
        student_data_sql = '''
        select * from Students s
        where s.StudentID = ?
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(student_data_sql, conn, params=(student_id,)).iloc[0]

    # TESTED
    def get_university_per_student(self, student_id) -> pd.Series:
        """
        Retrieve the university details for a given student ID.

        Args:
            student_id (int): The ID of the student whose university details are to be retrieved.

        Returns:
            pandas.Series: A pandas Series containing the university details for the specified student.

        Raises:
            IndexError: If no university details are found for the given student ID.
        """
        university_per_student_sql = '''
        select * from Universities u

        where u.UniversityID in (
            select UniversityID 
            from Students s 
            where s.StudentID = ?
        )
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(university_per_student_sql, conn, params=(student_id,)).iloc[0]
    
    # TESTED
    def get_subjects_per_student(self, student_id) -> pd.DataFrame:
        """
        Retrieve the subjects for a given student ID.

        Args:
            student_id (int): The ID of the student whose subjects are to be retrieved.
            
        Returns:
            pandas.Series: A Series containing the subjects for the specified student.
        """
        subjects_per_student_sql = '''
        WITH split_subjects AS (
            SELECT CAST(TRIM(value) AS INTEGER) as subject_id
            FROM 
                Students,
                json_each('["' || REPLACE(SubjectsTaken, ',', '","') || '"]')
            WHERE StudentID = ?
            )
        SELECT *
        FROM Subjects
        WHERE SubjectID IN (SELECT subject_id FROM split_subjects);
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(subjects_per_student_sql, conn, params=(student_id,))

    # TESTED
    def get_university_details(self, university_id) -> pd.Series:
        """
        Retrieve university details for branding.
        Args:
            university_id (int): The ID of the university to retrieve details for.
        Returns:
            pd.Series: A pandas Series containing the details of the university.
        Raises:
            IndexError: If the university with the given ID does not exist.
        """
        university_query = '''
        SELECT * FROM Universities 
        WHERE UniversityID = ?
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(university_query, conn, params=(university_id,)).iloc[0]
    
    # TESTED
    def get_grades_per_student(self, student_id) -> pd.DataFrame:
        """
        Retrieve the grades for a given student ID.

        Args:
            student_id (int): The ID of the student whose grades are to be retrieved.
            
        Returns:
            pandas.Series: A Series containing the grades for the specified student.
        """
        grades_per_student_sql = '''
        SELECT 
            sb.SubjectName as SubjectName, 
            e.ExamName as ExamName, 
            e.ExamDate as ExamDate, 
            g.MarksObtained as StudentMarks,
            e.MaximumMarks as MaxMarks
        FROM Grades g
        JOIN Exams e ON e.ExamID = g.ExamID
        JOIN Students s ON s.StudentID = g.StudentID
        JOIN Subjects sb ON sb.SubjectID = e.SubjectID
        WHERE g.StudentID = ?
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(grades_per_student_sql, conn, params=(student_id,))


    # REPORTS - 2
    def get_student_performance(self, student_id):
        """
        Retrieve comprehensive student performance data as a DataFrame.

        This method connects to the database specified by `self.db_path` and 
        retrieves the performance data for a given student, identified by `student_id`.
        The performance data includes the subject name, exam name, exam date, 
        marks obtained, and maximum marks for each exam taken by the student.
        The results are ordered by the exam date.

        Args:
            student_id (int): The ID of the student whose performance data is to be retrieved.
            conn (sqlite3.Connection, optional): An optional SQLite connection object.

        Returns:
            pandas.DataFrame: A DataFrame containing the student's performance data.
        """
        """Retrieve comprehensive student performance data as a DataFrame"""
        performance_query = '''
        SELECT 
            s.SubjectName, 
            e.ExamName, 
            e.ExamDate, 
            g.MarksObtained,
            e.MaximumMarks
        FROM Grades g
        JOIN Exams e ON g.ExamID = e.ExamID
        JOIN Subjects s ON e.SubjectID = s.SubjectID
        WHERE g.StudentID = ?
        ORDER BY e.ExamDate
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(performance_query, conn, params=(student_id,))

    def get_academic_performance_distribution(self):
        """
        Get comprehensive academic performance distribution with additional metrics
        
        Returns:
            pandas.DataFrame: Detailed performance metrics for subjects
        """
        distribution_query = '''
        SELECT 
            s.SubjectName,
            s.Department,
            ROUND(AVG(g.MarksObtained), 2) as AverageMarks,
            ROUND(MIN(g.MarksObtained), 2) as MinMarks,
            ROUND(MAX(g.MarksObtained), 2) as MaxMarks,
            COUNT(g.GradeID) as TotalExams,
            
            -- Performance distribution calculations
            ROUND(
                SUM(CASE 
                    WHEN g.MarksObtained >= e.MaximumMarks * 0.9 THEN 1 
                    WHEN g.MarksObtained >= e.MaximumMarks * 0.8 THEN 1 
                    WHEN g.MarksObtained >= e.MaximumMarks * 0.7 THEN 1 
                    WHEN g.MarksObtained >= e.MaximumMarks * 0.6 THEN 1 
                    ELSE 0 
                END) * 100.0 / COUNT(g.GradeID), 
            2) AS PassPercentage,
            
            -- Grade distribution
            ROUND(
                SUM(CASE 
                    WHEN g.MarksObtained >= e.MaximumMarks * 0.9 THEN 1 
                    ELSE 0 
                END) * 100.0 / COUNT(g.GradeID), 
            2) AS GradeAPercentage,
            
            ROUND(
                SUM(CASE 
                    WHEN g.MarksObtained >= e.MaximumMarks * 0.8 AND g.MarksObtained < e.MaximumMarks * 0.9 THEN 1 
                    ELSE 0 
                END) * 100.0 / COUNT(g.GradeID), 
            2) AS GradeBPercentage,
            
            -- Manual standard deviation calculation
            ROUND(
                SQRT(
                    AVG(g.MarksObtained * g.MarksObtained) - 
                    AVG(g.MarksObtained) * AVG(g.MarksObtained)
                ), 
            2) AS MarksStandardDeviation
        
        FROM Grades g
        JOIN Exams e ON g.ExamID = e.ExamID
        JOIN Subjects s ON e.SubjectID = s.SubjectID
        GROUP BY s.SubjectName, s.Department
        ORDER BY AverageMarks DESC
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(distribution_query, conn)
    