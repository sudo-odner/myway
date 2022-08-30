from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import sessionmaker

from app.db_setup import User, engine
from app.db_use import DBActivate

from app.model.model import SessionID
from app.model.authorization import LoginModel, RegistedModel

from pydantic import EmailStr
from app.help_func import object_to_datetime, _hash

router = APIRouter()

# Работа с Базой Данных
DBSession = sessionmaker(engine)
DB = DBActivate(DBSession)


########################################################### Элементы при регистрации

# Проверка регистрации пользователя
@router.get("/cheak-email")
def cheak_email(email: EmailStr):
    if DB.get_first_filter(User, search=(User.email == email)) is not None:
        raise HTTPException(status_code=403, detail="Email is registed")


########################################################### Регистрация

@router.post("/registed", response_model=SessionID)
def registed(_app:RegistedModel):
    if DB.get_first_filter(User, search=(User.email == _app.email)) is not None:
        raise HTTPException(status_code=423, detail="This mail is registered")
    
    date = object_to_datetime(_app.birthday)
    user_id = DB.new_user(email=_app.email, password=_app.password, name=_app.name, birthday=date)

    return SessionID(session=(DB.new_session(user_id, "patient")).session)

########################################################### Авторизация

@router.post("/login", response_model=SessionID)
def login(_app: LoginModel):
    user = DB.get_first_filter(User, search=(User.email == _app.email))
    if user is None:
        raise HTTPException(status_code=404, detail="This mail is not registered") # Изменить ошибку
    
    if _hash(_app.password + user.salt) != user.password:
        raise HTTPException(status_code=423, detail="Wrong password")
    
    user_session = DB.new_session(user.id, user.role)
    DB.using_app(user_session)
    
    return SessionID(session=user_session.session)