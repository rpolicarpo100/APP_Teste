"""
Database connection — SQLite + SQLAlchemy
Robust version for Render disk persistence
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os

from app.config.settings import settings, ROOT_DIR

# Resolve DB path
db_url = settings.database_url
if db_url.startswith("sqlite"):
    db_path_str = db_url.replace("sqlite:///", "")
    db_path = Path(db_path_str)
    if not db_path.is_absolute():
        db_path = ROOT_DIR / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{db_path}"
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
    """Inicializa DB a partir do schema.sql — robusto para Render"""
    try:
        from pathlib import Path
        schema_path = Path(__file__).parent / "schema.sql"
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
                        raw_conn.rollback()
                        raw_conn.close()
                        # Tenta apagar DB corrompido e recriar
                        try:
                            db_path_str = settings.database_url.replace("sqlite:///", "")
                            db_path = Path(db_path_str)
                            if not db_path.is_absolute():
                                db_path = ROOT_DIR / db_path
                            if db_path.exists():
                                db_path.unlink()
                                print(f"[DB] DB corrompido apagado: {db_path}")
                            # Recria engine
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
