from fastapi import APIRouter
from time import time
from dotenv import load_dotenv

import httpx
import os
import hashlib

router = APIRouter()
CODEFORCES_API_URL = "https://codeforces.com/api/"
load_dotenv()

@router.get("/{contestId}")
async def get_contest(contestId: str):
    currentUnixTime = int(time())
    method = "contest.status"
    queryParams = [{"key": "contestId", "value": contestId}, {"key": "time", "value": currentUnixTime}, {"key": "apiKey", "value": os.getenv("CODEFORCES_KEY")}]
    
    signature = getApiSignature(queryParams, method)
    queryParams.append({"key": "apiSig", "value": signature})

    async with httpx.AsyncClient() as client:
        params = {param["key"]: param["value"] for param in queryParams}
        print(f"Params: {params}")
        
        response = await client.get(CODEFORCES_API_URL + method,params=params)
    
    return response.json()


def getApiSignature(queryParams : list, method : str):
    rand = "123456"
    secret = os.getenv("CODEFORCES_SECRET")
    
    filteredParams = [param for param in queryParams if param['key'] != 'apiSig']
    sortedParams = sorted(filteredParams, key=lambda x: (x['key'], x['value']))
    queryString = "&".join([f"{param['key']}={param['value']}" for param in sortedParams])

    stringToHash = f"{rand}/{method}?{queryString}#{secret}"
    hash = hashlib.sha512(stringToHash.encode('utf-8')).hexdigest()
    
    signature = f"{rand}{hash}"
    return signature
