from fastapi import FastAPI

from .persistence.database import engine, SessionLocal
from .persistence.models import Base, VINInfo

# Create DB tables 
VINInfo.metadata.create_all(bind=engine)

# Init application
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message":"Hello World"}
