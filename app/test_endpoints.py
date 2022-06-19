import io
import pytest
import pandas as pd

from fastapi.testclient import TestClient
from persistence.models import Base
from persistence.schemas import VINInfoGet
from persistence.database import test_engine, TestSessionLocal
from main import app, get_db



########### TEST SET UP ###########

# get test DB
def get_db_test():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

# Override dependecy injection for DB
app.dependency_overrides[get_db] = get_db_test

# Test client 
client = TestClient(app)

Base.metadata.create_all(bind=test_engine)

@pytest.fixture()
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield 
    Base.metadata.drop_all(bind=test_engine)



########### BEGIN TESTS ###########

########### LOOKUP ENDPOINT TESTS ###########
def test_valid_vin_lookup(setup_db):
    '''
    Test valid vin number lookup via lookup endpoint. 
    First run will check for a non cache hit via vPIC 
    Second run will check for a cache hit via SQLITE 
    '''

    # VIN DTO
    vin_dto = VINInfoGet(
        vin='1XPWD40X1ED215307', 
        make='PETERBILT', 
        model='388', 
        model_year='2014', 
        body_class='Truck-Tractor', 
        cached_result=False)


    # First run
    # Get response 
    response = client.get('/lookup/{}'.format(vin_dto.vin))

    # Check response 
    assert response.status_code == 200

    # Should be the same as vin dto and not cached
    assert response.json() == vin_dto.dict()
    assert response.json()["cached_result"] == vin_dto.cached_result


    # Second run
    # Call endpoint again to test cache hit 
    response = client.get('/lookup/{}'.format(vin_dto.vin))

    # Check response 
    assert response.status_code == 200

    # Check cache hit and make sure the values still match
    vin_dto.cached_result = True
    assert response.json() == vin_dto.dict()


def test_invalid_vin_lookup(setup_db):
    '''
    Test a collection of invalid vins.
    Empty, less than 17 of a valid vin, more than 17 of a valid vin, illegal chars but 17 chars in len
    '''

    # Empty, less than 17 of a valid vin, more than 17 of a valid vin, illegal chars but 17 chars in len
    invalid_vins = ['', '1XPWD40X', '1XPWD40X1ED215307XXXXX', '!@#$%^&*()?><|[]/']

    # iterate through invalid vins 
    for invalid_vin in invalid_vins:

        # Get a response 
        response = client.get("/lookup/{}".format(invalid_vin))

        # status code should not be 200
        assert response.status_code != 200


def test_invalid_lookup_request(setup_db):
    '''
    Test sending the incorrect request headers but a valid vin to the endpoint /lookup.
    /lookup should only process GET requests 
    '''

    # POST request with a valid url and body
    request = client.post('/lookup/1XPWD40X1ED215307', json={'vin':'1XPWD40X1ED215307'})
    assert request.status_code == 405

    # DELETE request with a valid url and body
    request = client.delete('/lookup/1XPWD40X1ED215307', json={'vin':'1XPWD40X1ED215307'})
    assert request.status_code == 405

    # PUT request with a valid url and body
    request = client.put('/lookup/1XPWD40X1ED215307', json={'vin':'1XPWD40X1ED215307'})
    assert request.status_code == 405


########### REMOVE ENDPOINT TESTS ###########
def test_valid_vin_remove(setup_db):
    '''
    Test removal of a vin from the cache.
    Hit the lookup to add the valid vin to the cache and 
    then call the remove endpoint
    '''

    # VIN DTO
    vin_dto = VINInfoGet(
        vin='1XPWD40X1ED215307', 
        make='PETERBILT', 
        model='388', 
        model_year='2014', 
        body_class='Truck-Tractor', 
        cached_result=False)

    # Response types
    valid_response = {"VIN":vin_dto.vin, "cache_delete_success":True}
    invalid_response = {"VIN":vin_dto.vin, "cache_delete_success":False}

    # Try to remove the vin when it shouldnt exist 
    response = client.delete('/remove/{}'.format(vin_dto.vin))
    assert response.status_code == 200
    assert response.json() == invalid_response

    # Add the vin via lookup
    response = client.get('/lookup/{}'.format(vin_dto.vin))
    assert response.status_code == 200
    assert response.json() == vin_dto

    # Remove vin from cache 
    response = client.delete('/remove/{}'.format(vin_dto.vin))
    assert response.status_code == 200
    assert response.json() == valid_response


def test_invalid_vin_remove(setup_db):
    '''
    Test removal of a vin from the cache.
    Try to remove an invalid vin from the cache.
    Empty, non cached but valid, less than 17 of a valid vin, more than 17 of a valid vin, 
    illegal chars but 17 chars in len
    '''

    vins = ['', '1XPWD40X1ED215307', '1XPWD40X', '1XPWD40X1ED215307XXXXX', '!@#$%^&*()?><|[]/']

    # Iterate and test invalid endpoints
    for vin in vins:

        # Attempt to remove vin from cache 
        response = client.delete('/remove/{}'.format(vin))

        # key cache_delete_success should not be in the invalid responses but
        # should exist when a valid vin is sent but not in the cache
        assert ("cache_delete_success" not in response.json().keys()) or (response.json()["cache_delete_success"] == False)
    

