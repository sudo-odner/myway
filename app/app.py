import time
from charset_normalizer import detect
import fastapi
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import sessionmaker

from app.model.model import MessengTrue, SessionModel, UserModel, RegistedModel, UserResultModel
from app.model.task import AddBigTaskModel, AddTaskModel, GetTaskModel, IDResultModel, ListBigTaskResult, ListTaskResult
from app.model.statistic import DayStatistic, OneBigTaskStatistic, StatisticResult

from app.db_setup import TimeLinkGetImage, User, User_session, engine, Task, BigTask

import datetime
import hashlib

from app.db_use import DBActivate

import shutil

user_profile_setting = 'name email '.split(' ')

app = fastapi.FastAPI()

_hash = lambda x : hashlib.md5((x).encode()).hexdigest()
local_time = time.ctime(time.time()) # фича удалит на продекте ---------------- мб

def get_statistic(data):
    statistic = []
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
    
    return list(map(lambda kwargs: DayStatistic(**kwargs), statistic))

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


# Подключение БД
DBSession = sessionmaker(engine)
DB = DBActivate(DBSession)


@app.put("/upload_image_profile", response_model=MessengTrue)
async def upload_image_profile(session: str, file: fastapi.UploadFile = fastapi.File(...)):
    user_session = DB.get_first_filter_by(User_session, session=session)
    if user_session is None:
        raise HTTPException(status_code=401, detail="Session is not exists")

    with open(f"./app/image/user/{user_session.user_id}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    DB.update(User, reload={"image": f"./app/image/user/{user_session.user_id}"}, id=user_session.user_id)

    return MessengTrue(message=True)

@app.post('/registed', response_model=SessionModel)
def registed(_app: RegistedModel):
    print("Local time:", local_time)
    print(_app)  # ------------удалить на реализации------------

    if DB.get_first_filter_by(User, email=_app.email) is not None:
        raise HTTPException(status_code=423, detail="Login is registed")
    
    user = DB.new_user(email=_app.email, password=_app.password, name=_app.name)

    return SessionModel(session=DB.new_session(user))

@app.post('/authorization', response_model=SessionModel)
def authorization(email: str, password: str):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------

    user = DB.get_first_filter_by(User, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="Login not found")
    
    if _hash(password + user.salt) != user.hashpass:
        raise HTTPException(status_code=423, detail="Login is registed")
    
    return SessionModel(session=DB.new_session(user.id))




# Проверка пользователя
def check_user(_session):
    user_session = DB.get_first_filter_by(User_session, session=_session)
    if user_session is None:
        raise HTTPException(status_code=401, detail="The session is inactive or has been deleted due to a long period of inactivity")
    
    DB.using_app(user_session)
    return user_session


@app.post('/add-task', response_model=IDResultModel)
def add_task(_app: AddTaskModel):
    print("Local time:", local_time)
    print(_app)  # ------------удалить на реализации------------

    user_session = check_user(_app.session)

    if DB.get_first_filter_by(BigTask, id=_app.bigtask)is None and _app.bigtask != -1:
        raise HTTPException(status_code=400, detail="What?")
    if _app.bigtask != -1 and DB.get_first_filter_by(BigTask, id=_app.bigtask).user_id != user_session.user_id:
        raise HTTPException(status_code=423, detail="To this user is not accessing the big goal")
    
    date = datetime.datetime(_app.birthday.year, _app.birthday.month, _app.birthday.day, _app.birthday.hours, _app.birthday.minute)
    task_id = DB.add(Task(user_id=user_session.user_id, task=_app.task, date=date, big_task_id=_app.bigtask, completed=0))

    return IDResultModel(id=task_id)


@app.post('/get-task', response_model=ListTaskResult) # добавить красоту Кириллу
def get_task(_app: GetTaskModel):
    print("Local time:", local_time)
    print(_app)  # ------------удалить на реализации------------

    user_session = check_user(_app.session)

    date_start = datetime.datetime(_app.date_start.year, _app.date_start.month, _app.date_start.day, _app.date_start.hours, _app.date_start.minute)
    date_end = datetime.datetime(_app.date_end.year, _app.date_end.month, _app.date_end.day, _app.date_end.hours, _app.date_end.minute)
    
    tasks = DB.get_task(user_session.user_id, date_start, date_end)
    
    return ListTaskResult(list_result=tasks)

@app.delete('/delete-task', response_model=MessengTrue)
def delete_task(session: str, id: int):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------

    user_session = check_user(session)

    if DB.get_first_filter_by(Task, user_id=user_session.user_id, completed=0, id=id) == None:
        raise HTTPException(status_code=403, detail="The task has already been completed or it has not been set")
    
    DB.dell(Task, _search=(Task.id == id))
    return MessengTrue(messenge=True)





@app.post('/add_bigtask', response_model=IDResultModel) #замутить чтот
def add_bigtask(_app:AddBigTaskModel):
    print("Local time:", local_time)
    print(_app)  # ------------удалить на реализации------------
    user_session = check_user(_app.session)

    id_big_task = BigTask(user_id=user_session.user_id, name=_app.name, icon=_app.icon)
    big_task = DB.add(id_big_task)
    return IDResultModel(id=id_big_task.id)


@app.put("/upload-big-task", response_model=MessengTrue)
async def upload_big_task(session: str, id: str, type_file: str, file: fastapi.UploadFile = fastapi.File(...)): # пошпрехать с Кириллом на чёт получение типа файлв
    user_session = DB.get_first_filter_by(User_session, session=session)
    if user_session is None:
        raise HTTPException(status_code=401, detail="Session is not exists")
    if user_session.user_id != (DB.get_first_filter_by(BigTask, id=id)).user_id:
        raise HTTPException(status_code=423, deteil="The user does not have access to this big target")

    with open(f"./app/image/big_task/{id}.{type_file}", "wb") as buffer: #
        shutil.copyfileobj(file.file, buffer)
    
    DB.update(BigTask, reload={"image": f"./app/image/bit_task/{id}.{type_file}"}, id=id)
    return MessengTrue(message=True)


@app.post('/get-bigtask', response_model=ListBigTaskResult)
def get_bigtask(session: str, id: int):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)
    
    big_tasks = DB.get_bigtask(user_session.user_id, id)
    return ListBigTaskResult(list_result=big_tasks)


