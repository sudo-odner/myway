import fastapi
from fastapi.responses import FileResponse
from sqlalchemy.orm import sessionmaker

from app.model.model import SessionModel, UserModel,  AuthorizationModel, RegistedModel,  CompletedModel
from app.model.task import AddBigTaskModel, AddTaskModel, GetBigTaskModel, GetTaskModel, IDResultModel, ListResultModel
from app.model.statistic import StatisticModel, ResultStatisticModel, StatisticBigTaskModel, ResultStatisticBigTaskModel

from app.db_setup import TimeLinkGetImage, engine, Auth, Auth_session, Task, BigTask, Completed_bigtask, Completed_all

from app.http_err import forbidden, locked, bad_request, not_acceptable, not_found, unauthorized

import datetime
import re
import hashlib

from app.db_use import DBActivate

import shutil

user_profile_setting = 'name email '.split(' ')

app = fastapi.FastAPI()

_hash = lambda x : hashlib.md5((x).encode()).hexdigest()
_image = lambda j : " ".join(map(lambda x: str(x), j))

# Проверка пользователя
def check_user(_app):
    user_session = DB.get(Auth_session, Auth_session.session, _app.session)
    unauthorized(
        conditions=user_session is None,
        detail="Session is not exists"
    )
    return user_session

# Подключение БД
DBSession = sessionmaker(engine)
DB = DBActivate(DBSession)

