from pydantic import BaseModel
from app.model.model import SessionModel

class IDResultModel(BaseModel):
    id: int

class ListResultModel(BaseModel):
    task: list


class AddTaskModel(SessionModel):
    task: str
    date: str
    bigtask: int

class AddBigTaskModel(SessionModel):
    name: str
    icon: str

class GetTaskModel(SessionModel):
    date_start: str
    date_end: str

class GetBigTaskModel(SessionModel):
    goal: int