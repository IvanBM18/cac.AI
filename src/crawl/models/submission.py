from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Literal
from .problem import Problem 
from .party import Party

class Submission(BaseModel):
    id: int
    contestId: Optional[int] = None
    creationTimeSeconds: int
    relativeTimeSeconds: int
    problem: Problem 
    author: Party    
    programmingLanguage: str
    verdict: Optional[Literal["FAILED", "OK", "PARTIAL", "COMPILATION_ERROR", "RUNTIME_ERROR", 
                              "WRONG_ANSWER", "PRESENTATION_ERROR", "TIME_LIMIT_EXCEEDED", 
                              "MEMORY_LIMIT_EXCEEDED", "IDLENESS_LIMIT_EXCEEDED", "SECURITY_VIOLATED", 
                              "CRASHED", "INPUT_PREPARATION_CRASHED", "CHALLENGED", "SKIPPED", 
                              "TESTING", "REJECTED"]] = None
    testset: Literal["SAMPLES", "PRETESTS", "TESTS", "CHALLENGES", "TESTS1", "TESTS2", 
                     "TESTS3", "TESTS4", "TESTS5", "TESTS6", "TESTS7", "TESTS8", 
                     "TESTS9", "TESTS10"]
    passedTestCount: int
    timeConsumedMillis: int
    memoryConsumedBytes: int
    points: Optional[float] = None
    
class SubmissionDTO(BaseModel):
    submissionId: Optional[int] = None 
    problem: str #Problem index + Problem name
    verdict: str 
    penalty: int = 0  #Empty
    codeProfileId: int #Empty
    contestId: int #Same as id in Submission
    
    
class ContestDTO(BaseModel):
    contestId: Optional[int] = None 
    totalProblems: int
    startDate: str = datetime.now().isoformat()  # Valor predeterminado como en el constructor Java
    resourceId: int
    difficulty: Optional[int] = None  # Puede ser None si no está presente
    name: str
    
    
def formatDate(uniTimestamp: int) -> datetime:
    dtObject = datetime.fromtimestamp(uniTimestamp, tz=timezone.utc)

    # Si necesitas en formato 'YYYY-MM-DD HH:MM:SS' (formato estándar de Oracle)
    formattedDate = dtObject.strftime('%Y-%m-%dT%H:%M:%S')

    return formattedDate

