from sqlalchemy.orm import Session
from app.persistence import models 
from models import schemas

'''
CRUD methods for the database session
'''

def get_by_vin(db: Session, vin_num: str) -> schemas.VINInfoBase | None:
    '''
    Get a VINInfoBase from the DB based on vin_num
    Returns None if it does not exist, otherwise returns VINInfoBase obj
    '''
    vin_model = db.query(models.VINInfo).filter(models.VINInfo.vin == vin_num).first()

    if vin_model is not None:
        return schemas.VINInfoBase(**vin_model.dict())

    return vin_model

# Create VIN
def create_vin(db: Session, vin: schemas.VINInfoBase) -> schemas.VINInfoBase | None:
    '''
    Create VIN
    Returns a VinInfoBase obj
    '''

    # Create vin model obj and pre set cached to true 
    vin_info = models.VINInfo( **vin.dict() )
    vin_info.cached_result = vin.cached_result= True

    # Add model and commit and refresh
    db.add(vin_info)
    db.commit()
    db.refresh(vin_info)

    # Return base class
    return vin

def delete_vin(db: Session, vin: str) -> bool:
    '''
    Try to delete a vin item from the DB
    Returns True or False
    '''

    # Try to delete item
    try:
        db.query(models.VINInfo).filter(vin=vin).delete()
        db.commit()

        return True
    except Exception as e:
        return False
