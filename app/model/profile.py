from app.model.model import DateModel
from pydantic import BaseModel, EmailStr

class ProfileModel(BaseModel):
    name: str
    email: EmailStr
    birthday: DateModel
    user_file: str

    class Config:
        schema_extra  = {
            'example': {
                'name': 'Pidor',
                'email': 'pigor@podors.com',
                'birthay': 'date',
                'user_file_link': '/file?link=aboba'
            }
        }

class EditProfileModel(BaseModel):
    session: str
    name: str = None
    email: EmailStr = None
    birthday: DateModel = None

    class Config:
        schema_extra = {
            "example": {
                "session": "asf5GSD2efasf23asdfgV8AFVRdsv3213dgsRA",
                "name": "Kirill",
                'email': 'aboba@example.com',
                "birthday": {
                    "year": 2005,
                    "month": 2,
                    "day": 18},
            }
        }