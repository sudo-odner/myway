from fastapi import APIRouter, HTTPException, UploadFile, File
import shutil
from app.db_setup import User_profile
from app import DB, object_to_datetime, cheak_user_session
from app.model.profile import EditProfileModel, ProfileModel


router = APIRouter()
########################################################### Загрузка файла в профиль
@router.put("/upload-file")
def upload_file_profile(session: str, file: UploadFile = File(...)):
    user_session = cheak_user_session(session)
    
    way = f"./app/file/user/{user_session.user_id}.{file.content_type}"
    
    with open(way, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    DB.update(User_profile, search=(User_profile.id == user_session.user_id), reload={"user_file": way})
    
########################################################### Получение профиля
@router.get("/get-profile", response_model=ProfileModel)
def get_profile(session: str):
    user_session = cheak_user_session(session)
    user = DB.get_first_filter(User_profile, search=(User_profile.id == user_session.user_id))
    
    if user.user_file != None:
        user.user_file = DB.getlinkimage(user.user_file)
    return ProfileModel(**user)

########################################################### Изменнение профиля
@router.get("/edit-profile")
def get_profile(_app: EditProfileModel):
    user_session = cheak_user_session(_app.session)
    user = DB.get_first_filter(User_profile, search=(User_profile.id == user_session.user_id))

    if _app.email != None:
        if DB.get_first_filter(User_profile, search=(User_profile.email == _app.email)) is not None:
            raise HTTPException(status_code=423, detail="Почта зарегестрирована")
        DB.update(User_profile, search=(User_profile.id == user.id), reload={"email": _app.email})
    if _app.name != None:
        DB.update(User_profile, search=(User_profile.id == user.id), reload={"name": _app.name})
    if _app.birthday != None:
        DB.update(User_profile, search=(User_profile.id == user.id), reload={"birthday": object_to_datetime(_app.birthday)})