from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .persistence.database import engine, SessionLocal
from .persistence.models import Base
from .persistence import crud
from .services import vPIC

# Create DB tables 
Base.metadata.create_all(bind=engine)

# Init application
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#################### ENDPOINTS ####################
@app.get('/')
def index():
    '''
    Redirect index to docs for convenience
    '''
    return RedirectResponse('/docs')


@app.get("/lookup/{vin}")
async def lookup(db: Session = Depends(get_db), vin: str = Path(regex="^[A-Za-z0-9]{17}$")):
    '''
    Query cache for vin number or call vPIC api for response.
    Takes: vin str that is 17 characters in len exactly
    '''

    try:
        # Check cache if vin exists
        vin_dto = await crud.get_by_vin(db, vin_num=vin)

        # If VIN exists return the cached result
        if vin_dto is not None:
            return vin_dto

        # Query vPIC API for VIN record 
        vin_dto = await vPIC.decode(vin=vin)

        # If we have a valid response from the api
        if vin_dto is not None:

            # Save VIN record for future use in cache
            await crud.create_vin(db, vin_dto)

            # Return the VIN DTO as a response
            return vin_dto
        
        else:
            raise Exception("Unable to retrieve vin from API")

    except Exception as e:
        print(e)
        return HTTPException(status_code=400, detail="Unable to lookup vin: {}".format(vin))

@app.delete("/remove/{vin}")
async def remove(db: Session = Depends(get_db), vin: str = Path(regex="^[A-Za-z0-9]{17}$")):
    
    '''
    Delete VIN record from cache if it exists
    Takes: vin str that is 17 characters in len exactly
    '''

    try:
        
        # Try to delete VIN
        result = await crud.delete_vin(db, vin)

        # If successful return a valid response
        if result:
            return {"VIN":vin, "cache_delete_success":result}
        
        else:
            raise Exception("Unable to delete vin")

    except Exception as e:
        print(e)
        return {"VIN":vin, "cache_delete_success":False}