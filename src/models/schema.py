from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrganizationMember(Base):
    __tablename__ = "organization_members"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False) # owner, admin, manager, member

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DealStatus(str, enum.Enum):
    new = "new"
    inprogress = "inprogress"
    won = "won"
    lost = "lost"

class DealStage(str, enum.Enum):
    qualification = "qualification"
    proposal = "proposal"
    negotiation = "negotiation"
    closed = "closed"

class Deal(Base):
    __tablename__ = "deals"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    amount = Column(Numeric(12,2), nullable=False)
    currency = Column(String, nullable=False)  # USD, EUR
    status = Column(Enum(DealStatus), default=DealStatus.new)
    stage = Column(Enum(DealStage), default=DealStage.qualification)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    title = Column(String)
    description = Column(String)
    due_date = Column(DateTime)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityType(str, enum.Enum):
    comment = "comment"
    statuschanged = "statuschanged"
    taskcreated = "taskcreated"
    system = "system"

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    type = Column(Enum(ActivityType), nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
