from fastapi import APIRouter, HTTPException
from app import DB, object_to_datetime

from app.db_setup import User_profile
from app.model.authorization import LoginModel, RegistedModel, SessionOutModel
from pydantic import EmailStr

import hashlib

router = APIRouter()

_hash = lambda x : hashlib.md5((x).encode()).hexdigest()

########################################################### Элементы при регистрации

# # Проверка регистрации пользователя
# @router.get("/cheak-email")
# def cheak_email(email: EmailStr):
#     if DB.get_first_filter(User_profile, search=(User_profile.email == email)) is not None:
#         raise HTTPException(status_code=406, detail="Почта зарегистрирована")

########################################################### Регистрация

@router.post("/registed", response_model=SessionOutModel)
def registed(_app: RegistedModel):
    if DB.get_first_filter(User_profile, search=(User_profile.email == _app.email)) is not None:
        raise HTTPException(status_code=423, detail="Почта зарегистрирована")
    
    date = object_to_datetime(_app.birthday)
    user_session = DB.new_user(email=_app.email, password=_app.password, name=_app.name, birthday=date)

    return SessionOutModel(session=user_session)

########################################################### Авторизация

@router.post("/login", response_model=SessionOutModel)
def login(_app: LoginModel):
    db_user = DB.get_first_filter(User_profile, search=(User_profile.email == _app.email))
    if user is None:
        raise HTTPException(status_code=423, detail="Пользователя с таким логином не найдено")
    if _hash(_app.password + user.salt) != user.hashpass:
        raise HTTPException(status_code=423, detail="Пароль не верный")
    
    user_session = DB.new_session(db_user.id)
    DB.time_update(user_session)
    
    return SessionOutModel(session=user_session)