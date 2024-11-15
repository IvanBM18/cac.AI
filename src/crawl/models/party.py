from pydantic import BaseModel
from typing import Optional, List, Literal

class Member(BaseModel):
    handle: str
    name : Optional[str] = None

class Party(BaseModel):
    contestId: Optional[int] = None
    members: List[Member]
    participantType: Literal["CONTESTANT", "PRACTICE", "VIRTUAL", "MANAGER", "OUT_OF_COMPETITION"]
    teamId: Optional[int] = None
    teamName: Optional[str] = None
    ghost: bool
    room: Optional[int] = None
    startTimeSeconds: Optional[int] = None
