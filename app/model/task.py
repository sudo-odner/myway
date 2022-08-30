from typing import List
from pydantic import BaseModel
from app.model.model import DateModel

class DateModelmin(BaseModel):
    year: int = 1
    month: int = 1
    day: int = 1
    hours: int = 0
    minute: int = 0

class DateModelmax(BaseModel):
    year: int = 9999
    month: int = 12
    day: int = 31
    hours: int = 23
    minute: int = 59

class GetTaskModel(BaseModel):
    session: str
    date_start: DateModelmin
    date_end: DateModelmax



class BigTaskModel(BaseModel):
    id: int
    icon: str
    name: str
    filelink: str = 'null'

class TaskModel(BaseModel):
    id: int
    bigtask: BigTaskModel = 'null'
    name: str
    date: str
    completed: bool

class ListTaskModel(BaseModel):
    result: List[TaskModel]



class AddTaskModel(BaseModel):
    task: str
    date: DateModel
    bigtask_id: int = None
    class Config:
        schema_extra = {
            "example": {
                "session": "Enter your session",
                "task": "Pet the cat",
                "date": {
                    "year": 2005,
                    "month": 2,
                    "day": 18,
                    "hours": 12,
                    "minute": 1},
                "bigtask": 342
            }
        }