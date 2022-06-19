from sqlite3 import connect
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# For prod/dev

# SQLITE db file path 
SQLALCHEMY_DATABASE_URL = "sqlite:///./vin.db"

# SQL engine 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# Database session 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM
Base = declarative_base()




# For Testing

# Test DB 
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_vin.db"

# SQL test engine 
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={'check_same_thread': False})

# Database test session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)