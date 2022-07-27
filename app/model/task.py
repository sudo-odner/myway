from typing import List
from pydantic import BaseModel
from app.model.model import DateModel, SessionModel
from app.model.statistic import DayStatistic

class IDResultModel(BaseModel):
    id: int

class DateModelmax(BaseModel):
    year: int = 9999
    month: int = 12
    day: int = 31
    hours: int = 23
    minute: int = 59

class DateModelmin(BaseModel):
    year: int = 1
    month: int = 1
    day: int = 1
    hours: int = 0
    minute: int = 0


# Задачи
class GetTaskModel(SessionModel):
    date_start: DateModelmin
    date_end: DateModelmax

class TaskResult(BaseModel):
    id: int
    task: str
    date: str
    image: str = "None"
    icon: str = "None"
    name_big_task: str = "None"
    big_task_id: int = -1
    completed: int

class ListTaskResult(BaseModel):
    list_result: List[TaskResult]

    class Config:
        schema_extra = {
            "example": {
                "list_result": [
                    {
                        "id": 4,
                        "task": "Pet the cat",
                        "image": "None",
                        "icon": "None",
                        "name_big_task": "None",
                        "big_task_id": -1,
                        "completed": 0
                    },
                    {
                        "id": 23,
                        "task": "Pet the cat",
                        "image": "/download-file?link=4aEM2ndsqEQer",
                        "icon": "🍙",
                        "name_big_task": "Лолка",
                        "big_task_id": 4,
                        "completed": 1
                    },
                    {
                        "id": 23,
                        "task": "Pet the cat",
                        "image": "None",
                        "icon": "🍙",
                        "name_big_task": "Лолка",
                        "big_task_id": 4,
                        "completed": 0
                    }
                ]
            }
        }


class AddTaskModel(SessionModel):
    task: str
    date: DateModel
    bigtask: int

    class Config:
        schema_extra = {
            "example": {
                "task": "Pet the cat",
                "date": {
                    "year": 2005,
                    "month": 2,
                    "day": 18,
                    "hours": 12,
                    "minute": 1},
                "big_task": -1
            }
        }


# Большие задачи
class BigTaskResult(BaseModel):
    id: int
    image: str
    icon: str
    name: str
    statistic: List[DayStatistic]

class ListBigTaskResult(BaseModel):
    list_result: List[BigTaskResult]
   
    class Config:
        schema_extra = {
            "example": {
                "list_result": [
                    {
                        "id": 4,
                        "image": "None",
                        "icon": "None",
                        "name": "None",
                        "statistic": [
                            {
                                "all": 1,
                                "done": 54,
                                "date": "date"
                            },
                            {
                                "all": 1,
                                "done": 54,
                                "date": "date"
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "image": "/download-file?link=4aEM2ndsqEQer",
                        "icon": "🍙",
                        "name_": "Лолка",
                        "statistic": [
                            {
                                "all": 1100,
                                "done": 54,
                                "date": "date"
                            },
                            {
                                "all": 234,
                                "done": 54,
                                "date": "date"
                            }
                        ]
                    },
                ]
            }
        }

class AddBigTaskModel(SessionModel):
    name: str
    icon: str
