from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional, List
from uuid import UUID

class ProgrammingGridBase(BaseModel):
    channel: str
    broadcast_date: date
    start_time: time
    end_time: Optional[time]
    program_name: str
    description: Optional[str]
    is_live: bool

class ProgrammingGridResponse(ProgrammingGridBase):
    id: UUID

    class Config:
        from_attributes = True

class GridLookupResponse(BaseModel):
    total: int
    items: List[ProgrammingGridResponse]

# Monitoring Rule Schemas
class MonitoringRuleBase(BaseModel):
    channel: str
    program_name: Optional[str] = None
    start_time: time
    end_time: time
    days_of_week: List[int]

class MonitoringRuleCreate(MonitoringRuleBase):
    pass

class MonitoringRuleResponse(MonitoringRuleBase):
    id: UUID
    monitoring_set_id: UUID

    class Config:
        from_attributes = True

# Monitoring Set Schemas
class MonitoringSetBase(BaseModel):
    name: str
    search_terms: List[str]
    audience_data_enabled: Optional[bool] = False
    clip_context_seconds: Optional[int] = 15

class MonitoringSetCreate(MonitoringSetBase):
    rules: List[MonitoringRuleCreate]

class MonitoringSetUpdate(MonitoringSetBase):
    rules: Optional[List[MonitoringRuleCreate]] = None
    status: Optional[str] = None

class MonitoringSetResponse(MonitoringSetBase):
    id: UUID
    user_id: UUID
    status: str
    total_minutes_estimate: int
    created_at: datetime
    rules: List[MonitoringRuleResponse]

    class Config:
        from_attributes = True

# Operator Schemas
class OperatorAction(BaseModel):
    action: str
    target_id: UUID
    justification: Optional[str] = None
    details: Optional[dict] = None

class OperatorLogResponse(BaseModel):
    id: UUID
    operator_id: UUID
    operator_name: Optional[str] = None
    action: str
    target_id: Optional[UUID]
    target_type: Optional[str]
    justification: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class UserUpdateByOperator(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    credit_limit: Optional[int] = None
    is_blocked_access: Optional[bool] = None
    status: Optional[str] = None

class ClientOperatorResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    company_name: str
    credit_limit: int
    is_blocked_access: bool
    status: str
    active_sets_count: int
    total_minutes_estimate: int

    class Config:
        from_attributes = True

class MonitoringSetOperatorResponse(MonitoringSetResponse):
    client_name: str
    client_company: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    role: str
    company_name: Optional[str]
    status: str
    is_blocked_access: bool

    class Config:
        from_attributes = True

# Report Config Schemas
class ReportConfigBase(BaseModel):
    frequency: str
    day_of_week: Optional[int] = None
    hour: int
    email_recipients: List[str]

class ReportConfigCreate(ReportConfigBase):
    monitoring_set_id: UUID

class ReportConfigResponse(ReportConfigBase):
    id: UUID
    user_id: UUID
    monitoring_set_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Report Schemas
class ReportResponse(BaseModel):
    id: UUID
    monitoring_set_id: UUID
    generated_at: datetime
    file_url: str
    period_start: datetime
    period_end: datetime
    status: str

    class Config:
        from_attributes = True

# Invoice Schemas
class InvoiceResponse(BaseModel):
    id: UUID
    amount: int
    due_date: date
    status: str
    pdf_url: Optional[str]
    billing_period: str

    class Config:
        from_attributes = True

# Mention Schemas
class MentionBase(BaseModel):
    channel: str
    program_name: Optional[str] = None
    occurrence_time: datetime
    transcription: str
    context: Optional[str] = None
    video_url: Optional[str] = None

class MentionResponse(MentionBase):
    id: UUID
    monitoring_set_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
