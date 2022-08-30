from pydantic import BaseModel, EmailStr
from app.model.model import DateModel

class LoginModel(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "examplepassword"
            }
        }
    
class RegistedModel(BaseModel):
    name: str
    birthday: DateModel

    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "name": "First Name",
                "birthday": {
                    "year": 2005,
                    "month": 2,
                    "day": 18},
                "email": "user@example.com",
                "password": "examplepassword"
            }
        }