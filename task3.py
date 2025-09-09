from pydantic import BaseModel,Field
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from typing import Optional, Annotated
import json

class Student(BaseModel):

    id: Annotated[int, Field(...,title="Student Id" ,description="Unique for each student", examples=[1,2])]
    name:Annotated[str,Field(..., max_length=50, min_length= 2,title="Student Name", description="Student's Name")]
    age: Annotated[int, Field(gt=5,lt=100, title="Student's age")]
    roll_no: Annotated[str,Field(title="Student Roll_no", description="Unique roll no of student")]
    grade: Optional[str]

app=FastAPI()

def load_data():
    with open("student.json","r") as f:
        data=json.load(f)
        return data
    
def save_data(data):
    with open("student.json","w") as f:
        json.dump(data,f)

@app.get("/students")
def get_students_data():
    data=load_data()
    return data

@app.post('/create_student')
def create_student(student: Student):
    data=load_data()

    if str(student.id) in data:
        raise HTTPException(status_code=400, detail="Student Already Exits")
    
    for sid,info in data.items():
        if info['roll_no'] == student.roll_no:
            raise HTTPException(status_code=400, detail="Roll number already exists")
    
    data[str(student.id)]=student.model_dump(exclude='id')

    save_data(data)

    return JSONResponse(status_code=201, content={"message":"Student created successfully"})

@app.get("/student/{student_id}")
def get_student_data(student_id:str=Path(...,description="The id of the student", example=4)):
    data=load_data()

    if student_id in data:
        return data[student_id]
    raise HTTPException(status_code=404,detail="Student not found")