def test_invalid_remove_request(setup_db):
    '''
    Test sending the incorrect request headers but a valid vin to the endpoint /remove.
    /remove should only process DELETE requests 
    '''

    # POST request with a valid url and body
    request = client.post('/remove/1XPWD40X1ED215307', json={'vin':'1XPWD40X1ED215307'})
    assert request.status_code == 405

    # GET request with a valid url and body
    request = client.get('/remove/1XPWD40X1ED215307', json={'vin':'1XPWD40X1ED215307'})
    assert request.status_code == 405

    # PUT request with a valid url and body
    request = client.put('/remove/1XPWD40X1ED215307', json={'vin':'1XPWD40X1ED215307'})
    assert request.status_code == 405


########### EXPORT ENDPOINT TESTS ###########
def test_export_single_parquet(setup_db):
    '''
    Test the export functionality. 
    '''

    # Cached VIN DTO
    vin_dto = VINInfoGet(
        vin='1XPWD40X1ED215307', 
        make='PETERBILT', 
        model='388', 
        model_year='2014', 
        body_class='Truck-Tractor')

    # Test to make sure the initial call to export with no entities exported is empty
    response = client.get('/export/')

    # Turn parquet response content bytes into dataframe
    pq_file = io.BytesIO(response._content)
    df = pd.read_parquet(pq_file, engine='fastparquet')

    # Should be empty
    assert df.empty == True
    
    
    # Test for a populated parquet with an entity

    # Add a VIN entity to the DB and export again
    response = client.get('/lookup/{}'.format(vin_dto.vin))
    assert response.status_code == 200
    
    # Remove cached_result key from the response then assert
    del response.json()['cached_result']
    assert response.json() == vin_dto.dict()

    # Turn parquet response content bytes into dataframe
    response = client.get('/export/')
    pq_file = io.BytesIO(response._content)
    df = pd.read_parquet(pq_file, engine='fastparquet')

    # Dataframe should not be empty
    assert df.empty == False

    # Get a list of vin entries as a dict from the dataframe
    # The only entry should be the same as the vin_dto obj
    vin_objs = df.to_dict(orient='records')

    # Remove the cahced_result key from the vin_dto since the parquet will not have that column
    # then assert for equality
    vin_dto_comp = vin_dto.dict()
    del vin_dto_comp['cached_result']
    assert vin_objs[0] == vin_dto_comp


def test_export_invalid_parquet(setup_db):
    '''
    Try to populate DB with invalid entries and then export.
    Empty, less than 17 of a valid vin, more than 17 of a valid vin, 
    illegal chars but 17 chars in len
    '''

    vins = ['', '1XPWD40X', '1XPWD40X1ED215307XXXXX', '!@#$%^&*()?><|[]/']

    for vin in vins:
        # Add invalid VIN entity to the DB and export
        response = client.get('/lookup/{}'.format(vin))

    # Turn parquet response content bytes into dataframe
    response = client.get('/export/')
    pq_file = io.BytesIO(response._content)
    df = pd.read_parquet(pq_file, engine='fastparquet')

    # Dataframe should be empty
    assert df.empty == True


def test_export_multiple_parquet(setup_db):
    '''
    Test the export functionality when given multiple entities.
    '''

    # Test to make sure the initial call to export with no entities exported is empty
    response = client.get('/export/')

    # Turn parquet response content bytes into dataframe
    pq_file = io.BytesIO(response._content)
    df = pd.read_parquet(pq_file, engine='fastparquet')

    # Should be empty
    assert df.empty == True
    
    
    # Populate cache with 5 valid VINs
    vins = ['1XPWD40X1ED215307', '1XKWDB0X57J211825', '1XP5DB9X7YN526158', '4V4NC9EJXEN171694', '1XP5DB9X7XD487964']
    returned_vins = []

    for vin in vins:
        # Add valid VIN entities to the DB and export again
        response = client.get('/lookup/{}'.format(vin))
        assert response.status_code == 200
    
        # Remove cached_result key from the response
        vin_obj = response.json()
        del vin_obj['cached_result']

        # Add entity returned to list of recieved vin dto's
        returned_vins.append(vin_obj)

    # Make sure all came back with a response 
    assert len(returned_vins) == len(vins)
    
    # Grab parquet from export endpoint and convert to DataFrame
    response = client.get('/export/')
    pq_file = io.BytesIO(response._content)
    df = pd.read_parquet(pq_file, engine='fastparquet')

    # Get a list of vin entries as a dict from the dataframe
    parquet_vins = df.to_dict(orient='records')

    # The count of entities within the parquet file should be the 
    # same as the count of returned vins
    assert len(returned_vins) == len(parquet_vins)

    # Make sure the dicts are the same for both returned_vins and parquet_vins from parquet
    # NO need to sort as the parquet vins and returned vins should be in the same order
    for vin1, vin2 in zip(returned_vins, parquet_vins):
        assert vin1 == vin2


def test_invalid_export_request(setup_db):
    '''
    Test sending the incorrect request headers to the endpoint /export.
    /export should only process GET requests 
    '''

    # POST request 
    request = client.post('/export')
    assert request.status_code == 405

    # DELETE request 
    request = client.delete('/export')
    assert request.status_code == 405

    # PUT request
    request = client.put('/export')
    assert request.status_code == 405