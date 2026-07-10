from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String, Table, Column # type: ignore
from sqlalchemy.orm import ( # type: ignore
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


# Many-to-many association table
student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("student.id"), primary_key=True),
    Column("course_id", ForeignKey("course.id"), primary_key=True),
)


class Person(Base):
    """Base class using joined-table inheritance."""

    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20))

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __mapper_args__ = {
        "polymorphic_identity": "person",
        "polymorphic_on": type,
    }


class Student(Person):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(ForeignKey("person.id"), primary_key=True)
    major: Mapped[str] = mapped_column(String(100))

    advisor_id: Mapped[int | None] = mapped_column(
        ForeignKey("teacher.id"),
        nullable=True,
    )

    advisor: Mapped["Teacher | None"] = relationship(
        back_populates="students"
    )

    courses: Mapped[List["Course"]] = relationship(
        secondary=student_course,
        back_populates="students",
    )

    __mapper_args__ = {
        "polymorphic_identity": "student",
    }


class Teacher(Person):
    __tablename__ = "teacher"

    id: Mapped[int] = mapped_column(ForeignKey("person.id"), primary_key=True)
    department: Mapped[str] = mapped_column(String(100))

    students: Mapped[List[Student]] = relationship(
        back_populates="advisor"
    )

    courses: Mapped[List["Course"]] = relationship(
        back_populates="teacher"
    )

    __mapper_args__ = {
        "polymorphic_identity": "teacher",
    }


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    title: Mapped[str] = mapped_column(String(100))

    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher.id"))

    teacher: Mapped[Teacher] = relationship(
        back_populates="courses"
    )

    students: Mapped[List[Student]] = relationship(
        secondary=student_course,
        back_populates="courses",
    )
