import hashlib
import hmac
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import ChecklistItem, Issue, Partner, Submission
from .validation.engine import parse_feed, validate


def safe_name(name:str)->str: return Path(name).name.replace("..","")[:180] or "feed"
def store(data:bytes, digest:str)->str:
    settings.storage_path.mkdir(parents=True,exist_ok=True); path=settings.storage_path/f"{digest}.feed"; path.write_bytes(data); return str(path)
def process(db:Session, sub:Submission, data:bytes):
    try:
        payload=parse_feed(data,sub.format); findings=validate(payload); total=len(payload.get("programs") or []); bad={f.row for f in findings if f.severity=="error" and f.row}
        sub.record_count=total; sub.invalid_record_count=len(bad); sub.valid_record_count=max(0,total-len(bad)); sub.status="action_required" if any(f.severity=="error" for f in findings) else "succeeded"
        for f in findings: db.add(Issue(submission_id=sub.id,program_external_id=f.content_id,row_number=f.row,field=f.field,category=f.category,severity=f.severity,code=f.code,message=f.message,suggested_fix=f.fix,fingerprint=f.fingerprint))
    except (ValueError,UnicodeError,json.JSONDecodeError) as exc: sub.status="failed"; sub.failure_reason=str(exc)[:500]
    from datetime import datetime, timezone
    sub.completed_at=datetime.now(timezone.utc); db.commit(); update_readiness(db,sub.partner_id)
def update_readiness(db:Session,partner_id:int):
    partner=db.get(Partner,partner_id); items=db.scalars(select(ChecklistItem).where(ChecklistItem.partner_id==partner_id)).all(); score=sum(i.weight for i in items if i.status=="complete")
    latest=db.scalar(select(Submission).where(Submission.partner_id==partner_id).order_by(Submission.received_at.desc()))
    if latest and latest.status=="succeeded": score=max(score,50)
    partner.readiness_score=min(score,100); partner.status="launch_ready" if score==100 else ("action_required" if latest and latest.status!="succeeded" else "in_progress"); db.commit()
def sign(secret:str, body:bytes)->str: return "sha256="+hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
def backoff(attempt:int,seed:int=0)->float: return min(300,2**attempt)+(hashlib.sha256(f"{seed}:{attempt}".encode()).digest()[0]/255)
