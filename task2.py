from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import json

app = FastAPI()

# Load student data
def load_data():
    with open("student.json", "r") as f:
        data = json.load(f)
    return data["student_data"]   # <-- FIX: get the list inside "student_data"

@app.get("/", status_code=200)
def get_all_students():
    students = load_data()
    return {"students": students}

@app.get("/student/{student_id}", status_code=200)
def get_student_by_id(student_id: int):
    students = load_data()
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/students/sorted", status_code=200)
def get_sorted_students(sort_by: Optional[str] = Query("cgpa")):
    students = load_data()
    if sort_by != "cgpa":
        raise HTTPException(status_code=400, detail="Sorting only available by CGPA")
    
    sorted_students = sorted(students, key=lambda x: x["cgpa"], reverse=True)
    return {"students": sorted_students}
