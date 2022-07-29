import time
from charset_normalizer import detect
import fastapi
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

from app.model.model import MessengTrue, RuthorizationModel, SessionAndID, SessionModel, UserModel, RegistedModel, UserResultModel
from app.model.task import AddBigTaskModel, AddTaskModel, GetTaskModel, IDResultModel, ListBigTaskResult, ListTaskResult
from app.model.statistic import DayStatistic, OneBigTaskStatistic, StatisticResult

from app.db_setup import TimeLinkGetImage, User, User_session, engine, Task, BigTask

import datetime
import hashlib

from app.db_use import DBActivate

import shutil

app = fastapi.FastAPI()

_hash = lambda x : hashlib.md5((x).encode()).hexdigest()
file_type = lambda x: (x.content_type).split('/')[1]

local_time = time.ctime(time.time()) # фича удалит на продекте ---------------- мб

def get_statistic(data):
    statistic = []
    if data is not None:
        for item in data:
            flag = True
            for element in statistic:
                if element['date'] == str(item.date):
                    element['all'] += 1
                    if item.completed == 1:
                        element['done'] += 1
                    flag = False
            
            if flag:
                one_day = {"all": 1, "done": 0, "date": str(item.date)}
                if item.completed == 1:
                    one_day["done"] += 1
                statistic.append(one_day)
    
    return list(map(lambda kwargs: DayStatistic(**kwargs), statistic))

def print_element(data):
    print("Local time:", local_time)
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


# Подключение БД
DBSession = sessionmaker(engine)
DB = DBActivate(DBSession)

