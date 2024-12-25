from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil

from utils import ID_TO_TABLE, TABLE_TO_ID

import pandas as pd
# Import your database and report generator
from database import DatabaseManager
from report_generator import ReportGenerator

# Initialize database and report generator
db_manager = DatabaseManager()
report_generator = ReportGenerator(db_manager)

# Create V1 Router
router_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

@router_v1.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file and import data into the enhanced database"""
    try:
        # Create uploads directory if not exists
        os.makedirs('uploads', exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join('uploads', file.filename)
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        df = pd.read_csv(file_path)
        db_manager.import_csv(df)
        
        return JSONResponse(
            status_code=200, 
            content={
                "filename": file.filename, 
                "tablename": ID_TO_TABLE.get(df.columns[0], None),
                "status": "Uploaded and imported successfully",
                "message": "Data has been successfully imported into the database."
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_v1.get("/table/{table_name}")
async def get_table_data(table_name: str, limit = Query(100), id: int = Query(None)):
    """Retrieve data from specified table"""
    try:
        with db_manager.get_connection() as conn:
            if id:
                query = f'select * from {table_name} where {TABLE_TO_ID[table_name]} = {int(id)}  LIMIT {limit}'
            else:
                query = f'select * from {table_name} LIMIT {limit}'
            return pd.read_sql(query, conn).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router_v1.get("/reports/student-profile/{student_id}")
async def generate_student_profile_report(student_id: int):
    """Generate comprehensive student profile report"""
    try:
        pdf_path = report_generator.generate_student_profile_report(student_id)
        return FileResponse(pdf_path, media_type='application/pdf', filename=f'student_{student_id}_profile_report.pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_v1.get("/reports/academic-performance")
async def generate_academic_performance_report():
    """Generate comprehensive academic performance distribution report"""
    try:
        pdf_path = report_generator.generate_academic_performance_report()
        print(pdf_path)
        return FileResponse(pdf_path, media_type='application/pdf', filename='academic_performance_report.pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