@app.delete('/delete-bigtask', response_model=MessengTrue)
def delete_bigtask(session: str, id: int):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)

    if DB.get_first_filter_by(BigTask, id=id, user_id=user_session.user_id) == None:
        raise HTTPException(status_code=403, deteil="No such big goal or no access to it")

    DB.dell(Task, _search=(Task.id == id))
    return MessengTrue(messenge=True)




@app.put('/complite-task', response_model=MessengTrue)
def complite_task(session: str, id: int):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)

    if DB.get_first_filter_by(Task, id=id, user_id=user_session.user_id) is None:
        raise HTTPException(status_code=403, deteil="There is no such task or there is no access to it") # Такой задачи нет или к ней нет доступа
    
    DB.update(Task, reload={"completed": 1}, id=id, user_id=user_session.user_id)
    return MessengTrue(message=True)




@app.post('/get-statictic', response_model=StatisticResult)
def statistic(session: str):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)

    bigtask_statistic = get_statistic(DB.get_all_filter(Task, _search=(Task.user_id == user_session.user_id, Task.big_task_id != -1)))
    not_bigtask_statistic = get_statistic(DB.get_all_filter(Task, _search=(Task.user_id == user_session.user_id, Task.big_task_id == 0)))

    return StatisticResult(
        personal_effectiveness=bigtask_statistic,
        not_personal_effectiveness=not_bigtask_statistic
    )


@app.post('/get-statistic-one-big-task', response_model=OneBigTaskStatistic)
def statistic_big_task(session: str, id: int):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)

    if DB.get_first_filter_by(BigTask, id=id, user_id=user_session.user_id) is None:
        return HTTPException(status_code=403, detail="There is no or no access to such a big goal")

    one_bigtask_statistic = get_statistic(DB.get_all_filter(Task, _search=(Task.user_id == user_session.user_id, Task.big_task_id == id)))

    return OneBigTaskStatistic(
        list_result=one_bigtask_statistic
    )




@app.post('/get_profile', response_model=UserResultModel)
def get_profile(session: str):
    print("Local time:", local_time)
    print_element(vars()) # ------------удалить на реализации------------
    user_session = check_user(session)

    user = DB.get_first_filter_by(User, id=user_session.user_id)

    out = dict()
    for i in user_profile_setting:
        data = getattr(user, i)
        if i == "image":
            if data == None:
                out[i] = data
            else:
                out[i] = DB.getlinkimage(data)
        else:
            out[i] = data

    return UserResultModel(**out)

@app.put('/edit_profile', response_model=MessengTrue)
def edit_profile(_app:UserModel):
    print("Local time:", local_time)
    print(_app)
    user_session = check_user(_app.session)

    for key in _app.edit:
        if key not in user_profile_setting and key != 'image':
            HTTPException(status_code=400, detail="Wrong filling")

    user = DB.update(User, reload=_app.edit, id=user_session.user_id)
    return MessengTrue(message=True)




@app.get("/download-file", response_class=FileResponse)
async def download_file(link: str):
    link_image = (DB.get_all_filter(TimeLinkGetImage, link=link)).link_image
    DB.dell(TimeLinkGetImage, _search=(TimeLinkGetImage.link == link))
    return FileResponse(link_image)

@app.get("/dell_time_it_up_image")
async def dell_time_it_up_image():
    DB.dell(TimeLinkGetImage, _search=(TimeLinkGetImage.time_delete >= datetime.datetime.now(datetime.timezone.utc)))
    DB.dellallimage()