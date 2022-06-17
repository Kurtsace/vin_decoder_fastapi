from sqlalchemy import Boolean, Column, String
from .database import Base


'''
VIN Info model class
Inherit from base SQLALCHEMY model for ORM functionality
'''
class VINInfo(Base):

    __tablename__ = "VINInfo"

    vin = Column(String, primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String, index=True)
    model_year = Column(String, index=True)
    body_class = Column(String, index=True)

    # Cached result defaults to false
    cached_result = Column(Boolean, index=True)