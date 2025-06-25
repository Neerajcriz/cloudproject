from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Database Models
class StudentDB(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String, nullable=True)
    age = Column(Integer)
    city = Column(String)

class ClassDB(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String)
    description = Column(Text)
    start_date = Column(String)
    end_date = Column(String)
    number_of_hours = Column(Integer)

class RegistrationDB(Base):
    __tablename__ = "registrations"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    student_id = Column(Integer, ForeignKey("students.id"))

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
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

# Routes
@app.post("/students/")
def add_student(student: Student):
    db = SessionLocal()
    new_student = StudentDB(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    db.close()
    return {"student_id": new_student.id, "message": "Student added."}

@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    db = SessionLocal()
    existing_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not existing_student:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found.")
    for key, value in student.dict().items():
        setattr(existing_student, key, value)
    db.commit()
    db.close()
    return {"message": "Student updated."}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    db = SessionLocal()
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not student:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found.")
    db.delete(student)
    db.commit()
    db.close()
    return {"message": "Student deleted."}

@app.post("/classes/")
def add_class(cls: Class):
    db = SessionLocal()
    new_class = ClassDB(**cls.dict())
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    db.close()
    return {"class_id": new_class.id, "message": "Class added."}

@app.put("/classes/{class_id}")
def update_class(class_id: int, cls: Class):
    db = SessionLocal()
    existing_class = db.query(ClassDB).filter(ClassDB.id == class_id).first()
    if not existing_class:
        db.close()
        raise HTTPException(status_code=404, detail="Class not found.")
    for key, value in cls.dict().items():
        setattr(existing_class, key, value)
    db.commit()
    db.close()
    return {"message": "Class updated."}

@app.delete("/classes/{class_id}")
def delete_class(class_id: int):
    db = SessionLocal()
    existing_class = db.query(ClassDB).filter(ClassDB.id == class_id).first()
    if not existing_class:
        db.close()
        raise HTTPException(status_code=404, detail="Class not found.")
    db.delete(existing_class)
    db.commit()
    db.close()
    return {"message": "Class deleted."}

@app.post("/classes/{class_id}/register")
def register_student(class_id: int, student_id: int):
    db = SessionLocal()
    # Check if class and student exist
    cls = db.query(ClassDB).filter(ClassDB.id == class_id).first()
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not cls or not student:
        db.close()
        raise HTTPException(status_code=404, detail="Class or Student not found.")
    registration = RegistrationDB(class_id=class_id, student_id=student_id)
    db.add(registration)
    db.commit()
    db.close()
    return {"message": "Student registered to class."}

@app.get("/classes/{class_id}/students")
def get_registered_students(class_id: int):
    db = SessionLocal()
    cls = db.query(ClassDB).filter(ClassDB.id == class_id).first()
    if not cls:
        db.close()
        raise HTTPException(status_code=404, detail="Class not found.")
    registrations = db.query(RegistrationDB).filter(RegistrationDB.class_id == class_id).all()
    student_list = []
    for reg in registrations:
        student = db.query(StudentDB).filter(StudentDB.id == reg.student_id).first()
        if student:
            student_list.append({
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "city": student.city
            })
    db.close()
    return {"students": student_list}
