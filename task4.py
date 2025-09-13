from altair import Description
from fastapi import FastAPI,HTTPException,Query,Path
import json,uuid,uvicorn
from typing import List , Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field,EmailStr, validator

app = FastAPI(title="student management system")
JSON_FILE="student.json"

class Students(BaseModel):
    name:str= Field(..., min_length=2)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email:EmailStr
    age:int=Field(...,ge=10,le=100)
    department:Optional[str]=None
    created_at:datetime=Field(default_factory=datetime.now)
    cgpa:float= Field(...,ge=0.0,le=4.0)
    @validator('name')
    def name_space(cls,v):
        if len(v.strip())<2:
            raise ValueError("name must be atleast 2 charachteers long ")
        return v.title()
def read_json_file():
        try:
            with open(JSON_FILE,'r')as f:
                return json.load(f)
        except(FileNotFoundError,json.JSONDecodeError):
            return[]
def write_json_file(data):
        with open(JSON_FILE,'w')as f:
            json.dump(data,f,default=str,indent=2)
def student_dict(student:Students):
     return{
          "id":str(student.id),
          "name":student.name,
          "age":student.age,
          "email":student.email,
          "department": student.department,
          "cgpa":student.cgpa,
          "created_at":student.created_at.isoformat()       
     }
#api end points
@app.post("/students/",response_model=Dict[str,Any])
def create_student(student:Students):
     student_data=read_json_file()
     #check duplicate
     for existing_student in student_data:
          if existing_student["email"]==student.email:
               raise HTTPException(status_code=400,detail="email already exist try another")
          student_dic=student_dict(student)
          student_data.append(student_dic)
          write_json_file(student_data)
          return{"message": "student ceated successfully","student":student_dic}
@app.get("/students/{student_id}",response_model=Dict[str,Any])
def get_student_by_id(student_id:str=Path(...,description="enter the id of studengt to retrieve")):
     student_data=read_json_file()
     for student in student_data:
          if student["id"]==student_id:
               return student
     raise HTTPException(status_code=404, detail="Student not found")

@app.put("/students/{student_id}", response_model=Dict[str, Any])
def update_student(
    student_id: str, 
    name: Optional[str] = Query(None, min_length=2),
    email: Optional[EmailStr] = Query(None),
    age: Optional[int] = Query(None, ge=10, le=100),
    department: Optional[str] = Query(None),
    cgpa: Optional[float] = Query(None, ge=0.0, le=4.0)
):
    students_data = read_json_file()
    student_found = False
    
    for student in students_data:
        if student["id"] == student_id:
            student_found = True
            
            # Check for duplicate email if email is being updated
            if email:
                for existing_student in students_data:
                    if existing_student["email"] == email and existing_student["id"] != student_id:
                        raise HTTPException(status_code=400, detail="Email already exists")
                student["email"] = email
            
            if name:
                if ' ' not in name:
                    raise HTTPException(status_code=400, detail="Name must contain at least a first and last name")
                student["name"] = name.title()
            
            if age:
                student["age"] = age
            
            if department is not None:  
                student["department"] = department
            
            if cgpa:
                student["cgpa"] = cgpa
            
            break
    
    if not student_found:
        raise HTTPException(status_code=404, detail="Student not found")
    
    write_json_file(students_data)
    return {"message": "Student updated successfully"}

@app.delete("/students/{student_id}", response_model=Dict[str, Any])
def delete_student(student_id: str = Path(..., description="The ID of the student to delete")):
    students_data = read_json_file()
    updated_students = [s for s in students_data if s["id"] != student_id]
    
    if len(updated_students) == len(students_data):
        raise HTTPException(status_code=404, detail="Student not found")
    
    write_json_file(updated_students)
    return {"message": "Student deleted successfully"}

@app.get("/students/", response_model=List[Dict[str, Any]])
def list_all_students(
    search: Optional[str] = Query(None, description="Search by name or email"),
    department: Optional[str] = Query(None, description="Filter by department"),
    sort_by: Optional[str] = Query(None, description="Sort by 'name' or 'age'"),
    sort_order: Optional[str] = Query("asc", description="Sort order: 'asc' or 'desc'")
):
    students_data = read_json_file()
    
    # Filter by search term
    if search:
        students_data = [
            s for s in students_data 
            if search.lower() in s["name"].lower() or search.lower() in s["email"].lower()
        ]
    
    # Filter by department
    if department:
        students_data = [s for s in students_data if s["department"] and department.lower() in s["department"].lower()]
    
    # Sorting
    if sort_by:
        reverse_order = sort_order.lower() == "desc"
        if sort_by == "name":
            students_data.sort(key=lambda x: x["name"], reverse=reverse_order)
        elif sort_by == "age":
            students_data.sort(key=lambda x: x["age"], reverse=reverse_order)
    
    return students_data

@app.get("/stats/", response_model=Dict[str, Any])
def get_stats():
    students_data = read_json_file()
    
    if not students_data:
        return {
            "total_students": 0,
            "average_age": 0,
            "count_per_department": {}
        }
    
    total_students = len(students_data)
    average_age = sum(student["age"] for student in students_data) / total_students
    
    count_per_department = {}
    for student in students_data:
        dept = student["department"] or "Undeclared"
        count_per_department[dept] = count_per_department.get(dept, 0) + 1
    
    return {
        "total_students": total_students,
        "average_age": round(average_age, 2),
        "count_per_department": count_per_department
    }

