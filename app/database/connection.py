"""
Database connection — SQLite + SQLAlchemy
VERIFICADO: Implementação simples para v1.0 conforme spec §14
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os

from app.config.settings import settings, ROOT_DIR

# Resolve DB path
db_url = settings.database_url
if db_url.startswith("sqlite"):
    # Extract path
    db_path_str = db_url.replace("sqlite:///", "")
    db_path = Path(db_path_str)
    if not db_path.is_absolute():
        db_path = ROOT_DIR / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{db_path}"
    # For SQLite, check_same_thread=False needed for FastAPI
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa DB a partir do schema.sql"""
    from pathlib import Path
    schema_path = Path(__file__).parent / "schema.sql"
    if schema_path.exists():
        # Use raw connection for schema.sql
        with engine.connect() as conn:
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
                # SQLite executescript via raw connection
                raw_conn = engine.raw_connection()
                try:
                    cursor = raw_conn.cursor()
                    cursor.executescript(sql_script)
                    raw_conn.commit()
                finally:
                    raw_conn.close()
    # Also create via SQLAlchemy metadata if models exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

def get_engine():
    return engine
