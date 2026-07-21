import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now(): return datetime.now(timezone.utc)
class Role(str, enum.Enum):
    partner_admin="partner_admin"; partner_technical="partner_technical"; platform_operator="platform_operator"; platform_admin="platform_admin"

class Partner(Base):
    __tablename__="partners"
    id: Mapped[int]=mapped_column(primary_key=True); name: Mapped[str]=mapped_column(String(120)); slug: Mapped[str]=mapped_column(String(80),unique=True,index=True)
    status: Mapped[str]=mapped_column(String(40),default="draft",index=True); feed_type: Mapped[str]=mapped_column(String(10),default="json")
    default_language: Mapped[str]=mapped_column(String(20),default="en-US"); default_territory: Mapped[str]=mapped_column(String(2),default="US")
    readiness_score: Mapped[int]=mapped_column(default=0); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class User(Base):
    __tablename__="users"; id: Mapped[int]=mapped_column(primary_key=True); partner_id: Mapped[int|None]=mapped_column(ForeignKey("partners.id"),nullable=True,index=True)
    name: Mapped[str]=mapped_column(String(100)); email: Mapped[str]=mapped_column(String(160),unique=True,index=True); password_hash: Mapped[str]=mapped_column(String(255)); role: Mapped[Role]=mapped_column(Enum(Role)); active: Mapped[bool]=mapped_column(Boolean,default=True)
class Contact(Base):
    __tablename__="contacts"; id: Mapped[int]=mapped_column(primary_key=True); partner_id: Mapped[int]=mapped_column(ForeignKey("partners.id"),index=True)
    name: Mapped[str]=mapped_column(String(100)); email: Mapped[str]=mapped_column(String(160)); role: Mapped[str]=mapped_column(String(80),default="Technical lead"); timezone: Mapped[str]=mapped_column(String(40),default="UTC"); active: Mapped[bool]=mapped_column(default=True)
class Submission(Base):
    __tablename__="submissions"; __table_args__=(UniqueConstraint("partner_id","idempotency_key"),Index("ix_submission_partner_received","partner_id","received_at"))
    id: Mapped[int]=mapped_column(primary_key=True); partner_id: Mapped[int]=mapped_column(ForeignKey("partners.id"),index=True); format: Mapped[str]=mapped_column(String(10)); source_filename: Mapped[str]=mapped_column(String(180)); storage_key: Mapped[str]=mapped_column(String(255)); content_hash: Mapped[str]=mapped_column(String(64),index=True); idempotency_key: Mapped[str]=mapped_column(String(120)); status: Mapped[str]=mapped_column(String(30),default="queued",index=True); received_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now); completed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); record_count: Mapped[int]=mapped_column(default=0); valid_record_count: Mapped[int]=mapped_column(default=0); invalid_record_count: Mapped[int]=mapped_column(default=0); retry_count: Mapped[int]=mapped_column(default=0); failure_reason: Mapped[str|None]=mapped_column(Text)
    issues: Mapped[list["Issue"]]=relationship(cascade="all, delete-orphan")
class ContentProgram(Base):
    __tablename__="content_programs"; __table_args__=(UniqueConstraint("partner_id","external_content_id"),Index("ix_program_partner_type","partner_id","program_type"))
    id: Mapped[int]=mapped_column(primary_key=True); partner_id: Mapped[int]=mapped_column(ForeignKey("partners.id"),index=True); external_content_id: Mapped[str]=mapped_column(String(120)); program_type: Mapped[str]=mapped_column(String(20)); title: Mapped[str]=mapped_column(String(300)); description: Mapped[str]=mapped_column(Text); language: Mapped[str]=mapped_column(String(20)); territory: Mapped[str]=mapped_column(String(2)); artwork_url: Mapped[str|None]=mapped_column(String(500)); series_external_id: Mapped[str|None]=mapped_column(String(120)); season_number: Mapped[int|None]; episode_number: Mapped[int|None]; created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Issue(Base):
    __tablename__="issues"; id: Mapped[int]=mapped_column(primary_key=True); submission_id: Mapped[int]=mapped_column(ForeignKey("submissions.id"),index=True); program_external_id: Mapped[str|None]=mapped_column(String(120)); row_number: Mapped[int|None]; field: Mapped[str|None]=mapped_column(String(80)); category: Mapped[str]=mapped_column(String(50),index=True); severity: Mapped[str]=mapped_column(String(16),index=True); code: Mapped[str]=mapped_column(String(60),index=True); message: Mapped[str]=mapped_column(Text); suggested_fix: Mapped[str]=mapped_column(Text); fingerprint: Mapped[str]=mapped_column(String(64),index=True); resolved: Mapped[bool]=mapped_column(default=False)
class ChecklistItem(Base):
    __tablename__="checklist_items"; id: Mapped[int]=mapped_column(primary_key=True); partner_id: Mapped[int]=mapped_column(ForeignKey("partners.id"),index=True); category: Mapped[str]=mapped_column(String(50)); title: Mapped[str]=mapped_column(String(160)); weight: Mapped[int]; status: Mapped[str]=mapped_column(String(20),default="pending"); required: Mapped[bool]=mapped_column(default=True)
class Webhook(Base):
    __tablename__="webhooks"; id: Mapped[int]=mapped_column(primary_key=True); partner_id: Mapped[int]=mapped_column(ForeignKey("partners.id"),index=True); url: Mapped[str]=mapped_column(String(500)); secret_hash: Mapped[str]=mapped_column(String(64)); enabled: Mapped[bool]=mapped_column(default=True)
class Delivery(Base):
    __tablename__="deliveries"; id: Mapped[int]=mapped_column(primary_key=True); webhook_id: Mapped[int]=mapped_column(ForeignKey("webhooks.id"),index=True); event_type: Mapped[str]=mapped_column(String(80)); status: Mapped[str]=mapped_column(String(20)); attempt_count: Mapped[int]=mapped_column(default=0); response_status: Mapped[int|None]; created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class DocPage(Base):
    __tablename__="doc_pages"; id: Mapped[int]=mapped_column(primary_key=True); slug: Mapped[str]=mapped_column(String(100),unique=True); title: Mapped[str]=mapped_column(String(160)); summary: Mapped[str]=mapped_column(Text); content: Mapped[str]=mapped_column(Text); category: Mapped[str]=mapped_column(String(60)); published: Mapped[bool]=mapped_column(default=True)
class AuditEvent(Base):
    __tablename__="audit_events"; id: Mapped[int]=mapped_column(primary_key=True); partner_id: Mapped[int|None]=mapped_column(ForeignKey("partners.id"),index=True); actor_id: Mapped[int|None]=mapped_column(ForeignKey("users.id")); action: Mapped[str]=mapped_column(String(100),index=True); entity_type: Mapped[str]=mapped_column(String(60)); entity_id: Mapped[str]=mapped_column(String(60)); metadata_json: Mapped[dict]=mapped_column(JSON,default=dict); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
