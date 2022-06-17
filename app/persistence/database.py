from sqlite3 import connect
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# SQLITE db file path 
SQLALCHEMY_DATABASE_URL = "sqlite:///app/persistence/vin.db"

# SQL engine 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# Database session 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM
Base = declarative_base()