from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


class Base(DeclarativeBase): pass

kwargs = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
pool = {"poolclass": StaticPool} if settings.database_url == "sqlite:///:memory:" else {}
engine = create_engine(settings.database_url, connect_args=kwargs, pool_pre_ping=True, **pool)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_db():
    with SessionLocal() as db:
        yield db