# Проверк 
@app.put("/upload_image_profile", response_model=MessengTrue)
async def upload_image_profile(session: str, content_type: str, file: fastapi.UploadFile = fastapi.File(...)):
    user_session = DB.get_first_filter(User_session, search=(User_session.session == session))
    if user_session is None:
        raise HTTPException(status_code=401, detail="Session is not exists")
    
    way = f"./app/image/user/{user_session.user_id}.{content_type}"

    with open(way, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    DB.update(User, search=(User.id == user_session.user_id), reload={"image": way})

    return MessengTrue(message=True)


@app.post('/registed', response_model=SessionModel)
def registed(_app: RegistedModel):
    print_element(_app.__dict__)  # ------------удалить на реализации------------

    if DB.get_first_filter(User, search=(User.email == _app.email))is not None:
        raise HTTPException(status_code=423, detail="Login is registed")
    
    birthday = datetime.datetime(_app.birthday.year, _app.birthday.month, _app.birthday.day, _app.birthday.hours, _app.birthday.minute)
    user = DB.new_user(email=_app.email, password=_app.password, name=_app.name, birthday=birthday)

    return SessionModel(session=DB.new_session(user))


@app.post('/authorization', response_model=SessionModel)
def authorization(_app: RuthorizationModel):
    print_element(_app.__dict__)  # ------------удалить на реализации------------

    user = DB.get_first_filter_by(User, email=_app.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Login not found")
    
    if _hash(_app.password + user.salt) != user.hashpass:
        raise HTTPException(status_code=423, detail="Login is registed")
    
    return SessionModel(session=DB.new_session(user.id))






# Проверка пользователя
def check_user(session):
    user_session = DB.get_first_filter(User_session, search=(User_session.session == session))
    if user_session is None:
        raise HTTPException(status_code=401, detail="The session is inactive or has been deleted due to a long period of inactivity")
    
    DB.using_app(user_session)
    return user_session


@app.post('/add-task', response_model=IDResultModel)
def add_task(_app: AddTaskModel):
    print_element(_app.__dict__)  # ------------удалить на реализации------------

    user_session = check_user(_app.session)

    if DB.get_first_filter(BigTask, search=(BigTask.id == _app.bigtask)) is None and _app.bigtask != -1:
        raise HTTPException(status_code=400, detail="What?")
    if _app.bigtask != -1 and DB.get_first_filter(BigTask, search=(BigTask.id == _app.bigtask)).user_id != user_session.user_id:
        raise HTTPException(status_code=423, detail="To this user is not accessing the big goal")
    
    date = datetime.datetime(_app.date.year, _app.date.month, _app.date.day, _app.date.hours, _app.date.minute)
    task_id = DB.add(Task(user_id=user_session.user_id, task=_app.task, date=date, big_task_id=_app.bigtask, completed=0))

    return IDResultModel(id=task_id)


@app.post('/get-task', response_model=ListTaskResult) # добавить красоту Кириллу
def get_task(_app: GetTaskModel):
    print_element(_app.__dict__)  # ------------удалить на реализации------------

    user_session = check_user(_app.session)

    date_start = datetime.datetime(_app.date_start.year, _app.date_start.month, _app.date_start.day, _app.date_start.hours, _app.date_start.minute)
    date_end = datetime.datetime(_app.date_end.year, _app.date_end.month, _app.date_end.day, _app.date_end.hours, _app.date_end.minute)
    
    tasks = DB.get_task(user_session.user_id, date_start, date_end)
    
    return ListTaskResult(list_result=tasks)

@app.delete('/delete-task', response_model=MessengTrue)
def delete_task(_app: SessionAndID):
    print_element(_app.__dict__)  # ------------удалить на реализации------------

    user_session = check_user(_app.session)

    if DB.get_first_filter(Task, search=(and_(Task.user_id == user_session.user_id, Task.completed == 0, Task.id == _app.id))) == None:
        raise HTTPException(status_code=403, detail="The task has already been completed or it has not been set")
    
    DB.dell(Task, search=(Task.id == _app.id))
    return MessengTrue(message=True)




@app.put("/upload-big-task", response_model=MessengTrue)
async def upload_big_task(session: str, id: str, content_type: str, file: fastapi.UploadFile = fastapi.File(...)): # пошпрехать с Кириллом на чёт получение типа файлв
    user_session = check_user(session)

    if user_session is None:
        raise HTTPException(status_code=401, detail="Session is not exists")
    if user_session.user_id != (DB.get_first_filter_by(BigTask, id=id)).user_id:
        raise HTTPException(status_code=423, deteil="The user does not have access to this big target")
    
    way = f"./app/image/big_task/{id}.{content_type}"

    with open( way, "wb") as buffer: #
        shutil.copyfileobj(file.file, buffer)
    
    DB.update(BigTask,  search=(BigTask.id == id), reload={"image":  way})
    return MessengTrue(message=True)


@app.post('/add_bigtask', response_model=IDResultModel) #замутить чтот
def add_bigtask(_app:AddBigTaskModel):
    print_element(_app.__dict__)  # ------------удалить на реализации------------
    user_session = check_user(_app.session)

    id_big_task = BigTask(user_id=user_session.user_id, name=_app.name, icon=_app.icon)
    big_task = DB.add(id_big_task)
    return IDResultModel(id=id_big_task.id)


@app.post('/get-bigtask', response_model=ListBigTaskResult)
def get_bigtask(_app: SessionAndID):
    print_element(_app.__dict__)  # ------------удалить на реализации------------
    user_session = check_user(_app.session)
    
    big_tasks = DB.get_bigtask(user_session.user_id, _app.id)
    print(big_tasks)
    return ListBigTaskResult(list_result=big_tasks)


@app.delete('/delete-bigtask', response_model=MessengTrue) # сделать защиту от связаных тасков
def delete_bigtask(_app: SessionAndID):
    print_element(_app.__dict__)  # ------------удалить на реализации------------
    user_session = check_user(_app.session)

    if DB.get_first_filter(BigTask, search=(and_(BigTask.id ==_app.id, BigTask.user_id == user_session.user_id))) == None:
        raise HTTPException(status_code=403, detail="No such big goal or no access to it")

    DB.dell(BigTask, search=(BigTask.id == _app.id))
    return MessengTrue(message=True)




@app.put('/complite-task', response_model=MessengTrue)
def complite_task(_app: SessionAndID):
    print_element(_app.__dict__)  # ------------удалить на реализации------------
    user_session = check_user(_app.session)


    if DB.get_first_filter(Task, search=(and_(Task.id == _app.id, Task.user_id == user_session.user_id))) is None:
        raise HTTPException(status_code=403, detail="There is no such task or there is no access to it") # Такой задачи нет или к ней нет доступа
    
    DB.update(Task, search=(and_(Task.id == _app.id, Task.user_id == user_session.user_id)), reload={"completed": 1})
    return MessengTrue(message=True)




@app.post('/get-statictic', response_model=StatisticResult)
def statistic(session: str):
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)

    bigtask_statistic = get_statistic(DB.get_all_filter(Task, search=(and_(Task.user_id == user_session.user_id, Task.big_task_id != -1))))
    not_bigtask_statistic = get_statistic(DB.get_all_filter(Task, search=(and_(Task.user_id == user_session.user_id, Task.big_task_id == -1))))

    return StatisticResult(
        personal_effectiveness=bigtask_statistic,
        not_personal_effectiveness=not_bigtask_statistic
    )


@app.post('/get-statistic-one-big-task', response_model=OneBigTaskStatistic)
def statistic_big_task(_app: SessionAndID):
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(_app.session)

    if DB.get_first_filter(BigTask, search=(and_(BigTask.id == _app.id, BigTask.user_id == user_session.user_id))) is None:
        return HTTPException(status_code=403, detail="There is no or no access to such a big goal")

    one_bigtask_statistic = get_statistic(DB.get_all_filter(Task, search=(and_(Task.user_id == user_session.user_id, Task.big_task_id == _app.id))))

    return OneBigTaskStatistic(
        list_result=one_bigtask_statistic
    )




@app.post('/get_profile', response_model=UserResultModel) # Не нравитьсяя мне это но норм
def get_profile(session: str):
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)

    user = DB.get_first_filter_by(User, id=user_session.user_id)

    out = dict()
    print(user.__dict__.items())
    for item in user.__dict__.items():
        if item[0] in ['name', 'email', 'image', 'birthday']:
            if item[0] == "image":
                if item[1] is None:
                    out[item[0]] = "None"
                else:
                    out[item[0]] = DB.getlinkimage(item[1])
            elif item[0] == "birthday":
                out[item[0]] = str(item[1])
            else:
                out[item[0]] = item[1]

    return UserResultModel(**out)


@app.put('/edit_profile', response_model=MessengTrue) # Не нравитьсяя мне это норм
def edit_profile(_app:UserModel):
    print_element(_app.__dict__)  # ------------удалить на реализации------------
    user_session = check_user(_app.session)

    edit = dict()
    for item in _app.__dict__.items():
        if item is not None:
            if item[0] == 'birthday':
                edit[item[0]] = str(item[1])
            else:
                edit[item[0]] = item[1]

    user = DB.update(User, search=(User.id == user_session.user_id), reload=edit)
    return MessengTrue(message=True)




@app.get("/download-file", response_class=FileResponse)
async def download_file(link: str):
    link_image = (DB.get_first_filter(TimeLinkGetImage, search=(TimeLinkGetImage.link == link))).image
    DB.dell(TimeLinkGetImage, search=(TimeLinkGetImage.link == link))
    return FileResponse(link_image)

@app.get("/dell-time-it-up-image")
async def dell_time_it_up_image():
    DB.dell(TimeLinkGetImage, search=(TimeLinkGetImage.time_delete >= datetime.datetime.now(datetime.timezone.utc)))