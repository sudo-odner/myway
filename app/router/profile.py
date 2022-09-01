from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlalchemy.orm import sessionmaker

from app.db_setup import User, engine
from app.db_use import DBActivate

from app.model.profile import EditProfileModel, ProfileModel

from app.help_func import object_to_datetime, cheak_user_session, file_type
import shutil

router = APIRouter()

# Работа с Базой Данных
DBSession = sessionmaker(engine)
DB = DBActivate(DBSession)


########################################################### Загрузка файла в профиль

@router.put("/upload-file")
def upload_file_profile(session: str, file: UploadFile = File(...)):
    user_session = cheak_user_session(session)
    
    way = f"./app/file/user/{user_session.user_id}.{file_type(file)}"
    
    with open(way, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    DB.update(User, search=(User.id == user_session.user_id), reload={"filelink": way})


########################################################### Получение профиля

@router.get("/get-profile", response_model=ProfileModel)
def get_profile(session: str):
    user_session = cheak_user_session(session)
    user = DB.get_first_filter(User, search=(User.id == user_session.user_id))
    
    if user.filelink != None:
        user.filelink = DB.getlinkimage(user.filelink)
    return ProfileModel(**user)


########################################################### Изменнение профиля

@router.get("/edit-profile")
def get_profile(_app: EditProfileModel):
    user_session = cheak_user_session(_app.session)
    user = DB.get_first_filter(User, search=(User.id == user_session.user_id))

    if _app.email != None:
        if DB.get_first_filter(User, search=(User.email == _app.email)) is not None:
            raise HTTPException(status_code=423, detail="Email is registed")
        DB.update(User, search=(User.id == user.id), reload={"email": _app.email})
    if _app.name != None:
        DB.update(User, search=(User.id == user.id), reload={"name": _app.name})
    if _app.birthday != None:
        DB.update(User, search=(User.id == user.id), reload={"birthday": object_to_datetime(_app.birthday)})