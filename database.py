from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL


def prepare_url(url: str):
    """
    Accepts sqlite:///file.db or the postgres string from Neon / Render
    (postgres://... or postgresql://...). Returns (url_object, connect_args).
    Uses pg8000 (pure Python, nothing to compile).
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+pg8000://" + url[len("postgresql://"):]
    u = make_url(url)
    if u.drivername.startswith("sqlite"):
        return u, {"check_same_thread": False}
    # pg8000 does not understand these options in the URL; use SSL instead.
    query = {k: v for k, v in u.query.items() if k not in ("sslmode", "channel_binding", "options")}
    u = u.set(query=query)
    connect_args = {} if u.host in ("localhost", "127.0.0.1", None) else {"ssl_context": True}
    return u, connect_args


def make_engine(url: str):
    u, connect_args = prepare_url(url)
    kwargs = {}
    if not u.drivername.startswith("sqlite"):
        # Free online databases close idle connections: check before use.
        kwargs = dict(pool_pre_ping=True, pool_recycle=300, pool_size=3, max_overflow=2)
    return create_engine(u, echo=False, connect_args=connect_args, **kwargs)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import models  # noqa: F401  (registers tables)
    Base.metadata.create_all(bind=engine)
    # Older finebot_v2.db files have no "state" column yet: add it.
    cols = {c["name"] for c in inspect(engine).get_columns("users")}
    if "state" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN state TEXT"))
