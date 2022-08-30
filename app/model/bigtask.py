from typing import List
from pydantic import BaseModel

class GetBigTaskModel(BaseModel):
    session: str
    id: int = -1

class BigTaskModel(BaseModel):
    id: int
    icon: str
    name: str
    filelink: str

class ListBigTaskModel(BaseModel):
    result: List[BigTaskModel]


class AddBigTaskModel(BaseModel):
    session: str
    name: str
    icon: str