from fastapi import FastAPI
app= FastAPI()
student = {
    "id": "SE-002",
    "name": "Adan Naveed",
    "field": " Software Engineering"
}
@app.get("/")
def hello():
    return{
        "student_deatil": student
    }