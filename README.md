# vin_decoder_fastapi
Implement a simple FastAPI backend to decode VINs, powered by the vPIC API and backed by a SQLite cache.

## To Run App

### With Python/Uvicorn
Install requirements with 
```
pip install -r requirements.txt
```

Run 
```
uvicorn app.main:app --reload
```

OR 
```
python3 main.py
```

### With Docker
Build the image with 
```
docker build -t vpic_app .
```

Run the image with port setting 
```
docker run -p 8000:8000 vpic_app
```


## To Run Tests

Run 
```
pytest -v
```


# Endpoints

## /lookup/{vin}

This route will first check the SQLite database to see if a cached result is available. If so, it will be returned from the database.

If not, the API will contact the vPIC API to decode the VIN, store the results in the database, and return the result.

The request should contain a single string called "vin". It should contain exactly 17 alphanumeric characters.

The response object will contain the following elements:

    Input VIN Requested (string, exactly 17 alphanumeric characters)
    Make (String)
    Model (String)
    Model Year (String)
    Body Class (String)
    Cached Result? (Boolean)


## /remove/{vin}

This route will remove a entry from the cache.

The request should contain a single string called "vin". It should contain exactly 17 alphanumeric characters.

The response object will contain the following elements:

    Input VIN Requested (string, exactly 17 alphanumeric characters)
    Cache Delete Success? (boolean)


## /export

This route will export the SQLite database cache and return a binary file (parquet format) containing the data in the cache.

The response object will be a binary file downloaded by the client containing all currently cached VINs in a table stored in parquet format.
