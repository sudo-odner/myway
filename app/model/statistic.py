from typing import List
from pydantic import BaseModel

class DayStatistic(BaseModel):
    all: int
    done: int
    date: str

class StatisticResult(BaseModel):
    personal_effectiveness: List[DayStatistic]
    not_personal_effectiveness: List[DayStatistic]

    class Config:
        schema_extra = {
            "example": {
                "personal_effectivenes": [
                    {
                        "all": 1,
                        "done": 54,
                        "date": "date"
                    },
                    {
                        "all": 1,
                        "done": 54,
                        "date": "date"
                    },
                    {
                        "all": 0,
                        "done": 0,
                        "date": "date"
                    }
                ],
                "not_personal_effectiveness": [
                    {
                        "all": 12,
                        "done": 12,
                        "date": "date"
                    },
                    {
                        "all": 43,
                        "done": 43,
                        "date": "date"
                    },
                    {
                        "all": 0,
                        "done": 0,
                        "date": "date"
                    }
                ]
            }
        }

class OneBigTaskStatistic(BaseModel):
    list_result: List[DayStatistic]