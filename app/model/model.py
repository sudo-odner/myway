from pydantic import BaseModel

class IDResult(BaseModel):
    id: int

class SessionModel(BaseModel):
    session: str

class SessionAndID(BaseModel):
    session: str
    id: int

class DateModel(BaseModel):
    year: int = 1
    month: int = 1
    day: int = 1
    hours: int = 0
    minute: int = 0
