from fastapi import APIRouter
from time import time
from dotenv import load_dotenv
from pydantic import BaseModel
from .models.submission import Submission,formatDate,SubmissionDTO,ContestDTO
from .models.contestSummary import ContestSummary
import asyncio

import httpx
import os
import hashlib

router = APIRouter()
CODEFORCES_API_URL = "https://codeforces.com/api/"
load_dotenv()

@router.put("/contest/{contestId}")
async def crawl_contest(contestId: str):
    cacUrl = os.getenv("CAC_API_URL")
    contestToUpload = await get_contest(contestId)
     
    if(contestToUpload["result"] == []):
        return {"status": "FAILED", "message": "No se encontraron datos para el concurso"}
    
    result = [ContestSummary.model_validate(i).model_dump() for i in contestToUpload["result"]]
    print(f"Subiendo {len(result)} entradas de concurso {contestId} a CAC")
    async with httpx.AsyncClient() as client:
        response = await client.post( cacUrl + "/api/v1/submission/batch" ,json=result)
    
    return {"status": "OK", "message": "Datos subidos correctamente", "result": result}

@router.get("/{contestId}")
async def get_contest(contestId: str):
    
    contestStatus = await getContestStatus(contestId)
    if(contestStatus["status"] != "OK"):
        return {"status": "FAILED", "message": contestStatus.get("comment", "Unknown error"), "result": []}
    listProblems = [Submission.model_validate(submission) for submission in contestStatus["result"]]
    
    print("Esperando 2 segundos") #Espera de 2 segundos requerida desde la ultima vez que mandamos una peticion
    await asyncio.sleep(2)
    
    totalProblems = 0
    contestName = ""
    submissionsForUser = dict()
    problemDifficulty = dict()
    contestDto = None
    result = []
    contestStanding = await getContestStanding(contestId)
    if(contestStanding["status"] == "OK"):
        totalProblems = len(contestStanding["result"]["problems"])
        contestName = contestStanding["result"]["contest"]["name"]
        
        
    for i in listProblems:
        contestDto = ContestDTO(contestId = i.contestId, totalProblems = totalProblems, startDate = formatDate(i.creationTimeSeconds), resourceId = -1, name = contestName)
        
        
        for participant in i.author.members:
            if participant.handle not in submissionsForUser:
                submissionsForUser[participant.handle] = []
            submissionDto = SubmissionDTO(submissionId = i.id, problem = i.problem.index + " " + i.problem.name, verdict = i.verdict, penalty = 0, codeProfileId = -1, contestId = i.contestId)
            submissionsForUser[participant.handle].append(submissionDto)
            
        problemDifficulty[i.problem.index + " " + i.problem.name] = i.problem.rating if i.problem.rating != None else 0    
        
    contestDto.difficulty = int(sum(problemDifficulty.values())/len(problemDifficulty))
    
    for key in submissionsForUser:
        result.append(ContestSummary(contest = contestDto, handle = key, submissions = submissionsForUser[key]))
    
    return { "total": len(listProblems), "result": result }

async def getContestStatus(contestId : str) -> dict:
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

async def getContestStanding(contestId : str) -> dict:
    currentUnixTime = int(time())
    method = "contest.standings"
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
