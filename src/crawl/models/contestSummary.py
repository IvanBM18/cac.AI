from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal, List

from .submission import SubmissionDTO,ContestDTO

class ContestSummary(BaseModel):
    contest : ContestDTO
    handle: str
    submissions: List[SubmissionDTO]