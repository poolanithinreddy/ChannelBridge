import os

os.environ["DATABASE_URL"]="sqlite:///:memory:"
from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Partner, Role, User


def setup_module():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        p=Partner(name="Test Partner",slug="test",status="draft",feed_type="json");db.add(p);db.flush();db.add_all([User(name="Partner",email="p@test.example",password_hash=hash_password("test-password"),role=Role.partner_admin,partner_id=p.id),User(name="Other",email="o@test.example",password_hash=hash_password("test-password"),role=Role.partner_admin,partner_id=None)]);db.commit()
def auth(email="p@test.example"):
    r=TestClient(app).post("/api/v1/auth/login",json={"email":email,"password":"test-password"});return {"Authorization":f"Bearer {r.json()['access_token']}"}
def test_health_and_auth():assert TestClient(app).get("/health").status_code==200;assert TestClient(app).get("/api/v1/auth/me",headers=auth()).status_code==200
def test_idempotency_and_report():
    c=TestClient(app);feed={"feed_version":"1.0","partner_id":"test","programs":[]};h={**auth(),"Idempotency-Key":"same"};a=c.post("/api/v1/partners/1/submissions/direct",json=feed,headers=h);b=c.post("/api/v1/partners/1/submissions/direct",json=feed,headers=h);assert a.status_code==200 and a.json()["id"]==b.json()["id"];assert c.post("/api/v1/partners/1/submissions/direct",json={**feed,"x":1},headers=h).status_code==409
def test_tenant_isolation():assert TestClient(app).get("/api/v1/partners/1",headers=auth("o@test.example")).status_code==403

