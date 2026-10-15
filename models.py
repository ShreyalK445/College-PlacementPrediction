"""
Database Models — College Placement & Career Intelligence Platform
Supports SQLite and PostgreSQL via SQLAlchemy.
"""

from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash
import os

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(
        String(30), default="student", nullable=False
    )  # student, mentor, tpo, admin
    department = Column(String(80), default="Computer Science")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    assessments = relationship(
        "AssessmentRecord", back_populates="user", cascade="all, delete-orphan"
    )
    roadmap_tasks = relationship(
        "RoadmapTask", back_populates="user", cascade="all, delete-orphan"
    )
    mock_attempts = relationship(
        "MockAssessmentAttempt", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "department": self.department,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AssessmentRecord(Base):
    __tablename__ = "assessment_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    inputs_json = Column(Text, nullable=False)
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    explainability_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    user = relationship("User", back_populates="assessments")

    def get_inputs(self):
        return json.loads(self.inputs_json) if self.inputs_json else {}

    def get_explainability(self):
        return (
            json.loads(self.explainability_json) if self.explainability_json else None
        )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "inputs": self.get_inputs(),
            "prediction": self.prediction,
            "probability": self.probability,
            "status": self.status,
            "explainability": self.get_explainability(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(
        String(60), nullable=False
    )  # Academics, Coding, Communication, Projects, Mock Interviews
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    status = Column(String(30), default="pending")  # pending, in_progress, completed
    deadline = Column(String(50), nullable=True)
    resources_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="roadmap_tasks")

    def get_resources(self):
        return json.loads(self.resources_json) if self.resources_json else []

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "week_number": self.week_number,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "deadline": self.deadline,
            "resources": self.get_resources(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MockAssessmentAttempt(Base):
    __tablename__ = "mock_assessment_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    test_type = Column(
        String(60), nullable=False
    )  # technical, aptitude, hr, software_developer, etc.
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_spent_secs = Column(Integer, default=0)
    category_scores_json = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    user = relationship("User", back_populates="mock_attempts")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "test_type": self.test_type,
            "score": self.score,
            "total_questions": self.total_questions,
            "time_spent_secs": self.time_spent_secs,
            "category_scores": json.loads(self.category_scores_json)
            if self.category_scores_json
            else {},
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MentorIntervention(Base):
    __tablename__ = "mentor_interventions"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    student_name = Column(String(120), nullable=False)
    student_email = Column(String(120), nullable=False)
    priority = Column(String(20), default="High")  # High, Medium, Low
    reason = Column(Text, nullable=False)
    action_plan = Column(Text, nullable=False)
    follow_up_date = Column(String(50), nullable=True)
    status = Column(String(30), default="Open")  # Open, In Progress, Resolved
    created_by_name = Column(String(120), default="Placement Officer")
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "student_email": self.student_email,
            "priority": self.priority,
            "reason": self.reason,
            "action_plan": self.action_plan,
            "follow_up_date": self.follow_up_date,
            "status": self.status,
            "created_by": self.created_by_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Database Session Management
# ---------------------------------------------------------------------------

_engine = None
_session_factory = None


def init_db(database_uri=None):
    global _engine, _session_factory
    if database_uri is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "placement_platform.db")
        database_uri = f"sqlite:///{db_path}"

    _engine = create_engine(
        database_uri,
        connect_args={"check_same_thread": False} if "sqlite" in database_uri else {},
        echo=False,
    )
    Base.metadata.create_all(_engine)
    _session_factory = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    )
    return _engine


def get_db_session():
    global _session_factory
    if _session_factory is None:
        init_db()
    return _session_factory()
