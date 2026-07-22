from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import or_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
import uvicorn
import shutil
import os

from src.database import get_db
from src.models import models
from src.models import schemas

app = FastAPI(title="Mentions On-Demand API", version="1.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mentions On-Demand API is running", "version": "1.1.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/auth/login", response_model=schemas.UserResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(func.lower(models.User.email) == func.lower(req.email)).first()
    if not user or user.password_hash != req.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    if user.status == "pending_approval" and user.role != "client":
        raise HTTPException(status_code=403, detail="Sua conta está aguardando aprovação")
    
    if user.is_blocked_access and user.status != "pending_approval":
        raise HTTPException(status_code=403, detail="Seu acesso está bloqueado")
        
    return user

@app.get("/api/user/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@app.patch("/api/user/{user_id}/profile", response_model=schemas.UserResponse)
def update_client_profile(user_id: UUID, profile_data: schemas.ClientProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name
        
    b_info = dict(user.billing_info) if user.billing_info else {}
    if profile_data.phone is not None:
        b_info["telefone"] = profile_data.phone
    if profile_data.address is not None:
        b_info["endereco"] = profile_data.address
        
    user.billing_info = b_info
    flag_modified(user, "billing_info")
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register_public(user_data: schemas.UserCreateByOperator, db: Session = Depends(get_db)):
    # Check if user exists
    email_lower = user_data.email.lower()
    existing = db.query(models.User).filter(func.lower(models.User.email) == email_lower).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    
    db_user = models.User(
        email=email_lower,
        password_hash=user_data.password,
        full_name=user_data.full_name,
        company_name=user_data.company_name,
        role="client",
        status="pending_approval", # Force pending approval for public registration
        credit_limit=0, # Initial credit 0
        is_blocked_access=True, # Initially blocked
        document_status="missing",
        billing_info=user_data.billing_info
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/grid/channels", response_model=List[str])
def get_channels(market: Optional[str] = Query(None, description="Filter by market (NACIONAL, SP, RJ, NL)"), db: Session = Depends(get_db)):
    # Fetch all channels, trim them and get unique ones in uppercase
    query = db.query(models.ProgrammingGrid.channel)
    if market:
        query = query.filter(models.ProgrammingGrid.market.ilike(f"%{market}%"))
    channels = query.distinct().all()
    unique_channels = sorted(list(set(c[0].strip().upper() for c in channels if c[0])))
    return unique_channels

@app.get("/api/grid/lookup", response_model=schemas.GridLookupResponse)
def lookup_grid(
    q: Optional[str] = Query(None, description="Search by program name or description"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    market: Optional[str] = Query("NACIONAL", description="Filter by market (NACIONAL, SP, RJ)"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.ProgrammingGrid)
    
    market_val = market or "NACIONAL"
    query = query.filter(models.ProgrammingGrid.market.ilike(f"%{market_val}%"))
    
    if channel:
        query = query.filter(models.ProgrammingGrid.channel.ilike(f"%{channel}%"))
    
    if q:
        query = query.filter(
            or_(
                models.ProgrammingGrid.program_name.ilike(f"%{q}%"),
                models.ProgrammingGrid.description.ilike(f"%{q}%")
            )
        )
    
    total = query.count()
    items = query.order_by(models.ProgrammingGrid.broadcast_date.desc(), models.ProgrammingGrid.start_time.asc()).offset(offset).limit(limit).all()
    
    return {"total": total, "items": items}

# Monitoring Sets CRUD
@app.post("/api/sets", response_model=schemas.MonitoringSetResponse)
def create_monitoring_set(set_data: schemas.MonitoringSetCreate, user_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    if not user_id:
        user = db.query(models.User).filter(models.User.role == "client").first()
        if not user:
            raise HTTPException(status_code=404, detail="Nenhum usuário cliente encontrado")
        effective_user_id = user.id
    else:
        effective_user_id = user_id
    
    # Calculate estimated minutes
    total_min = 0
    for r in set_data.rules:
        h1, m1 = r.start_time.hour, r.start_time.minute
        h2, m2 = r.end_time.hour, r.end_time.minute
        duration = (h2*60 + m2) - (h1*60 + m1)
        if duration < 0: duration += 24*60 # Cross midnight
        total_min += duration * len(r.days_of_week)

    # AUTO-APPROVAL LOGIC
    # 1. Get user credit and existing active sets cost
    user_obj = db.query(models.User).filter(models.User.id == effective_user_id).first()
    
    # Simple price logic: 10 cents per minute
    new_set_cost = total_min * 10
    
    # Calculate current usage
    existing_sets = db.query(models.MonitoringSet).filter(
        models.MonitoringSet.user_id == effective_user_id,
        models.MonitoringSet.status == "active"
    ).all()
    current_weekly_cost = sum(s.total_minutes_estimate * 10 for s in existing_sets)
    
    # Decide status
    if (current_weekly_cost + new_set_cost) <= user_obj.credit_limit:
        initial_status = "active"
    else:
        initial_status = "awaiting_approval"

    db_set = models.MonitoringSet(
        user_id=effective_user_id,
        name=set_data.name,
        search_terms=set_data.search_terms,
        status=initial_status,
        total_minutes_estimate=total_min,
        audience_data_enabled=set_data.audience_data_enabled,
        clip_context_seconds=set_data.clip_context_seconds
    )

    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    
    for rule_data in set_data.rules:
        db_rule = models.MonitoringRule(
            monitoring_set_id=db_set.id,
            **rule_data.model_dump() if hasattr(rule_data, "model_dump") else rule_data.dict()
        )
        db.add(db_rule)
    
    db.commit()
    db.refresh(db_set)
    return db_set

# Report Config & History Endpoints
@app.post("/api/reports/config", response_model=schemas.ReportConfigResponse)
def create_report_config(config: schemas.ReportConfigCreate, user_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    if not user_id:
        user = db.query(models.User).filter(models.User.role == "client").first()
        effective_user_id = user.id if user else None
    else:
        effective_user_id = user_id

    db_config = models.ReportConfig(
        user_id=effective_user_id,
        **config.model_dump()
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@app.get("/api/reports/config/{set_id}", response_model=Optional[schemas.ReportConfigResponse])
def get_report_config(set_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.ReportConfig).filter(models.ReportConfig.monitoring_set_id == set_id).first()

@app.get("/api/reports/history/{set_id}", response_model=List[schemas.ReportResponse])
def get_report_history(set_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Report).filter(models.Report.monitoring_set_id == set_id).order_by(models.Report.generated_at.desc()).all()

@app.post("/api/reports/generate", response_model=schemas.ReportResponse)
def generate_report_manual(
    set_id: UUID, 
    user_id: UUID, 
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None), 
    db: Session = Depends(get_db)
):
    from datetime import timedelta
    import random
    
    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
        
    report_num = random.randint(1000, 9999)
    
    p_start = datetime.combine(start_date, datetime.min.time()) if start_date else (datetime.utcnow() - timedelta(days=7))
    p_end = datetime.combine(end_date, datetime.max.time()) if end_date else datetime.utcnow()
    
    db_report = models.Report(
        user_id=user_id,
        monitoring_set_id=set_id,
        generated_at=datetime.utcnow(),
        file_url=f"https://example.com/reports/report_{db_set.name.replace(' ', '_')}_{report_num}.pdf",
        period_start=p_start,
        period_end=p_end,
        status="ready"
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@app.get("/api/invoices", response_model=List[schemas.InvoiceResponse])
def list_invoices(user_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    if not user_id:
        user = db.query(models.User).filter(models.User.role == "client").first()
        effective_user_id = user.id if user else None
    else:
        effective_user_id = user_id
        
    if not effective_user_id: return []
    return db.query(models.Invoice).filter(models.Invoice.user_id == effective_user_id).order_by(models.Invoice.due_date.desc()).all()

@app.patch("/api/invoices/{invoice_id}/pay")
def pay_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    inv = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    inv.status = "paid"
    db.commit()
    return {"status": "success", "message": "Fatura dada como paga com sucesso", "invoice_id": invoice_id}

@app.get("/api/sets", response_model=List[schemas.MonitoringSetResponse])
def list_monitoring_sets(user_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.MonitoringSet)
    if user_id:
        query = query.filter(models.MonitoringSet.user_id == user_id)
    return query.all()

@app.put("/api/sets/{set_id}", response_model=schemas.MonitoringSetResponse)
def update_monitoring_set(set_id: UUID, set_data: schemas.MonitoringSetUpdate, db: Session = Depends(get_db)):
    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    
    db_set.name = set_data.name
    db_set.search_terms = set_data.search_terms
    db_set.audience_data_enabled = set_data.audience_data_enabled
    db_set.clip_context_seconds = set_data.clip_context_seconds
    if set_data.status:
        db_set.status = set_data.status

    if set_data.rules is not None:
        db.query(models.MonitoringRule).filter(models.MonitoringRule.monitoring_set_id == set_id).delete()
        for rule_data in set_data.rules:
            db_rule = models.MonitoringRule(
                monitoring_set_id=db_set.id,
                **rule_data.model_dump() if hasattr(rule_data, "model_dump") else rule_data.dict()
            )
            db.add(db_rule)
    
    db.commit()
    db.refresh(db_set)
    return db_set

@app.delete("/api/sets/{set_id}")
def delete_monitoring_set(set_id: UUID, db: Session = Depends(get_db)):
    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    db.delete(db_set)
    db.commit()
    return {"status": "deleted"}

@app.patch("/api/sets/{set_id}/status")
def update_set_status(set_id: UUID, status: str, db: Session = Depends(get_db)):
    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    
    db_set.status = status
    db.commit()
    
    if status in ["active", "approved"]:
        create_tasks_for_approved_set(db, db_set)
        
    return {"status": "updated", "new_status": status}

# Operator Specific Endpoints
@app.get("/api/operator/pending-clients", response_model=List[schemas.ClientOperatorResponse])
def list_pending_clients(db: Session = Depends(get_db)):
    clients = db.query(models.User).filter(models.User.role == "client", models.User.status == "pending_approval").all()
    results = []
    for c in clients:
        active_sets = [s for s in c.monitoring_sets if s.status == "active"]
        total_min = sum(s.total_minutes_estimate for s in c.monitoring_sets)
        results.append({
            "id": c.id,
            "full_name": c.full_name or "N/A",
            "email": c.email,
            "company_name": c.company_name or "N/A",
            "credit_limit": c.credit_limit,
            "is_blocked_access": c.is_blocked_access,
            "status": c.status,
            "active_sets_count": len(active_sets),
            "total_minutes_estimate": total_min,
            "billing_info": c.billing_info,
            "document_status": c.document_status,
            "documents": c.documents
        })
    return results

@app.patch("/api/operator/approve-client/{user_id}")
def approve_client(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    user.status = "approved"
    user.is_blocked_access = False
    
    # Update document_status based on uploaded documents
    docs = user.documents or {}
    if "certidao" in docs and "contrato" in docs:
        user.document_status = "verified"
    elif docs:
        user.document_status = "partial"
    else:
        user.document_status = "missing"

    operator = db.query(models.User).filter(models.User.role == "operator").first()
    if operator:
        log = models.OperatorLog(
            operator_id=operator.id,
            action="APPROVE_CLIENT",
            target_id=user_id,
            target_type="user",
            justification=f"Aprovação de cadastro para a empresa {user.company_name}"
        )
        db.add(log)

    db.commit()
    return {"status": "approved", "user_id": user_id}

@app.get("/api/operator/pending-sets")
def list_pending_sets(db: Session = Depends(get_db)):
    sets = db.query(models.MonitoringSet).join(models.User).filter(models.MonitoringSet.status == "awaiting_approval").all()
    results = []
    for s in sets:
        unique_channels = set(r.channel for r in s.rules)
        unique_programs = set(r.program_name for r in s.rules if r.program_name)
        all_days = set()
        for r in s.rules:
            if r.days_of_week:
                all_days.update(r.days_of_week)
                
        results.append({
            "id": s.id,
            "name": s.name,
            "client_name": s.owner.full_name if s.owner else "N/A",
            "client_company": s.owner.company_name if s.owner else "N/A",
            "total_minutes": s.total_minutes_estimate,
            "client_credit_limit": (s.owner.credit_limit or 0) if s.owner else 0,
            "user_id": s.user_id,
            "client_document_status": s.owner.document_status if s.owner else "missing",
            "channels_count": len(unique_channels),
            "programs_count": len(unique_programs),
            "frequency_weekly_count": len(all_days)
        })
    return results

@app.get("/api/operator/clients", response_model=List[schemas.ClientOperatorResponse])
def list_clients_for_operator(db: Session = Depends(get_db)):
    clients = db.query(models.User).filter(models.User.role == "client").all()
    results = []
    for c in clients:
        active_sets = [s for s in c.monitoring_sets if s.status == "active"]
        total_min = sum(s.total_minutes_estimate for s in c.monitoring_sets)
        results.append({
            "id": c.id,
            "full_name": c.full_name or "N/A",
            "email": c.email,
            "company_name": c.company_name or "N/A",
            "credit_limit": c.credit_limit,
            "is_blocked_access": c.is_blocked_access,
            "status": c.status,
            "active_sets_count": len(active_sets),
            "total_minutes_estimate": total_min,
            "billing_info": c.billing_info
        })
    return results

@app.post("/api/operator/user", response_model=schemas.UserResponse)
def create_user_by_operator(user_data: schemas.UserCreateByOperator, db: Session = Depends(get_db)):
    # Check if user exists
    email_lower = user_data.email.lower()
    existing = db.query(models.User).filter(func.lower(models.User.email) == email_lower).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    
    db_user = models.User(
        email=email_lower,
        password_hash=user_data.password,

        full_name=user_data.full_name,
        company_name=user_data.company_name,
        role=user_data.role,
        status=user_data.status,
        credit_limit=user_data.credit_limit,
        billing_info=user_data.billing_info
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/api/operator/user/{user_id}")
def delete_user_by_operator(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

@app.delete("/api/operator/user/{user_id}/sets")
def delete_all_user_sets(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Delete all monitoring sets (cascading to rules and mentions)
    db.query(models.MonitoringSet).filter(models.MonitoringSet.user_id == user_id).delete()
    db.commit()
    return {"status": "all sets deleted"}

@app.patch("/api/operator/user/{user_id}")
def update_user_details(user_id: UUID, update_data: schemas.UserUpdateByOperator, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    
    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.company_name is not None:
        user.company_name = update_data.company_name
    if update_data.credit_limit is not None:
        user.credit_limit = update_data.credit_limit
    if update_data.is_blocked_access is not None:
        user.is_blocked_access = update_data.is_blocked_access
    if update_data.status is not None:
        user.status = update_data.status
    if update_data.password is not None:
        user.password_hash = update_data.password
    if update_data.role is not None:
        user.role = update_data.role
    if update_data.document_status is not None:
        user.document_status = update_data.document_status
    if update_data.billing_info is not None:
        if user.billing_info is None:
            user.billing_info = update_data.billing_info
        else:
            current_info = dict(user.billing_info)
            current_info.update(update_data.billing_info)
            user.billing_info = current_info
        
    db.commit()
    return {"status": "updated"}

@app.get("/api/operator/sets", response_model=List[schemas.MonitoringSetOperatorResponse])
def list_all_sets_for_operator(db: Session = Depends(get_db)):
    sets = db.query(models.MonitoringSet).all()
    for s in sets:
        s.client_name = s.owner.full_name
        s.client_company = s.owner.company_name
    return sets

@app.post("/api/sets/{set_id}/reprocess")
def reprocess_set(set_id: UUID, db: Session = Depends(get_db)):
    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    
    operator = db.query(models.User).filter(models.User.role == "operator").first()
    log = models.OperatorLog(
        operator_id=operator.id,
        action="reprocess_set",
        target_id=set_id,
        target_type="set",
        justification="Reprocessamento solicitado pelo operador"
    )
    db.add(log)
    db.commit()
    return {"status": "reprocessing_queued", "set_id": set_id}

@app.patch("/api/operator/user/{user_id}/credit")
def update_user_credit(user_id: UUID, credit_limit: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    
    user.credit_limit = credit_limit
    
    operator = db.query(models.User).filter(models.User.role == "operator").first()
    if operator:
        log = models.OperatorLog(
            operator_id=operator.id,
            action="UPDATE_CREDIT_LIMIT",
            target_id=user_id,
            target_type="user",
            justification=f"Ajuste de limite de crédito para R$ {credit_limit/100:.2f} ({user.company_name})"
        )
        db.add(log)

    db.commit()
    return {"status": "updated", "credit_limit": credit_limit}

def create_tasks_for_approved_set(db: Session, db_set: models.MonitoringSet):
    from datetime import date, timedelta, time, datetime
    import json
    
    current_date = date(2026, 6, 30) # Anchor to our environment's current date
    dates_to_process = [current_date - timedelta(days=i) for i in range(3, -1, -1)]
    
    # Get all existing tasks for this set to avoid duplicate creations
    existing_tasks = db.query(models.TaskQueue).filter(models.TaskQueue.monitoring_set_id == db_set.id).all()
    
    for d in dates_to_process:
        weekday = d.isoweekday() # 1 = Monday, 7 = Sunday
        
        for rule in db_set.rules:
            if weekday in rule.days_of_week:
                # Query ProgrammingGrid for this channel, date and market
                grid_items = db.query(models.ProgrammingGrid).filter(
                    models.ProgrammingGrid.channel == rule.channel,
                    models.ProgrammingGrid.broadcast_date == d,
                    models.ProgrammingGrid.market == (rule.market or "NACIONAL")
                ).all()
                
                for prog in grid_items:
                    # Match by name or time overlap
                    name_match = False
                    if rule.program_name and prog.program_name:
                        if rule.program_name.lower() in prog.program_name.lower() or prog.program_name.lower() in rule.program_name.lower():
                            name_match = True
                    
                    time_overlap = False
                    if rule.start_time and rule.end_time and prog.start_time:
                        if rule.start_time <= prog.start_time <= rule.end_time:
                            time_overlap = True
                            
                    if name_match or time_overlap:
                        # Check duplicate in Python
                        is_duplicate = False
                        for et in existing_tasks:
                            if et.task_type == "transcribe_and_clip" and et.payload:
                                if et.payload.get("broadcast_date") == str(d) and et.payload.get("program_name") == prog.program_name and et.payload.get("market") == prog.market:
                                    is_duplicate = True
                                    break
                                    
                        if not is_duplicate:
                            prog_end_time = prog.end_time if prog.end_time else rule.end_time
                            scheduled_time = datetime.combine(d, prog_end_time) + timedelta(hours=1)
                            
                            payload_data = {
                                "channel": prog.channel,
                                "program_name": prog.program_name,
                                "broadcast_date": str(d),
                                "start_time": str(prog.start_time),
                                "end_time": str(prog.end_time) if prog.end_time else None,
                                "market": prog.market
                            }
                            
                            task = models.TaskQueue(
                                monitoring_set_id=db_set.id,
                                task_type="transcribe_and_clip",
                                scheduled_for=scheduled_time,
                                status="pending",
                                payload=payload_data
                            )
                            db.add(task)
                            
        # Create daily report task for D+1 at 06:00
        report_scheduled = datetime.combine(d + timedelta(days=1), time(6, 0, 0))
        is_report_duplicate = False
        for et in existing_tasks:
            if et.task_type == "send_daily_report" and et.payload:
                if et.payload.get("broadcast_date") == str(d):
                    is_report_duplicate = True
                    break
                    
        if not is_report_duplicate:
            rep_task = models.TaskQueue(
                monitoring_set_id=db_set.id,
                task_type="send_daily_report",
                scheduled_for=report_scheduled,
                status="pending",
                payload={"broadcast_date": str(d)}
            )
            db.add(rep_task)
            
    db.commit()

@app.post("/api/operator/approve-set")
def approve_set(action: schemas.OperatorAction, db: Session = Depends(get_db)):
    operator = db.query(models.User).filter(models.User.role == "operator").first()
    if not operator:
        operator = models.User(email="operator@mentions.com", role="operator", password_hash="op", full_name="Op Interno")
        db.add(operator); db.commit(); db.refresh(operator)

    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == action.target_id).first()
    if not db_set: raise HTTPException(status_code=404)

    db_set.status = "approved"
    db.commit() # commit status first
    
    # Generate background tasks for the newly approved set
    create_tasks_for_approved_set(db, db_set)
    
    log = models.OperatorLog(
        operator_id=operator.id,
        action="approve_set",
        target_id=db_set.id,
        target_type="set",
        justification=action.justification
    )
    db.add(log)
    db.commit()
    return {"status": "approved"}

@app.patch("/api/operator/user/{user_id}/block")
def block_user_access(user_id: UUID, block: bool, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    
    user.is_blocked_access = block

    operator = db.query(models.User).filter(models.User.role == "operator").first()
    if operator:
        act = "BLOCK_USER" if block else "UNBLOCK_USER"
        log = models.OperatorLog(
            operator_id=operator.id,
            action=act,
            target_id=user_id,
            target_type="user",
            justification=f"Acesso {'bloqueado' if block else 'desbloqueado'} para a empresa {user.company_name}"
        )
        db.add(log)

    db.commit()
    return {"status": "updated", "is_blocked": block}

@app.get("/api/admin/logs", response_model=List[schemas.OperatorLogResponse])
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(models.OperatorLog).order_by(models.OperatorLog.timestamp.desc()).all()
    for log in logs:
        if log.operator:
            log.operator_name = log.operator.full_name
    return logs

@app.get("/api/operator/health")
def get_system_health(db: Session = Depends(get_db)):
    active_clients = db.query(models.User).filter(models.User.role == "client", models.User.status == "approved").count()
    active_sets = db.query(models.MonitoringSet).filter(models.MonitoringSet.status == "active").count()
    return {
        "active_clients": active_clients,
        "active_sets": active_sets,
        "running_now": 2,
        "upcoming": 5,
        "errors": 0
    }

@app.get("/api/mentions", response_model=List[schemas.MentionResponse])
def list_all_mentions(
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return db.query(models.Mention).order_by(models.Mention.occurrence_time.desc()).offset(offset).limit(limit).all()

@app.get("/api/sets/{set_id}/mentions", response_model=List[schemas.MentionResponse])
def get_set_mentions(set_id: UUID, db: Session = Depends(get_db)):
    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    return db_set.mentions

@app.post("/api/sets/{set_id}/mentions", response_model=schemas.MentionResponse)
def create_mention(set_id: UUID, mention_data: schemas.MentionBase, db: Session = Depends(get_db)):
    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    
    db_mention = models.Mention(
        monitoring_set_id=set_id,
        **mention_data.dict()
    )
    db.add(db_mention)
    db.commit()
    db.refresh(db_mention)
    return db_mention

@app.get("/api/admin/users", response_model=List[schemas.UserResponse])
def list_internal_users(db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.role.in_(["admin", "operator"])).all()
    return users

@app.post("/api/admin/user", response_model=schemas.UserResponse)
def create_internal_user(user_data: schemas.UserCreateByOperator, db: Session = Depends(get_db)):
    email_lower = user_data.email.lower()
    existing = db.query(models.User).filter(func.lower(models.User.email) == email_lower).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    
    db_user = models.User(
        email=email_lower,
        password_hash=user_data.password,
        full_name=user_data.full_name,
        company_name="INTERNAL",
        role=user_data.role, # Should be admin or operator
        status="approved"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

DEFAULT_CONFIGS = {
    "default_credit_limit": "50.0",
    "price_per_minute": "0.10",
    "audience_multiplier_pct": "20.0",
    "clip_context_seconds": "15"
}

@app.get("/api/admin/config", response_model=schemas.SystemConfigResponse)
def get_system_config(db: Session = Depends(get_db)):
    cfg_rows = db.query(models.SystemConfig).all()
    cfg_map = {c.key: c.value for c in cfg_rows}
    
    updated = False
    for k, default_val in DEFAULT_CONFIGS.items():
        if k not in cfg_map:
            new_cfg = models.SystemConfig(key=k, value=default_val, description=f"Default {k}")
            db.add(new_cfg)
            cfg_map[k] = default_val
            updated = True
            
    if updated:
        db.commit()
        
    return schemas.SystemConfigResponse(
        default_credit_limit=float(cfg_map.get("default_credit_limit", 50.0)),
        price_per_minute=float(cfg_map.get("price_per_minute", 0.10)),
        audience_multiplier_pct=float(cfg_map.get("audience_multiplier_pct", 20.0)),
        clip_context_seconds=int(cfg_map.get("clip_context_seconds", 15))
    )

@app.post("/api/admin/config", response_model=schemas.SystemConfigResponse)
def update_system_config(config_data: schemas.SystemConfigUpdate, db: Session = Depends(get_db)):
    updates = {
        "default_credit_limit": str(config_data.default_credit_limit),
        "price_per_minute": str(config_data.price_per_minute),
        "audience_multiplier_pct": str(config_data.audience_multiplier_pct),
        "clip_context_seconds": str(config_data.clip_context_seconds)
    }
    
    for k, v in updates.items():
        existing = db.query(models.SystemConfig).filter(models.SystemConfig.key == k).first()
        if existing:
            existing.value = v
        else:
            db.add(models.SystemConfig(key=k, value=v, description=f"Updated {k}"))
            
    db.commit()
    return get_system_config(db=db)

@app.post("/api/user/upload-document")
async def upload_document(
    user_id: UUID = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    upload_dir = "uploads"
    user_dir = os.path.join(upload_dir, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update documents JSON
    docs = dict(user.documents) if user.documents else {}
    docs[doc_type] = {
        "filename": file.filename,
        "path": file_path,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    user.documents = docs
    if "certidao" in docs and "contrato" in docs:
        user.document_status = "pending_review"
    else:
        user.document_status = "partial"
    db.commit()
    
    return {"status": "uploaded", "doc_type": doc_type}

@app.get("/api/user/document/{user_id}/{filename}")
def get_user_document(user_id: UUID, filename: str):
    file_path = os.path.join("uploads", str(user_id), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(file_path)

@app.get("/api/operator/tasks", response_model=List[schemas.TaskQueueResponse])
def get_task_queue(db: Session = Depends(get_db)):
    return db.query(models.TaskQueue).order_by(models.TaskQueue.scheduled_for.asc()).all()

@app.post("/api/operator/tasks/run")
def run_pending_tasks(db: Session = Depends(get_db)):
    import shutil
    import random
    import uuid
    from datetime import datetime, timedelta, time
    from src.services.email_service import email_service
    
    pending_tasks = db.query(models.TaskQueue).filter(models.TaskQueue.status == "pending").order_by(models.TaskQueue.scheduled_for.asc()).all()
    
    processed_count = 0
    for task in pending_tasks:
        task.status = "processing"
        db.commit()
        
        try:
            db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == task.monitoring_set_id).first()
            if not db_set:
                task.status = "failed"
                db.commit()
                continue
                
            if task.task_type == "transcribe_and_clip":
                channel = task.payload.get("channel")
                program_name = task.payload.get("program_name")
                broadcast_date_str = task.payload.get("broadcast_date")
                start_time_str = task.payload.get("start_time")
                
                broadcast_date = datetime.strptime(broadcast_date_str, "%Y-%m-%d").date()
                start_time_t = datetime.strptime(start_time_str, "%H:%M:%S").time()
                
                base_time = datetime.combine(broadcast_date, start_time_t) + timedelta(minutes=random.randint(12, 18))
                
                # For each term in the set
                for term in db_set.search_terms:
                    # 75% chance of finding the term
                    if random.random() < 0.75:
                        mention_id = uuid.uuid4()
                        
                        # Copy samplevideo.mp4 to unique clip
                        clips_dir = os.path.join("uploads", "clips")
                        os.makedirs(clips_dir, exist_ok=True)
                        source_video = os.path.join("uploads", "samplevideo.mp4")
                        target_video = os.path.join(clips_dir, f"clip_{mention_id}.mp4")
                        
                        if os.path.exists(source_video):
                            shutil.copy(source_video, target_video)
                        
                        phrases = [
                            f"E no bloco comercial, a {term} consolidou sua liderança de recall na praça de São Paulo com grande repercussão.",
                            f"Os números oficiais da Kantar mostram que a nova ativação da marca {term} no reality bateu recordes de engajamento diário.",
                            f"Entrevistados comentaram a importância do patrocínio esportivo da {term} na consolidação da marca em rede nacional.",
                            f"Na coletiva de imprensa, o porta-voz explicou como a {term} planeja expandir as operações neste segundo semestre."
                        ]
                        transcription = random.choice(phrases)
                        
                        # Determine realistic audience
                        aud_rating = 1500
                        aud_share = 2800
                        if channel == "GLOBO":
                            aud_rating = random.randint(1800, 2400)
                            aud_share = random.randint(3500, 4500)
                        elif channel == "SBT":
                            aud_rating = random.randint(400, 600)
                            aud_share = random.randint(1000, 1500)
                        elif channel == "RECORD":
                            aud_rating = random.randint(500, 800)
                            aud_share = random.randint(1200, 1800)
                        elif channel == "BANDEIRANTES":
                            aud_rating = random.randint(150, 300)
                            aud_share = random.randint(300, 600)
                            
                        db_mention = models.Mention(
                            id=mention_id,
                            monitoring_set_id=db_set.id,
                            channel=channel,
                            program_name=program_name,
                            occurrence_time=base_time,
                            transcription=transcription,
                            context=f"Transcrição automatizada via Kantar Transcription Façade. Clipe gerado com offset de {db_set.clip_context_seconds}s.",
                            video_url=f"uploads/clips/clip_{mention_id}.mp4",
                            audience_rating=aud_rating,
                            audience_share=aud_share
                        )
                        db.add(db_mention)
                        
                task.status = "completed"
                db.commit()
                
            elif task.task_type == "send_daily_report":
                broadcast_date_str = task.payload.get("broadcast_date")
                broadcast_date = datetime.strptime(broadcast_date_str, "%Y-%m-%d").date()
                
                # Fetch all mentions of this set for that day
                start_dt = datetime.combine(broadcast_date, datetime.min.time())
                end_dt = datetime.combine(broadcast_date, datetime.max.time())
                
                mentions = db.query(models.Mention).filter(
                    models.Mention.monitoring_set_id == db_set.id,
                    models.Mention.occurrence_time >= start_dt,
                    models.Mention.occurrence_time <= end_dt
                ).all()
                
                # Monitored programs list
                monitored_programs = [r.program_name for r in db_set.rules if r.program_name]
                if not monitored_programs:
                    monitored_programs = [f"Grade {r.channel}" for r in db_set.rules]
                
                client = db_set.owner
                to_emails = [client.email]
                formatted_date = broadcast_date.strftime("%d/%m/%Y")
                
                html_body = f"""
                <div style="font-family: 'Verdana', sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #E8E8EE; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <div style="background-color: #0F21FD; color: white; padding: 25px; text-align: center;">
                        <h2 style="margin: 0; font-size: 1.6rem; letter-spacing: 0.5px;">Mentions On-Demand</h2>
                        <p style="margin: 5px 0 0 0; font-size: 0.95rem; opacity: 0.9;">Relatório Diário Automatizado D+1</p>
                    </div>
                    <div style="padding: 30px; background-color: #F5F5F7;">
                        <p style="font-size: 1rem; line-height: 1.5; margin-top: 0;">Olá, <b>{client.full_name}</b>,</p>
                        <p style="font-size: 1rem; line-height: 1.5;">Abaixo está o resumo consolidado de monitoramento de ontem, <b>{formatted_date}</b>, para o conjunto <b>{db_set.name}</b>.</p>
                        
                        <div style="background-color: white; border-radius: 8px; padding: 18px; margin-bottom: 25px; border: 1px solid #E2E8F0;">
                            <h4 style="margin: 0 0 12px 0; color: #0F21FD; font-size: 1.15rem; border-bottom: 2px solid #0F21FD; padding-bottom: 6px; display: inline-block;">Ficha do Conjunto</h4>
                            <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem; margin-top: 5px;">
                                <tr>
                                    <td style="padding: 6px 0; color: #64748B; width: 35%;"><b>Termos de Busca:</b></td>
                                    <td style="padding: 6px 0; color: #1E293B;">{", ".join(db_set.search_terms)}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 6px 0; color: #64748B; valign: top;"><b>Programas Ativos:</b></td>
                                    <td style="padding: 6px 0; color: #1E293B;">{", ".join(set(monitored_programs))}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <h4 style="color: #0F21FD; font-size: 1.2rem; margin: 25px 0 12px 0;">Ocorrências Mapeadas</h4>
                """
                
                for prog in set(monitored_programs):
                    prog_mentions = [m for m in mentions if m.program_name and prog.lower() in m.program_name.lower()]
                    
                    html_body += f"""
                    <div style="background-color: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <h5 style="margin: 0 0 12px 0; font-size: 1.05rem; color: #0F21FD; border-bottom: 1px solid #EDF2F7; padding-bottom: 8px; font-weight: bold;">🎥 {prog}</h5>
                    """
                    
                    for term in db_set.search_terms:
                        term_mentions = [m for m in prog_mentions if term.lower() in m.transcription.lower()]
                        
                        if not term_mentions:
                            html_body += f"""
                            <p style="font-size: 0.95rem; margin: 6px 0; color: #64748B;">
                                ❌ Termo <b>'{term}'</b>: Zero ocorrências
                            </p>
                            """
                        else:
                            count = len(term_mentions)
                            times_str = ", ".join(m.occurrence_time.strftime("%H:%M:%S") for m in term_mentions)
                            html_body += f"""
                            <p style="font-size: 0.95rem; margin: 6px 0; color: #1E293B;">
                                ✅ Termo <b>'{term}'</b>: <b>{count}</b> ocorrência(s) às {times_str}
                            </p>
                            """
                            for m in term_mentions:
                                clip_url = f"http://localhost:8501/?user_id={client.id}&set_id={db_set.id}&mention_id={m.id}"
                                rating_val = f"{m.audience_rating/100:.2f} pontos" if m.audience_rating else "N/A"
                                html_body += f"""
                                <div style="margin-left: 15px; padding: 12px; background-color: #F8FAFC; border-left: 3px solid #0F21FD; border-radius: 0 4px 4px 0; font-size: 0.9rem; margin-top: 8px; margin-bottom: 8px;">
                                    <span style="display: block; margin-bottom: 5px; color: #334155;"><i>"{m.transcription}"</i></span>
                                    <span style="color: #64748B; font-size: 0.8rem;">📊 Audiência: <b>{rating_val}</b></span> | 
                                    <a href="{clip_url}" target="_blank" style="color: #0F21FD; font-weight: bold; text-decoration: none; font-size: 0.85rem;">▶️ Assistir Clipe ({db_set.clip_context_seconds}s)</a>
                                </div>
                                """
                                
                    html_body += "</div>"
                    
                html_body += f"""
                        <p style="font-size: 0.8rem; color: #64748B; margin-top: 30px; text-align: center; border-top: 1px solid #E2E8F0; padding-top: 18px; line-height: 1.4;">
                            Este é um e-mail gerado automaticamente pelo sistema Mentions On-Demand da Kantar IBOPE Media.<br>
                            © 2026 Kantar IBOPE Media. Todos os direitos reservados.
                        </p>
                    </div>
                </div>
                """
                
                # Send email report
                email_service.send_notification(
                    to=to_emails,
                    subject=f"Relatório Diário D+1 - {db_set.name} ({formatted_date})",
                    text=f"Relatório Diário para {db_set.name}. Ocorrências encontradas: {len(mentions)}.",
                    html=html_body
                )
                
                task.status = "completed"
                db.commit()
                
            processed_count += 1
        except Exception as e:
            task.status = "failed"
            db.commit()
            print(f"Error processing task {task.id}: {e}")
            
    return {"status": "success", "processed_tasks": processed_count}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
