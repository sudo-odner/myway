from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from app.db_setup import User_session, engine
from app.db_use import DB_Activate
import datetime


# Working with the Database
DBSession = sessionmaker(engine)
DB = DB_Activate(DBSession)

# Convert json object to datetime
object_to_datetime = lambda x: datetime.datetime(x.year, x.month, x.day, x.hours, x.minute)

# Check if the session exists in the Database
def cheak_user_session(session):
    user_session = DB.get_first_filter(User_session, search=(User_session.session == session))
    if user_session == None:
        raise HTTPException(status_code=423, detail="Сессия неактивна или удалена из-за длительного периода бездействия")
    DB.time_update(user_session)

    return user_session