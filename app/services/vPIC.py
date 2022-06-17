from functools import cached_property
import httpx
from ..persistence.schemas import VINInfoGet


async def decode(vin: str) -> VINInfoGet:
    '''
    Use HTTPX library to decode vin data from vpic api
    https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/

    Refer to https://www.twilio.com/blog/asynchronous-http-requests-in-python-with-httpx-and-asyncio
    for httpx async usage
    '''

    url = 'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{}?format=json'.format(vin)

    # Catch possible exceptions from sending request to api 
    try:

        # Make call to API
        async with httpx.AsyncClient() as client:
            
            # Await response
            response = await client.get(url)
            vin_response = response.json()["Results"][0]

            # If error code is not 0 then something has gone wrong
            if(vin_response["ErrorCode"] != "0"):
                raise Exception("Unable to retrieve data for VIN: {}".format(vin))

            # Deserialize vin data into vin DTO
            vin_deserialzied = VINInfoGet(
                vin=vin_response["VIN"],
                make=vin_response["Make"], 
                model=vin_response["Model"], 
                model_year=vin_response["ModelYear"], 
                body_class=vin_response["BodyClass"], 
                cached_result=False)

            return vin_deserialzied

    except Exception as e:
        raise e