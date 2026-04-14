import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Time, Date, JSON, ARRAY, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    qualification = Column(String)
    billing_info = Column(JSON)
    credit_limit = Column(Integer, default=5000) # In currency cents
    is_blocked_access = Column(Boolean, default=False)
    role = Column(String, default="client")  # admin, client, operator
    status = Column(String, default="pending_approval")  # pending_approval, approved, blocked
    erp_client_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    monitoring_sets = relationship("MonitoringSet", back_populates="owner")

class MonitoringSet(Base):
    __tablename__ = "monitoring_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    search_terms = Column(ARRAY(String), nullable=False)
    status = Column(String, default="stand_by")  # stand_by, awaiting_approval, approved, active, cancelled
    total_minutes_estimate = Column(Integer, default=0)
    audience_data_enabled = Column(Boolean, default=False)
    clip_context_seconds = Column(Integer, default=15) # Context offset
    erp_order_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="monitoring_sets")
    rules = relationship("MonitoringRule", back_populates="monitoring_set", cascade="all, delete-orphan")
    mentions = relationship("Mention", back_populates="monitoring_set", cascade="all, delete-orphan")
    report_configs = relationship("ReportConfig", back_populates="monitoring_set", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="monitoring_set", cascade="all, delete-orphan")

class MonitoringRule(Base):
    __tablename__ = "monitoring_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitoring_set_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sets.id"), nullable=False)
    channel = Column(String, nullable=False)
    program_name = Column(String, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    days_of_week = Column(ARRAY(Integer), nullable=False)  # [1, 2, 3, 4, 5]
    created_at = Column(DateTime, default=datetime.utcnow)

    monitoring_set = relationship("MonitoringSet", back_populates="rules")

class ReportConfig(Base):
    __tablename__ = "report_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    monitoring_set_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sets.id"), nullable=False)
    frequency = Column(String, nullable=False)  # daily, weekly, monthly
    day_of_week = Column(Integer, nullable=True)  # 0-6
    hour = Column(Integer, nullable=False, default=8)
    email_recipients = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    monitoring_set = relationship("MonitoringSet", back_populates="report_configs")

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    monitoring_set_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sets.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    file_url = Column(String, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String, default="ready")

    monitoring_set = relationship("MonitoringSet", back_populates="reports")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # In cents or fixed decimal
    due_date = Column(Date, nullable=False)
    status = Column(String, default="pending")  # pending, paid, overdue
    pdf_url = Column(String, nullable=True)
    billing_period = Column(String, nullable=False) # e.g., "2026-04"
    created_at = Column(DateTime, default=datetime.utcnow)

class Mention(Base):
    __tablename__ = "mentions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitoring_set_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sets.id"), nullable=False)
    channel = Column(String, nullable=False)
    program_name = Column(String, nullable=True)
    occurrence_time = Column(DateTime, nullable=False)
    transcription = Column(String, nullable=False)
    context = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    monitoring_set = relationship("MonitoringSet", back_populates="mentions")

class ProgrammingGrid(Base):
    __tablename__ = "programming_grid"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel = Column(String, nullable=False, index=True)
    broadcast_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    program_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_live = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemConfig(Base):
    __tablename__ = "system_configs"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OperatorLog(Base):
    __tablename__ = "operator_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=True)
    target_type = Column(String, nullable=True) # "user", "set"
    justification = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    operator = relationship("User")
