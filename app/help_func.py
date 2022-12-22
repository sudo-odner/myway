from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from app.db_setup import User_session, engine
from app.db_use import DB_Activate
from app import DB

import datetime
import hashlib

# # Работа с Базой Данных
# DBSession = sessionmaker(engine)
# DB = DBActivate(DBSession)

# Функция позволяет посмотерть что пришло в приложение
def print_element(data):
    nl_char = '\n\t'
    out = list()
    for item, value in data.items():
        if item != list(data.keys())[-1]:
            if type(value) == int:
                out.append(f"{item}: {value},")
            else:
                out.append(f"{item}: '{value}',")
        else:
            if type(value) == int:
                out.append(f"{item}: {value}")
            else:
                out.append(f"{item}: '{value}'")

    print('{\n\t' + nl_char.join(out) + "\n}")

# функция проверяющая существование сессии
def cheak_user_session(session):
    user_session = DB.get_first_filter(User_session, search=(User_session.session == session))
    if user_session == None:
        raise HTTPException(status_code=403, detail="The session is inactive or has been deleted due to a long period of inactivity")
    # DB.using_app(user_session)

    return user_session

# Функция конвертор из объекта в DateTime
object_to_datetime = lambda x: datetime.datetime(x.year, x.month, x.day, x.hours, x.minute)

# Функция хеширования
_hash = lambda x : hashlib.md5((x).encode()).hexdigest()

file_type = lambda x: (x.filename).split('.')[1]