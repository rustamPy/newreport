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

        """
        subjects_per_student_sql = """
        SELECT s.StudentID, sub.SubjectName, sub.Department FROM Students s
        JOIN Grades g ON s.StudentID = g.StudentID
        JOIN Exams e ON e.ExamID = g.ExamID
        JOIN Subjects sub ON sub.SubjectID = e.SubjectID
        WHERE s.StudentID = ?
        """

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
    def get_universities_details(self) -> pd.Series:
        """
        Retrieve university details for report branding.

        Returns:
            pd.Series: Series containing:
                - UniversityID
                - UniversityName
                - LogoURL
                - Address
                - ContactDetails
        """
        query = """
        SELECT 
            UniversityID,
            UniversityName,
            LogoURL,
            Address,
            ContactDetails
        FROM Universities
        LIMIT 1
        """

        with sqlite3.connect(self.db_path) as conn:
            result = pd.read_sql(query, conn)
            return result.iloc[0] if not result.empty else pd.Series()

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

    # TESTED
    def get_all_grades(self) -> pd.DataFrame:
        """
        Retrieve all grades data with associated exam, subject, and department information.

        Returns:
            pd.DataFrame: DataFrame containing columns:
                - StudentID
                - SubjectName
                - Department
                - MarksObtained
                - MaximumMarks
                - ExamDate
                - ExamName
        """
        query = """
        SELECT 
            g.StudentID,
            s.SubjectName,
            s.Department,
            g.MarksObtained as StudentMarks,
            e.MaximumMarks as MaxMarks,
            e.ExamDate,
            e.ExamName
        FROM Grades g
        JOIN Exams e ON g.ExamID = e.ExamID
        JOIN Subjects s ON e.SubjectID = s.SubjectID
        ORDER BY e.ExamDate ASC
        """

        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(query, conn)

    # TESTED
    def get_all_students(self) -> pd.DataFrame:
        """
        Retrieve all student records with basic information.

        Returns:
            pd.DataFrame: DataFrame containing columns:
                - StudentID
                - FirstName
                - LastName
                - Email
                - DateOfBirth
                - AcademicYear
                - ImageURL
                - UniversityID
        """
        query = "SELECT * FROM Students"

        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(query, conn)
