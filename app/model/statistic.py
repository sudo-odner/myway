from pydantic import BaseModel

class StatisticModel(BaseModel):
    session: int

class StatisticBigTaskModel(StatisticModel):
    id: int

class ResultStatisticBigTaskModel(BaseModel):
    completed_bigtask: list
    all_bigtask: list

class ResultStatisticModel(BaseModel):
    completed_bigtask: list
    all_bigtask: list
    completed_task: list
    all_task: list