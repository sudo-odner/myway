from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from app.db_setup import BigTask, engine
from app.db_use import DB_Activate

from app.model.bigtask import AddBigTaskModel, GetBigTaskModel, ListBigTaskModel
from app.model.model import IDResult, SessionAndID

from app.help_func import cheak_user_session, file_type
import shutil

router = APIRouter()

# Работа с Базой Данных
DBSession = sessionmaker(engine)
DB = DB_Activate(DBSession)


########################################################### Загрузка файла к большой цели

@router.put("/upload-file")
def upload_file_profile(session: str, id: int, file: UploadFile = File(...)):
    user_session = cheak_user_session(session)

    if DB.get_first_filter(BigTask, search=(BigTask.id == id)) == None or user_session.user_id != (DB.get_first_filter(BigTask, search=(BigTask.id == id))).user_id:
        raise HTTPException(status_code=404, detail='Such target does not exist or is not available')
    
    way = f"./app/file/bigtask/{user_session.user_id}.{file_type(file)}"
    
    with open(way, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    DB.update(BigTask, search=(BigTask.id == id), reload={"filelink": way})


########################################################### Получение большой цели по времени

@router.get('/get-bigtask', response_model=ListBigTaskModel)
def get_task(_app: GetBigTaskModel):
    user_session = cheak_user_session(_app.session)

    bigtasks = DB.get_bigtask(user_session.user_id, _app.id)
    return ListBigTaskModel(result=bigtasks)


########################################################### Добавление большой цели

@router.post('/add-bigtask', response_model=IDResult)
def add_bigtask(_app: AddBigTaskModel):
    user_session = cheak_user_session(_app.session)
    
    bigtask_id = DB.add(BigTask(user_id=user_session.user_id, name=_app.name, icon=_app.icon))
    return IDResult(id=bigtask_id)


########################################################### Удаление большой цели

@router.delete('/deleted-bigtask')
def deleted_task(_app: SessionAndID):
    user_session = cheak_user_session(_app.session)

    if DB.get_first_filter(BigTask, search=(and_(BigTask.id == _app.id, BigTask.user_id == user_session.user_id))) is None:
        raise HTTPException(status_code=404, detail='Such target does not exist or is not available')
    
    DB.dell(BigTask, search=(and_(BigTask.id == id, BigTask.user_id == user_session.user_id)))