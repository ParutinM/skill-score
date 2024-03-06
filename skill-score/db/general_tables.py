from typing import Optional, List
from sqlalchemy import Text, Date, MetaData, ForeignKey, Integer, Connection, select
from sqlalchemy.dialects.postgresql import BYTEA, JSONB, JSON
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import date


class Base(DeclarativeBase):
    metadata = MetaData(schema="general")


class Region(Base):
    __tablename__ = "region"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class School(Base):
    __tablename__ = "school"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    region_id: Mapped[int] = mapped_column(Integer(), nullable=False)


class Subject(Base):
    __tablename__ = "subject"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class Complexity(Base):
    __tablename__ = "complexity"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class Privilege(Base):
    __tablename__ = "privilege"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class AnswerType(Base):
    __tablename__ = "answer_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class TaskSourceType(Base):
    __tablename__ = "task_source_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class TaskSource(Base):
    __tablename__ = "task_source"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    type_id: Mapped[int] = mapped_column(Integer(), nullable=False)


class TaskSourceExtra(Base):
    __tablename__ = "task_source_extra"
    id: Mapped[int] = mapped_column(primary_key=True)
    extra: Mapped[str] = mapped_column(Text(), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer(), nullable=False)


class TaskTag(Base):
    __tablename__ = "task_tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)


class ServiceBase(DeclarativeBase):
    metadata = MetaData(schema="service")


class User(ServiceBase):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    privilege_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    first_name: Mapped[str] = mapped_column(Text(), nullable=False)
    last_name: Mapped[str] = mapped_column(Text(), nullable=False)
    email: Mapped[str] = mapped_column(Text(), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date(), nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text(), nullable=False)
    avatar: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    subject_id: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    school_id: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    grade: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)


class Task(ServiceBase):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    answer_type_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    source_type_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    source_extra: Mapped[str] = mapped_column(JSON(), nullable=False)
    topics: Mapped[str] = mapped_column(JSON(), nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(JSON(), nullable=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    task: Mapped[str] = mapped_column(Text(), nullable=False)
    symbols: Mapped[str] = mapped_column(JSON(), nullable=False)
    task_pic: Mapped[Optional[bytes]] = mapped_column(BYTEA(), nullable=True)
    task_pic_name: Mapped[str] = mapped_column(Text(), nullable=True)
    solution: Mapped[str] = mapped_column(Text(), nullable=False)
    solution_pic: Mapped[Optional[bytes]] = mapped_column(BYTEA(), nullable=True)
    solution_pic_name: Mapped[str] = mapped_column(Text(), nullable=True)
    answer: Mapped[str] = mapped_column(Text(), nullable=False)
    answer_extra: Mapped[str] = mapped_column(JSON(), nullable=False)


class TopicTree(ServiceBase):
    __tablename__ = "topic_tree"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer())


class Anonymous(ServiceBase):
    __tablename__ = "anonymous"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ajs_id: Mapped[str] = mapped_column(Text(), nullable=False)
    state: Mapped[str] = mapped_column(JSON(), nullable=False)
    is_authed: Mapped[int] = mapped_column(Integer(), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
