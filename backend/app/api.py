import hashlib
import json
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .auth import current_user, require, scope_partner, token
from .config import settings
from .database import get_db
from .models import (
    AuditEvent,
    ChecklistItem,
    Contact,
    Delivery,
    DocPage,
    Issue,
    Partner,
    Role,
    Submission,
    User,
    Webhook,
)
from .services import backoff, process, safe_name, store, update_readiness

router=APIRouter(prefix="/api/v1")
class Login(BaseModel): email:str; password:str
class PartnerIn(BaseModel): name:str; slug:str; feed_type:str="json"
class ContactIn(BaseModel): name:str; email:str; role:str="Technical lead"; timezone:str="UTC"
class ChecklistPatch(BaseModel): status:str
class WebhookIn(BaseModel): url:str
def audit(db,user,action,entity,eid,partner_id=None,meta=None): db.add(AuditEvent(actor_id=user.id,partner_id=partner_id,action=action,entity_type=entity,entity_id=str(eid),metadata_json=meta or {}))
def serialize_issue(i): return {"id":i.id,"code":i.code,"category":i.category,"severity":i.severity,"message":i.message,"suggested_fix":i.suggested_fix,"row":i.row_number,"field":i.field,"content_id":i.program_external_id,"resolved":i.resolved,"documentation_slug":"validation-rules#"+i.code.lower(),"blocks_readiness":i.severity=="error"}
def serialize_sub(s): return {"id":s.id,"partner_id":s.partner_id,"format":s.format,"filename":s.source_filename,"status":s.status,"received_at":s.received_at,"completed_at":s.completed_at,"record_count":s.record_count,"valid_records":s.valid_record_count,"invalid_records":s.invalid_record_count,"retry_count":s.retry_count,"duplicate_content":False,"failure_reason":s.failure_reason}

