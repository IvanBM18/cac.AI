from pydantic import BaseModel
from typing import Optional, Literal, List

class Problem(BaseModel):
    contestId: Optional[int] = None
    problemsetName: Optional[str] = None
    index: str
    name: str
    type: Literal["PROGRAMMING", "QUESTION"]
    points: Optional[float] = None
    rating: Optional[int] = None
    tags: Optional[List[str]] = None
