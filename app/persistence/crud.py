import tempfile
from sqlalchemy.orm import Session
from fastparquet import write
import pandas as pd
from . import models, schemas

'''
CRUD methods for the database session
'''

async def get_by_vin(db: Session, vin_num: str) -> models.VINInfo:
    '''
    Get a VINInfo model obj from the DB based on vin_num
    Returns None if it does not exist, otherwise returns VINInfo model obj
    '''
    vin_model = db.query(models.VINInfo).filter(models.VINInfo.vin == vin_num).first()

    if vin_model is not None:
        return vin_model

    return None



async def delete_vin(db: Session, vin: str) -> bool:
    '''
    Try to delete a vin item from the DB
    Returns True or False
    '''

    # Try to delete item
    try:
        count = db.query(models.VINInfo).filter(models.VINInfo.vin == vin).delete()
        db.commit()

        return True if count > 0 else False
    except Exception as e:
        print("Error deleting vin from DB. {}".format(e))
        return False



async def create_vin(db: Session, vin: schemas.VINInfoBase) -> models.VINInfo:
    '''
    Create VIN
    Returns a VinInfo model obj
    '''

    # Create vin model obj and pre set cached to true 
    vin_info = models.VINInfo( **vin.dict() )
    vin_info.cached_result = True

    # Add model and commit and refresh
    try:
        db.add(vin_info)
        db.commit()
        db.refresh(vin_info)

        # Return base class
        return vin

    except Exception as e:
        print("Error saving vin to DB. {}".format(e))
        raise e



async def export_db(db: Session) -> list:
    '''
    Export the cache of VIN's as a list. 
    '''

    try:

        cache_list = db.query(models.VINInfo).with_entities(models.VINInfo.vin, models.VINInfo.make, models.VINInfo.model, models.VINInfo.model_year, models.VINInfo.body_class)
        return cache_list
    except Exception as e:
        raise e


async def db_to_parquet(db: Session) -> str:
    '''
    Export the list into a parquet file format.
    Returns a string of the path of the parquet file
    Use library called fastparquet.
    Refer to https://github.com/dask/fastparquet/
    '''

    try:
        
        # Filename 
        parq_file_name = tempfile.mkdtemp() + "/cache.parquet"

        # Grab the vins from the db 
        vin_list = await export_db(db)

        # Create pandas data frame 
        dataframe = pd.DataFrame(vin_list, columns=['vin', 'make', 'model', 'model_year', 'body_class'])

        # Write the file to a temp dir 
        write(parq_file_name, dataframe)

        return parq_file_name

    except Exception as e:
        raise e