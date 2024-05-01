from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sql.database.db_manager import Base
from sqlalchemy.sql import func

class Teacher(Base):
    __tablename__ = "teacher"
    __table_args__ = {"extend_existing": True}
    email = Column(String, primary_key=True)
    name = Column(String)
    password = Column(String)
    division = Column(String)
    sem = Column(String)
    subject= Column(String)
    year = Column(String)

class Student(Base):
    __tablename__ = "student"
    __table_args__ = {"extend_existing": True}
    email = Column(String, primary_key=True)
    name = Column(String)
    rollno = Column(Integer)
    division = Column(String, ForeignKey("division.division"))
    sem = Column(String)
    year = Column(Integer)
    password = Column(String)

class Division(Base):
    __tablename__ = "division"
    __table_args__ = {"extend_existing": True}
    division = Column(String, primary_key=True)
    sem = Column(String, primary_key=True)
    year = Column(Integer, primary_key=True)
    
class Division_Teacher(Base):
    __tablename__ = "division_teacher"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    division = Column(String, ForeignKey("division.division"))
    teacher_email = Column(String, ForeignKey("teacher.email"))

class Division_Student(Base):
    __tablename__ = "division_student"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    division = Column(String, ForeignKey("division.division"))
    student_email = Column(String, ForeignKey("student.email"))

class Subject(Base):
    __tablename__ = "subject"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    division = Column(String)
    name = Column(String)
    sem = Column(String)
    teacher_email = Column(String)
    year = Column(Integer)

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = {"extend_existing": True}
    subject_id = Column(Integer,primary_key=True)
    date = Column(DateTime, primary_key=True)
    student_email = Column(String,primary_key=True) 
    teacher_email = Column(String)
