from pydantic import BaseModel


'''
    Pydantic VIN Info schemas for requests 
    Acts as a DTO between the API and the DB
'''

class VINInfoBase(BaseModel):
    vin: str

class VINDelete(VINInfoBase):
    vin: str
    deleted_from_cache: bool = True

class VINInfoGet(VINInfoBase):
    vin: str
    make: str
    model: str
    model_year: str
    body_class: str

    # Cached result defaults to false
    cached_result: bool = False

    # Enable ORM mode to interface with SQLA ORM
    class Config:
        orm_mode = True