@app.post("/upload_big_task")
async def upload_big_task(session: str, idd: str, file: fastapi.UploadFile = fastapi.File(...)):
    user_session = DB.get(Auth_session, Auth_session.session, session)
    unauthorized(
        conditions=user_session is None,
        detail="Session is not exists"
    )

    forbidden(
        conditions=user_session.user_id != (DB.get(BigTask, BigTask.id, idd)).user_id,
        detail="Forbidden"
    )

    with open(f"./app/image/big_task/{idd}.jpeg", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    DB.add_image(BigTask, BigTask.id, idd, f"./app/image/bit_task/{idd}.jpeg")
    return {"message": True}

@app.post("/upload_image_profile")
async def upload_image_profile(session: str, file: fastapi.UploadFile = fastapi.File(...)):
    user_session = DB.get(Auth_session, Auth_session.session, session)
    unauthorized(
        conditions=user_session is None,
        detail="Session is not exists"
    )
    with open(f"./app/image/user/{user_session.user_id}.jpeg", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    DB.add_image(Auth, Auth.id, user_session.user_id, f"./app/image/user/{user_session.user_id}.jpeg")
    # return {description: 1}

    return {"message": True}

@app.post('/registed', response_model=SessionModel)
def registed(_app: RegistedModel):

    locked(
        conditions=DB.get(Auth, Auth.email, _app.email) is not None,
        detail="Login is registed")
    not_acceptable(
        conditions= not bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", _app.email)),
        detail="Email is not corect")
    
    user = DB.new_user(email=_app.email, password=_app.password, name=_app.name)

    return SessionModel(session=DB.new_session(user))

@app.post('/login', response_model=SessionModel)
def login(_app: AuthorizationModel):
    user = DB.get(Auth, Auth.email, _app.email)

    print(_app)
    unauthorized(
        conditions=user is None,
        detail="Login not found")
    locked(
        conditions=_hash(_app.password + user.salt) != user.hashpass,
        detail="Login is registed")
    
    return SessionModel(session=DB.new_session(user.id))

@app.post('/add_task', response_model=IDResultModel)
def add_task(_app: AddTaskModel):
    user_session = check_user(_app)
    print(_app)
    
    try:
        date = datetime.datetime.strptime(_app.date, '%d.%m.%Y %H:%M:%S')
    except:
        bad_request(detail="Date is not corect")
    
    bad_request(
        conditions=DB.get(BigTask, BigTask.id, _app.bigtask) is None and _app.bigtask != -1,
        detail="BigTask")
    
    if _app.bigtask != -1:
        locked(
            conditions=DB.get(BigTask, BigTask.id, _app.bigtask).user_id != user_session.user_id,
            detail="What?")

    task_id = DB.add(Task(user_id=user_session.user_id, task=_app.task, date=date, big_task_id=_app.bigtask, completed=0))

    if _app.bigtask != -1:
        DB.add(Completed_bigtask(user_id=user_session.user_id, date=date.date(), completed=0, task_id=task_id, bigtask_id=_app.bigtask))
    DB.add(Completed_all(user_id=user_session.user_id, date=date, completed=0, task_id=task_id))

    return IDResultModel(id=task_id)


@app.post('/get_task', response_model=ListResultModel)
def get_task(_app: GetTaskModel):
    user_session = check_user(_app)

    date_start, date_end = datetime.date(1, 1, 1), datetime.date(9999, 1, 1)

    if _app.date_start != "None":
        try:
            date_start = datetime.datetime.strptime(_app.date_start, '%d.%m.%Y %H:%M:%S')
        except:
            bad_request(detail="Bed Request date start")

    if _app.date_end != "None":
        try:
            date_end = datetime.datetime.strptime(_app.date_end, '%d.%m.%Y %H:%M:%S')
        except:
            bad_request(detail="Bed Request date end")
    
    tasks = DB.get_task(user_session.user_id, date_start, date_end)

    not_found(
        conditions=tasks is None,
        detail="Tasks not found")
    
    return ListResultModel(task=tasks)


@app.post('/add_bigtask', response_model=IDResultModel) #замутить чтот
def add_bigtask(_app:AddBigTaskModel):
    user_session = check_user(_app)

    id_big_task = BigTask(user_id=user_session.user_id, name=_app.name, icon=_app.icon)
    big_task = DB.add(id_big_task)
    return IDResultModel(id=id_big_task.id)


@app.post('/get_bigtask', response_model=ListResultModel)
def get_bigtask(_app:GetBigTaskModel):
    user_session = check_user(_app)
    
    tasks = DB.get_bigtask(user_session.user_id, _app.goal)
    return ListResultModel(task=tasks)


@app.post('/complite_task')
def complite_task(_app:CompletedModel):
    user_session = check_user(_app)

    forbidden(
        conditions=DB.get(Completed_bigtask, Completed_bigtask.task_id, _app.id_task).user_id != user_session.user_id,
        detail="Forbidden"
    )

    not_found(
        conditions=DB.get(Completed_bigtask, Completed_bigtask.task_id, _app.id_task) is None and DB.get(Completed_all, Completed_all.task_id, _app.id_task) is None,
        detail="Tasks not found")

    if DB.get(Completed_bigtask, Completed_bigtask.task_id, _app.id_task) is not None:
        DB.edit_complete_task(Completed_bigtask, Completed_bigtask.task_id, _app.id_task)

    DB.edit_complete_task(Completed_all, Completed_all.task_id, _app.id_task)
    return {"Out" : True}


@app.post('/get_statictic', response_model=ResultStatisticModel)
def statistic(_app:StatisticModel):
    user_session = check_user(_app)

    completed_bigtask = DB.set_statistic_copm(Completed_bigtask, Completed_bigtask.user_id, user_session.user_id)
    all_bigtask = DB.set_statistic_all(Completed_bigtask, Completed_bigtask.user_id, user_session.user_id)

    completed_task = DB.set_statistic_copm(Completed_all, Completed_all.user_id, user_session.user_id)
    all_task = DB.set_statistic_all(Completed_all, Completed_all.user_id, user_session.user_id)

    return ResultStatisticModel(
        completed_bigtask=completed_bigtask, 
        all_bigtask=all_bigtask,
        completed_task=completed_task,
        all_task=all_task
        )


@app.post('/get_statistic_big_task', response_model=ResultStatisticBigTaskModel)
def statistic_big_task(_app:StatisticBigTaskModel):
    user_session = check_user(_app)

    forbidden(
        conditions=user_session.user_id != DB.get(BigTask, BigTask.id, _app.id).user_id,
        detail="Forbidden"
    )

    not_found(
        conditions=DB.get(BigTask, BigTask.id, _app.id) is None,
        detail="BigTask is not Found")

    completed_bigtask = DB.set_statistic_copm(Completed_bigtask, Completed_bigtask.bigtask_id, _app.id)
    all_bigtask = DB.set_statistic_all(Completed_bigtask, Completed_bigtask.bigtask_id, _app.id)

    return ResultStatisticBigTaskModel(
        completed_bigtask=completed_bigtask, 
        all_bigtask=all_bigtask)


@app.post('/get_profile')
def get_profile(_app:SessionModel):
    user_session = check_user(_app)

    user = DB.get(Auth, Auth.id, user_session.user_id)

    out = dict()
    for i in user_profile_setting:
        data = getattr(user, i)
        if i == "image":
            out[i] = DB.getlinkimage(data)
        else:
            out[i] = data
    return out

@app.post('/edit_profile')
def edit_profile(_app:UserModel):
    user_session = check_user(_app)

    for key in _app.edit:
        bad_request(
            conditions=key not in user_profile_setting and key != 'image',
            detail="Bead reqest")
    
    user = DB.edit_profile_db(Auth, Auth.id, user_session.user_id, **(_app.edit))

    return {'Out': True}

@app.get("/image")
async def get_image(link: str):
    link_image = (DB.get(TimeLinkGetImage, TimeLinkGetImage.link, link)).link_image
    DB.dellinkimage(link)
    return FileResponse(path=link_image, filename="User", media_type='text/mp4')

@app.get("/dell_time_it_up_image")
async def dell_time_it_up_image():
    DB.dellallimage()