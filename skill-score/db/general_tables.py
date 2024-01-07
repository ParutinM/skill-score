from typing import Optional
from sqlalchemy import Text, Date, MetaData, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import date


class Base(DeclarativeBase):
    metadata = MetaData(schema="general")


class Session(Base):
    __tablename__ = "session"
    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[str] = mapped_column(JSONB())


class Region(Base):
    __tablename__ = "region"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class School(Base):
    __tablename__ = "school"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    region_id: Mapped[int] = mapped_column(Integer())


class Privilege(Base):
    __tablename__ = "privilege"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class Subject(Base):
    __tablename__ = "subject"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class Complexity(Base):
    __tablename__ = "complexity"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class AnswerType(Base):
    __tablename__ = "answer_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    sections: Mapped[str] = mapped_column(JSONB(), nullable=False)
    tags: Mapped[str] = mapped_column(JSONB(), nullable=False)
    complexity_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    task: Mapped[str] = mapped_column(Text(), nullable=False)
    task_picture: Mapped[Optional[bytes]] = mapped_column(BYTEA())
    solution: Mapped[str] = mapped_column(Text(), nullable=False)
    solution_picture: Mapped[Optional[bytes]] = mapped_column(BYTEA())
    answer: Mapped[str] = mapped_column(Text(), nullable=False)
    answer_type_id: Mapped[str] = mapped_column(Integer(), nullable=False)


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    privilege_id: Mapped[Optional[int]] = mapped_column(Integer())
    first_name: Mapped[str] = mapped_column(Text(), nullable=False)
    last_name: Mapped[str] = mapped_column(Text(), nullable=False)
    email: Mapped[str] = mapped_column(Text(), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date(), nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text(), nullable=False)
    avatar: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(Text())


class SectionTree(Base):
    __tablename__ = "section_tree"
    section_id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    section_name: Mapped[str] = mapped_column(Text(), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer())


class TeacherInfo(Base):
    __tablename__ = "teacher_info"
    teacher_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer())
    subject_id: Mapped[int] = mapped_column(Integer())


class StudentInfo(Base):
    __tablename__ = "student_info"
    student_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer())
    school_id: Mapped[int] = mapped_column(Integer())
    grade: Mapped[int] = mapped_column(Integer())


# class Class(Base):
#     __tablename__ = "class"
