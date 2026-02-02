from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# Minimal local SQLite engine for development/testing
engine = create_engine("sqlite:///./data.db", connect_args={"check_same_thread": False})

Base = declarative_base()
