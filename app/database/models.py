"""
SQLAlchemy models — GOD Cerebro Core / Local AI Brain
Espelho do schema.sql para ORM opcional. MVP usa SQLite directo também.
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, func
from app.database.connection import Base

class Mission(Base):
    __tablename__ = "missions"
    id = Column(String, primary_key=True)
    objective = Column(Text, nullable=False)
    expected_result = Column(Text)
    context = Column(Text)
    constraints_text = Column(Text)
    priority = Column(String, default="medium")
    status = Column(String, default="PENDING")
    autonomy_level = Column(Integer, default=2)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    completed_at = Column(TIMESTAMP, nullable=True)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True)
    mission_id = Column(String)
    objective = Column(Text, nullable=False)
    description = Column(Text)
    agent_id = Column(String)
    required_skills = Column(Text)
    dependencies = Column(Text)
    priority = Column(String, default="medium")
    acceptance_criteria = Column(Text)
    risk = Column(String, default="low")
    required_tools = Column(Text)
    status = Column(String, default="PENDING")
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    result_summary = Column(Text)
    artifacts = Column(Text)
    evidence = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    specialty = Column(String, nullable=False)
    skills = Column(Text)
    tools = Column(Text)
    permissions = Column(Text)
    status = Column(String, default="IDLE")
    execution_type = Column(String, default="local")
    limitations = Column(Text)
    contract_version = Column(String, default="1.0.0")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class Tool(Base):
    __tablename__ = "tools"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    description = Column(Text)
    input_schema = Column(Text)
    output_schema = Column(Text)
    permissions = Column(Text)
    side_effects = Column(Text)
    risk_level = Column(String, default="LOW")
    status = Column(String, default="available")
    requires_approval = Column(Boolean, default=False)
    allowed_paths = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
