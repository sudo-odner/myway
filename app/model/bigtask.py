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

    class Config:
        schema_extra = {
            "example": {
                "result": [{"id": 1, "icon": "a", "name": "Dogs", "filelink": "/file?link=asdQ1345wswk213fafjmwqeffaSFwe"},
                {"id": 15, "icon": "a", "name": "Dogs", "filelink": "/file?link=asdQ1345wswk213fafjmwqeffaSFwe"}
                ]
            }
        }


class AddBigTaskModel(BaseModel):
    session: str
    name: str
    icon: str