from email.mime import image
from uuid import uuid4
import datetime
from app.db_setup import Task, BigTask, TimeLinkGetImage, User, User_session

import hashlib

import random
import string
from app.model.statistic import DayStatistic

from app.model.task import BigTaskResult, TaskResult


_hash = lambda x : hashlib.md5((x).encode()).hexdigest()

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

def add_linc_to_imag(file):
    link = str(uuid4().hex)
    db = TimeLinkGetImage(link=link, file=file, time_delete=(datetime.datetime.now() + datetime.timedelta(minutes=60)))
    link = link + _hash(db.id)
    db.link = link

    return db

class DBActivate():
    def __init__(self, session) -> None:
        self.session = session
    
    def DBdecorator(func):
        def DBUSe(self, *args, **kwargs):
            result = None
            session = None

            try:
                session = self.session()
                result = func(*args, **kwargs, session=session)
            except Exception as err:
                print("ERR: ", err)
                if session is not None:
                    session.rollback()
            if session is not None:
                session.close()
            return result
        return DBUSe
    
    @DBdecorator
    def get_first_filter_by(db_table, session=None, **_search):
        return session.query(db_table).filter_by(**_search).first()
    
    @DBdecorator
    def get_all_filter_by(db_table, session=None, **_search):
        return session.query(db_table).filter_by(**_search).all()
    
    @DBdecorator
    def get_all_filter(db_table, session=None, _search=()):
        return session.query(db_table).filter(*_search).all()
    
    @DBdecorator
    def get_all_filter(db_table, session=None, _search=()):
        return session.query(db_table).filter(*_search).first()
    
    @DBdecorator
    def update(db_table, reload={}, session=None, **_search):
        session.query(db_table).filter(**_search).update(reload)
        session.commit()
    
    @DBdecorator
    def add(db_table, session=None):
        session.add(db_table)
        session.commit()
        return db_table.id
    
    @DBdecorator
    def dell(db_table, session=None, _search=()):
        db_list = session.query(db_table).filter(*_search).all()
        for db in db_list:
            session.delete(db)
        session.commit()
    
    @DBdecorator
    def getlinkimage(image, session=None):
        db = add_linc_to_imag(image)
        session.add(db)
        session.commit()
        return f"/download-file?link={db.link}"

    

    @DBdecorator
    def new_session(user_id, session=None):
        _session_ = uuid4().hex

        session.add(User_session(user_id=user_id, session=_session_, last_using=datetime.datetime.now(datetime.timezone.utc)))
        session.commit()

        db_user = session.query(User).filter_by( id=user_id ).first()
        db_user.last_using = datetime.datetime.now(datetime.timezone.utc)
        session.commit()
        return _session_
        
    @DBdecorator
    def new_user(email, password, name, image="None", session=None):
        _salt = ''.join(random.choice(string.ascii_letters) for x in range(30))
        _hashpass = _hash(password + _salt)

        db_table = User(email=email, hashpass=_hashpass, salt=_salt, name=name, image=image)
        session.add(db_table)
        session.commit()
        return db_table.id
    
    @DBdecorator
    def using_app(user_session, session=None):
        db_user = session.query(User).filter_by( id=user_session.user_id ).first()
        db_session = session.query(User_session).filter_by( session=user_session.id ).first()
        db_user.last_using = datetime.datetime.now(datetime.timezone.utc)
        db_session.last_using = datetime.datetime.now(datetime.timezone.utc)
        session.commit()    
    
    
    
    @DBdecorator
    def get_task(idd, date_start, date_end, session=None):
        db_table = session.query(Task).filter(Task.user_id == idd, date_start <= Task.date, Task.date <= date_end).all()

        tasks = []
        for i in db_table:
            db_table_big = session.query(BigTask).filter(BigTask.id == i.big_task_id).first()
            if i.big_task_id == -1:
                TaskResult(
                    id=i.id,
                    task=i.task,
                    date=i.date,
                    completed=db_table.completed
                )
            else:
                db = add_linc_to_imag(db_table_big.image)
                session.add(db)
                session.commit()
                tasks.append(TaskResult(
                    id=i.id,
                    task=i.task,
                    date=i.date,
                    image=f"/download-file?link={db.link}",
                    name_big_task=db_table_big.name,
                    icon=db_table_big.icon,
                    big_task_id=i.big_task_id,
                    completed=db_table.completed
                ))
        return tasks
    @DBdecorator
    def get_bigtask(idd, goal, session=None):
        if goal == -1:
            db_table_bigtask = session.query(BigTask).filter(BigTask.user_id == idd).all()
        else:
            db_table_bigtask = session.query(BigTask).filter(BigTask.user_id == idd, BigTask.id == goal).all()

        bigtask = []
        for item in db_table_bigtask:
            statistic = get_statistic(session.query(Task).filter(Task.id == item.id).all())

            db = add_linc_to_imag(db_table_bigtask.image)
            session.add(db)
            session.commit()

            BigTaskResult( 
                id=item.id,
                image=f"/download-file?link={db.link}",
                icon=item.icon,
                name=item.name,
                statistic=statistic)

        return bigtask