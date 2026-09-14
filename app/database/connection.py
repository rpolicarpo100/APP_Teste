"""
Database connection — SQLite + Postgres + Turso support
Robust version for Render + zero-cost alternatives (Neon, Supabase, Turso)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os

from app.config.settings import settings, ROOT_DIR

# Resolve DB path — supports DATABASE_URL env override for zero-cost alternatives
# Priority: DATABASE_URL env var > settings.database_url
db_url = os.getenv('DATABASE_URL') or settings.database_url

# Fix postgres:// -> postgresql:// for SQLAlchemy + psycopg2 compatibility
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

# Handle Turso libSQL — if URL starts with libsql://, convert to sqlite+libsql:// for SQLAlchemy
# Turso free tier: 5GB, no card, HTTP based
if db_url.startswith('libsql://'):
    # Requires sqlalchemy-libsql, fallback to http client if not available
    try:
        db_url = db_url.replace('libsql://', 'sqlite+libsql://', 1)
        engine = create_engine(db_url)
    except Exception as e:
        print(f"[DB] Turso libSQL driver not available: {e} — falling back to SQLite")
        db_url = settings.database_url
        db_path_str = db_url.replace("sqlite:///", "")
        db_path = Path(db_path_str)
        if not db_path.is_absolute():
            db_path = ROOT_DIR / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
elif db_url.startswith("sqlite"):
    db_path_str = db_url.replace("sqlite:///", "")
    db_path = Path(db_path_str)
    if not db_path.is_absolute():
        db_path = ROOT_DIR / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    # Postgres (Neon, Supabase, Render Postgres) — zero-cost alternatives
    # Neon: 0.5GB free, no card, scale to zero
    # Supabase: 500MB free, no card, pauses after 1 week
    # Render Postgres Free: 1GB, expires 30 days, no card
    try:
        engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
    except Exception as e:
        print(f"[DB] Postgres engine failed: {e} — falling back to SQLite")
        db_path_str = settings.database_url.replace("sqlite:///", "")
        db_path = Path(db_path_str)
        if not db_path.is_absolute():
            db_path = ROOT_DIR / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa DB a partir do schema.sql — robusto para Render + zero-cost"""
    try:
        from pathlib import Path
        schema_path = Path(__file__).parent / "schema.sql"
        # For Postgres, skip raw sqlite executescript and use SQLAlchemy metadata
        if not db_url.startswith("sqlite"):
            try:
                Base.metadata.create_all(bind=engine)
                print(f"[DB] Postgres init OK via Base.metadata.create_all")
            except Exception as e:
                print(f"[DB] Postgres Base.metadata.create_all failed: {e}")
            return

        if schema_path.exists():
            with engine.connect() as conn:
                with open(schema_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                    raw_conn = engine.raw_connection()
                    try:
                        cursor = raw_conn.cursor()
                        cursor.executescript(sql_script)
                        raw_conn.commit()
                    except Exception as e:
                        print(f"[DB] schema.sql failed: {e} — tentando recriar DB")
                        try:
                            raw_conn.rollback()
                        except:
                            pass
                        try:
                            raw_conn.close()
                        except:
                            pass
                        try:
                            db_path_str = settings.database_url.replace("sqlite:///", "")
                            db_path = Path(db_path_str)
                            if not db_path.is_absolute():
                                db_path = ROOT_DIR / db_path
                            if db_path.exists():
                                db_path.unlink()
                                print(f"[DB] DB corrompido apagado: {db_path}")
                            db_path.parent.mkdir(parents=True, exist_ok=True)
                            raw_conn2 = engine.raw_connection()
                            cursor2 = raw_conn2.cursor()
                            cursor2.executescript(sql_script)
                            raw_conn2.commit()
                            raw_conn2.close()
                        except Exception as e2:
                            print(f"[DB] Falha ao recriar: {e2}")
                    finally:
                        try:
                            raw_conn.close()
                        except:
                            pass
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print(f"[DB] Base.metadata.create_all failed: {e}")
    except Exception as e:
        print(f"[DB] init_db geral falhou: {e} — continua mesmo assim")

def get_engine():
    return engine

def get_db_type():
    """Retorna tipo de DB atual para debug"""
    if db_url.startswith("sqlite"):
        return "sqlite"
    elif "neon" in db_url:
        return "neon"
    elif "supabase" in db_url:
        return "supabase"
    elif "render" in db_url and "postgres" in db_url:
        return "render_postgres"
    elif db_url.startswith("postgresql"):
        return "postgres"
    elif "libsql" in db_url or "turso" in db_url:
        return "turso"
    else:
        return "unknown"
