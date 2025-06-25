from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

students = {}
classes = {}
registrations = {}

class Student(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    age: int
    city: str

class Class(BaseModel):
    class_name: str
    description: str
    start_date: str
    end_date: str
    number_of_hours: int

@app.post("/students/")
def add_student(student: Student):
    student_id = len(students) + 1
    students[student_id] = student
    return {"student_id": student_id, "message": "Student added."}

@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found.")
    students[student_id] = student
    return {"message": "Student updated."}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found.")
    del students[student_id]
    return {"message": "Student deleted."}

@app.post("/classes/")
def add_class(cls: Class):
    class_id = len(classes) + 1
    classes[class_id] = cls
    return {"class_id": class_id, "message": "Class added."}

@app.put("/classes/{class_id}")
def update_class(class_id: int, cls: Class):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found.")
    classes[class_id] = cls
    return {"message": "Class updated."}

@app.delete("/classes/{class_id}")
def delete_class(class_id: int):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found.")
    del classes[class_id]
    return {"message": "Class deleted."}

@app.post("/classes/{class_id}/register")
def register_student(class_id: int, student_id: int):
    if class_id not in classes or student_id not in students:
        raise HTTPException(status_code=404, detail="Class or Student not found.")
    registrations.setdefault(class_id, []).append(student_id)
    return {"message": "Student registered to class."}

@app.get("/classes/{class_id}/students")
def get_registered_students(class_id: int):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found.")
    student_list = [students[sid] for sid in registrations.get(class_id, [])]
    return {"students": student_list}
