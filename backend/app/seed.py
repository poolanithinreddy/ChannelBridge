from datetime import datetime, timezone

from .auth import hash_password
from .database import Base, SessionLocal, engine
from .models import (
    AuditEvent,
    ChecklistItem,
    Contact,
    ContentProgram,
    Delivery,
    DocPage,
    Issue,
    Partner,
    Role,
    Submission,
    User,
    Webhook,
)

PARTNERS=[("Northstar Media","northstar-media","action_required","json",60),("Harborlight Studios","harborlight-studios","launch_ready","xml",100),("Cedar Peak Entertainment","cedar-peak","in_progress","json",45),("Blue Orbit Kids","blue-orbit-kids","action_required","xml",35),("Meridian Sports Network","meridian-sports","operational_review","json",80),("Lantern Documentary Group","lantern-docs","in_progress","xml",70),("Silverline Cinema","silverline-cinema","draft","json",10),("EchoWave Music Television","echowave-mtv","launch_ready","json",100)]
DOCS=[
 ("getting-started","Getting started","Submit your first synthetic catalog.","Choose JSON or XML version 1.0, use a unique idempotency key, upload, and poll its status.","guide"),
 ("feed-specification","Feed specification","ChannelBridge JSON and XML format.","The independent ChannelBridge 1.0 schema requires partner_id, generated_at, and programs. It does not represent any commercial platform.","reference"),
 ("validation-rules","Validation rule reference","Actionable error-code reference.","ID_REQUIRED blocks readiness: add a stable content_id. TERRITORY_INVALID blocks readiness: use a documented ISO-like code. ARTWORK_MISSING is a warning: add HTTPS 16:9 artwork. AVAILABILITY_ORDER blocks readiness: ensure ends_at is later than starts_at.","reference"),
 ("idempotency","Idempotency","Safely repeat feed requests.","Reuse a key only for the identical payload. An identical request returns the original submission; changed content returns HTTP 409.","integration"),
 ("webhooks","Webhook configuration","HMAC-signed simulated events.","Local callbacks use bounded exponential backoff. Public destinations are disabled in the educational demo to prevent SSRF.","integration"),
 ("troubleshooting","Common failure runbooks","Resolve malformed and invalid feeds.","Malformed XML is rejected by a hardened parser. Check version 1.0, required fields, availability ordering, identifiers, and artwork metadata.","runbook"),
]
STEPS=[("Organization configuration",10),("Technical contacts",10),("Valid feed submission",25),("No blocking validation errors",25),("Webhook verification",10),("Launch checklist",20)]
def seed():
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine)
    with SessionLocal() as db:
        partners=[]
        for name,slug,status,feed,score in PARTNERS:
            p=Partner(name=name,slug=slug,status=status,feed_type=feed,readiness_score=score);db.add(p);db.flush();partners.append(p)
            db.add(Contact(partner_id=p.id,name=f"{name.split()[0]} Integration Desk",email=f"integrations@{slug}.example",role="Technical lead",timezone="America/New_York"))
            earned=0
            for title,weight in STEPS:
                complete=earned+weight<=score;db.add(ChecklistItem(partner_id=p.id,category="launch_readiness",title=title,weight=weight,status="complete" if complete else "pending"));earned+=weight if complete else 0
        password=hash_password("ChannelBridgeDemo!")
        users=[User(name="Avery Partner",email="admin@northstar.example",password_hash=password,role=Role.partner_admin,partner_id=partners[0].id),User(name="Taylor Integrator",email="technical@northstar.example",password_hash=password,role=Role.partner_technical,partner_id=partners[0].id),User(name="Morgan Operator",email="operator@channelbridge.local",password_hash=password,role=Role.platform_operator),User(name="Jordan Admin",email="admin@channelbridge.local",password_hash=password,role=Role.platform_admin)]
        db.add_all(users)
        for slug,title,summary,content,cat in DOCS:db.add(DocPage(slug=slug,title=title,summary=summary,content=content,category=cat))
        db.commit()
        codes=[("ID_DUPLICATE_FEED","identifiers"),("ARTWORK_MISSING","artwork"),("TERRITORY_INVALID","language_territory"),("AVAILABILITY_ORDER","dates_timezones")]
        for idx,p in enumerate(partners):
            for record in range(15):
                episodic=record%3==0
                db.add(ContentProgram(partner_id=p.id,external_content_id=f"{p.slug[:3].upper()}-{'EP' if episodic else 'MOV'}-{record:03d}",program_type="episode" if episodic else "movie",title=f"Fictional Program {record+1}",description="A deterministic fictional catalog record for the ChannelBridge educational demo.",language="en-US",territory="US",artwork_url=None if record%7==0 else "https://example.invalid/synthetic.jpg",series_external_id=f"{p.slug[:3].upper()}-SER-001" if episodic else None,season_number=1 if episodic else None,episode_number=record+1 if episodic else None))
            for n in range(3):
                sub=Submission(partner_id=p.id,format=p.feed_type,source_filename=f"catalog-{n+1}.{p.feed_type}",storage_key="seed/demo",content_hash=f"{idx:02}{n:02}".ljust(64,"0"),idempotency_key=f"seed-{idx}-{n}",status="succeeded" if n==2 and idx%3 else "action_required",record_count=15,valid_record_count=12,invalid_record_count=3,retry_count=(idx+n)%3,completed_at=datetime.now(timezone.utc));db.add(sub);db.flush()
                if sub.status!="succeeded":
                    for j,(code,cat) in enumerate(codes[:(idx%4)+1]):db.add(Issue(submission_id=sub.id,program_external_id=f"{p.slug[:3].upper()}-{n}-{j}",row_number=j+1,field="metadata",category=cat,severity="error" if j!=1 else "warning",code=code,message=f"Synthetic {code.lower().replace('_',' ')} detected.",suggested_fix="Review the validation reference and correct this field.",fingerprint=f"{code}-{idx}-{j}".ljust(64,"0")[:64]))
            wh=Webhook(partner_id=p.id,url="http://webhook-simulator:8090/events",secret_hash="not-a-real-secret".ljust(64,"0"));db.add(wh);db.flush();db.add(Delivery(webhook_id=wh.id,event_type="validation.completed",status="failed" if idx%3==0 else "succeeded",attempt_count=3 if idx%3==0 else 1,response_status=500 if idx%3==0 else 204))
        db.add(AuditEvent(partner_id=partners[0].id,actor_id=users[0].id,action="demo.seeded",entity_type="system",entity_id="seed",metadata_json={"synthetic":True}));db.commit()
if __name__=="__main__":seed();print("Seeded 8 fictional partners and deterministic operational history.")