@router.post("/auth/login")
def login(body:Login,db:Session=Depends(get_db)):
    from .auth import passwords
    user=db.scalar(select(User).where(User.email==body.email))
    if not user or not passwords.verify(body.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":token(user),"token_type":"bearer"}
@router.get("/auth/me")
def me(user:User=Depends(current_user)): return {"id":user.id,"name":user.name,"email":user.email,"role":user.role,"partner_id":user.partner_id}
@router.get("/partners")
def partners(db:Session=Depends(get_db),user:User=Depends(current_user)):
    q=select(Partner).order_by(Partner.name)
    if user.partner_id: q=q.where(Partner.id==user.partner_id)
    return db.scalars(q).all()
@router.post("/partners")
def create_partner(body:PartnerIn,db:Session=Depends(get_db),user:User=Depends(require(Role.platform_admin))):
    p=Partner(**body.model_dump()); db.add(p); db.flush(); audit(db,user,"partner.created","partner",p.id,p.id); db.commit(); return p
@router.get("/partners/{partner_id}")
def partner(partner_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    scope_partner(user,partner_id); p=db.get(Partner,partner_id)
    if not p: raise HTTPException(404,"Partner not found")
    return p
@router.get("/partners/{partner_id}/contacts")
def contacts(partner_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)): scope_partner(user,partner_id); return db.scalars(select(Contact).where(Contact.partner_id==partner_id)).all()
@router.post("/partners/{partner_id}/contacts")
def add_contact(partner_id:int,body:ContactIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    scope_partner(user,partner_id)
    if user.role==Role.partner_technical: raise HTTPException(403,"Only administrators may add contacts")
    c=Contact(partner_id=partner_id,**body.model_dump());db.add(c);audit(db,user,"contact.created","contact","new",partner_id);db.commit();return c

async def accept_submission(partner_id:int,data:bytes,filename:str,fmt:str,key:str,db:Session,user:User):
    scope_partner(user,partner_id)
    if len(data)>settings.max_upload_bytes: raise HTTPException(413,{"code":"UPLOAD_TOO_LARGE","message":"Feed exceeds the 10 MiB limit"})
    digest=hashlib.sha256(data).hexdigest(); existing=db.scalar(select(Submission).where(Submission.partner_id==partner_id,Submission.idempotency_key==key))
    if existing:
        if existing.content_hash!=digest: raise HTTPException(409,{"code":"IDEMPOTENCY_CONFLICT","message":"This key was already used with a different payload"})
        return serialize_sub(existing)
    if fmt not in ("json","xml"): raise HTTPException(415,{"code":"FORMAT_UNSUPPORTED","message":"Only JSON and XML feeds are supported"})
    sub=Submission(partner_id=partner_id,format=fmt,source_filename=safe_name(filename),storage_key=store(data,digest),content_hash=digest,idempotency_key=key,status="processing")
    db.add(sub);db.flush();audit(db,user,"submission.received","submission",sub.id,partner_id,{"format":fmt});db.commit();process(db,sub,data);return serialize_sub(sub)
@router.post("/partners/{partner_id}/submissions")
async def upload(partner_id:int,file:UploadFile=File(...),format:str|None=Form(None),idempotency_key:Annotated[str|None,Header(alias="Idempotency-Key")]=None,db:Session=Depends(get_db),user:User=Depends(current_user)):
    data=await file.read(settings.max_upload_bytes+1); fmt=format or ("xml" if (file.filename or "").lower().endswith(".xml") else "json")
    return await accept_submission(partner_id,data,file.filename or "feed",fmt,idempotency_key or secrets.token_urlsafe(16),db,user)
@router.post("/partners/{partner_id}/submissions/direct")
async def direct(partner_id:int,payload:dict,idempotency_key:Annotated[str|None,Header(alias="Idempotency-Key")]=None,db:Session=Depends(get_db),user:User=Depends(current_user)):
    return await accept_submission(partner_id,json.dumps(payload,separators=(",",":"),sort_keys=True).encode(),"direct.json","json",idempotency_key or secrets.token_urlsafe(16),db,user)
@router.get("/partners/{partner_id}/submissions")
def submissions(partner_id:int,limit:int=Query(50,le=100),db:Session=Depends(get_db),user:User=Depends(current_user)): scope_partner(user,partner_id); return [serialize_sub(s) for s in db.scalars(select(Submission).where(Submission.partner_id==partner_id).order_by(Submission.received_at.desc()).limit(limit))]
@router.get("/submissions/{submission_id}")
def submission(submission_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.get(Submission,submission_id)
    if not s: raise HTTPException(404,"Submission not found")
    scope_partner(user,s.partner_id); return serialize_sub(s)
@router.get("/submissions/{submission_id}/report")
def report(submission_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.get(Submission,submission_id)
    if not s: raise HTTPException(404,"Submission not found")
    scope_partner(user,s.partner_id); return {"submission":serialize_sub(s),"issues":[serialize_issue(i) for i in db.scalars(select(Issue).where(Issue.submission_id==s.id))]}
@router.get("/submissions/{submission_id}/report.csv",response_class=PlainTextResponse)
def report_csv(submission_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.get(Submission,submission_id)
    if not s: raise HTTPException(404,"Submission not found")
    scope_partner(user,s.partner_id); rows=["severity,code,category,row,field,message,suggested_fix"]
    import csv
    import io
    out=io.StringIO();w=csv.writer(out);w.writerow(rows[0].split(","));[w.writerow([i.severity,i.code,i.category,i.row_number,i.field,i.message,i.suggested_fix]) for i in db.scalars(select(Issue).where(Issue.submission_id==s.id))];return PlainTextResponse(out.getvalue(),media_type="text/csv",headers={"Content-Disposition":f"attachment; filename=channelbridge-report-{s.id}.csv"})
@router.post("/submissions/{submission_id}/retry")
def retry(submission_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.get(Submission,submission_id)
    if not s: raise HTTPException(404,"Submission not found")
    scope_partner(user,s.partner_id);s.retry_count+=1; audit(db,user,"submission.retry","submission",s.id,s.partner_id,{"delay_seconds":backoff(s.retry_count)});db.query(Issue).filter(Issue.submission_id==s.id).delete();db.commit();process(db,s,open(s.storage_key,"rb").read());return serialize_sub(s)
@router.get("/validation-runs/{submission_id}/issues")
def issues(submission_id:int,severity:str|None=None,search:str|None=None,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.get(Submission,submission_id)
    if not s: raise HTTPException(404,"Submission not found")
    scope_partner(user,s.partner_id);q=select(Issue).where(Issue.submission_id==submission_id)
    if severity:q=q.where(Issue.severity==severity)
    if search:q=q.where(or_(Issue.code.ilike(f"%{search}%"),Issue.message.ilike(f"%{search}%")))
    return [serialize_issue(i) for i in db.scalars(q)]
@router.get("/partners/{partner_id}/readiness")
def readiness(partner_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    scope_partner(user,partner_id);p=db.get(Partner,partner_id);items=db.scalars(select(ChecklistItem).where(ChecklistItem.partner_id==partner_id)).all();return {"score":p.readiness_score,"status":p.status,"calculation":[{"title":i.title,"weight":i.weight,"earned":i.weight if i.status=="complete" else 0,"status":i.status} for i in items]}
@router.get("/partners/{partner_id}/checklist")
def checklist(partner_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)): scope_partner(user,partner_id);return db.scalars(select(ChecklistItem).where(ChecklistItem.partner_id==partner_id)).all()
@router.patch("/checklist-items/{item_id}")
def patch_checklist(item_id:int,body:ChecklistPatch,db:Session=Depends(get_db),user:User=Depends(current_user)):
    i=db.get(ChecklistItem,item_id)
    if not i:raise HTTPException(404,"Checklist item not found")
    scope_partner(user,i.partner_id)
    if body.status not in ("pending","blocked","complete"):raise HTTPException(422,"Invalid checklist status")
    i.status=body.status;audit(db,user,"checklist.updated","checklist_item",i.id,i.partner_id,{"status":body.status});db.commit();update_readiness(db,i.partner_id);return i
@router.post("/partners/{partner_id}/webhooks")
def create_webhook(partner_id:int,body:WebhookIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    scope_partner(user,partner_id)
    if not (body.url.startswith("http://webhook-simulator") or body.url.startswith("http://localhost")):raise HTTPException(422,"Demo webhooks are restricted to the internal simulator or localhost")
    secret=secrets.token_urlsafe(24);w=Webhook(partner_id=partner_id,url=body.url,secret_hash=hashlib.sha256(secret.encode()).hexdigest());db.add(w);db.commit();return {"id":w.id,"url":w.url,"signing_secret":secret,"notice":"This secret is shown once."}
@router.post("/webhooks/{webhook_id}/test")
def test_webhook(webhook_id:int,simulate:str="success",db:Session=Depends(get_db),user:User=Depends(current_user)):
    w=db.get(Webhook,webhook_id)
    if not w:raise HTTPException(404,"Webhook not found")
    scope_partner(user,w.partner_id);status="succeeded" if simulate=="success" else "failed";d=Delivery(webhook_id=w.id,event_type="endpoint.test",status=status,attempt_count=1,response_status=204 if status=="succeeded" else 500);db.add(d);audit(db,user,"webhook.test","webhook",w.id,w.partner_id,{"simulated":True,"outcome":status});db.commit();return d
@router.get("/operations/dashboard")
def operations(db:Session=Depends(get_db),user:User=Depends(require(Role.platform_operator,Role.platform_admin))):
    total=db.scalar(select(func.count(Partner.id))) or 0; ready=db.scalar(select(func.count(Partner.id)).where(Partner.status=="launch_ready")) or 0; subs=db.scalar(select(func.count(Submission.id))) or 0; ok=db.scalar(select(func.count(Submission.id)).where(Submission.status=="succeeded")) or 0
    categories=db.execute(select(Issue.category,func.count(Issue.id)).group_by(Issue.category).order_by(func.count(Issue.id).desc())).all()
    return {"total_partners":total,"launch_ready":ready,"blocked":db.scalar(select(func.count(Partner.id)).where(Partner.status=="action_required")) or 0,"submissions":subs,"validation_success_rate":round(ok/subs*100,1) if subs else 0,"errors_by_category":[{"category":x,"count":n} for x,n in categories]}
@router.get("/analytics/overview")
def analytics(db:Session=Depends(get_db),user:User=Depends(require(Role.platform_operator,Role.platform_admin))):
    codes=db.execute(select(Issue.code,func.count(Issue.id)).group_by(Issue.code).order_by(func.count(Issue.id).desc()).limit(10)).all();retries=db.execute(select(Partner.name,func.sum(Submission.retry_count)).join(Submission,Submission.partner_id==Partner.id).group_by(Partner.id).order_by(func.sum(Submission.retry_count).desc())).all();return {"frequent_errors":[{"code":c,"count":n} for c,n in codes],"retries_by_partner":[{"partner":p,"retries":n or 0} for p,n in retries]}
@router.get("/docs")
def docs(q:str|None=None,db:Session=Depends(get_db),user:User=Depends(current_user)):
    query=select(DocPage).where(DocPage.published==True)
    if q:query=query.where(or_(DocPage.title.ilike(f"%{q}%"),DocPage.content.ilike(f"%{q}%"),DocPage.summary.ilike(f"%{q}%")))
    return db.scalars(query.order_by(DocPage.title)).all()
@router.get("/docs/{slug}")
def doc(slug:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    page=db.scalar(select(DocPage).where(DocPage.slug==slug,DocPage.published==True))
    if not page:raise HTTPException(404,"Documentation page not found")
    return page
@router.get("/audit-events")
def audits(partner_id:int|None=None,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if user.partner_id:partner_id=user.partner_id
    q=select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100)
    if partner_id:q=q.where(AuditEvent.partner_id==partner_id)
    return db.scalars(q).all()

