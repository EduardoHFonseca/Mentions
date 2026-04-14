from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from uuid import UUID
import uvicorn

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
    
    if user.status == "pending_approval":
        raise HTTPException(status_code=403, detail="Sua conta está aguardando aprovação")
    
    if user.is_blocked_access:
        raise HTTPException(status_code=403, detail="Seu acesso está bloqueado")
        
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
        billing_info=user_data.billing_info
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/grid/channels", response_model=List[str])
def get_channels(db: Session = Depends(get_db)):
    # Fetch all channels, trim them and get unique ones in uppercase
    channels = db.query(models.ProgrammingGrid.channel).distinct().all()
    unique_channels = sorted(list(set(c[0].strip().upper() for c in channels if c[0])))
    return unique_channels

@app.get("/api/grid/lookup", response_model=schemas.GridLookupResponse)
def lookup_grid(
    q: Optional[str] = Query(None, description="Search by program name or description"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.ProgrammingGrid)
    
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

    db_set = models.MonitoringSet(
        user_id=effective_user_id,
        name=set_data.name,
        search_terms=set_data.search_terms,
        status="stand_by",
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

@app.get("/api/invoices", response_model=List[schemas.InvoiceResponse])
def list_invoices(user_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    if not user_id:
        user = db.query(models.User).filter(models.User.role == "client").first()
        effective_user_id = user.id if user else None
    else:
        effective_user_id = user_id
        
    if not effective_user_id: return []
    return db.query(models.Invoice).filter(models.Invoice.user_id == effective_user_id).order_by(models.Invoice.due_date.desc()).all()

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
    return {"status": "updated", "new_status": status}

# Operator Specific Endpoints
@app.get("/api/operator/pending-sets")
def list_pending_sets(db: Session = Depends(get_db)):
    sets = db.query(models.MonitoringSet).join(models.User).filter(models.MonitoringSet.status == "awaiting_approval").all()
    results = []
    for s in sets:
        results.append({
            "id": s.id,
            "name": s.name,
            "client_name": s.owner.full_name,
            "client_company": s.owner.company_name,
            "total_minutes": s.total_minutes_estimate,
            "client_credit_limit": s.owner.credit_limit,
            "user_id": s.user_id
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
    db.commit()
    return {"status": "updated", "credit_limit": credit_limit}

@app.post("/api/operator/approve-set")
def approve_set(action: schemas.OperatorAction, db: Session = Depends(get_db)):
    operator = db.query(models.User).filter(models.User.role == "operator").first()
    if not operator:
        operator = models.User(email="operator@mentions.com", role="operator", password_hash="op", full_name="Op Interno")
        db.add(operator); db.commit(); db.refresh(operator)

    db_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.id == action.target_id).first()
    if not db_set: raise HTTPException(status_code=404)

    db_set.status = "approved"
    
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
