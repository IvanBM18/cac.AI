from pydantic import BaseModel
from typing import Optional

class ContestData(BaseModel):
    name : str
    total: Optional[int] = None
    correct: Optional[float] = None
    difficulty: float
