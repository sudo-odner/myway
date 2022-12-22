from app.db_setup import Task, BigTask, TimeLinkGetImage, User_profile, User_session

from app.model.task import TaskModel
from app.model.bigtask import BigTaskModel

from uuid import uuid4
import datetime
import hashlib
import random
import string

# Функция хеширования
_hash = lambda x : hashlib.md5((x).encode()).hexdigest()

# def get_statistic(data):
#     statistic = []
#     for item in data:
#         flag = True
#         for element in statistic:
#             if element['date'] == str(item.date):
#                 element['all'] += 1
#                 if item.completed == 1:
#                     element['done'] += 1
#                 flag = False
        
#         if flag:
#             one_day = {"all": 1, "done": 0, "date": str(item.date)}
#             if item.completed == 1:
#                 one_day["done"] += 1
    
#     return list(map(lambda kwargs: DayStatistic(**kwargs), statistic))
    

def add_linc_to_imag(file):
    link = str(uuid4().hex)
    db = TimeLinkGetImage(link=link, image=file, time_delete=(datetime.datetime.now() + datetime.timedelta(minutes=60)))
    link = link + _hash(str(db.id))
    db.link = link

    return db


class DB_Activate():
    def __init__(self, session) -> None:
        self.session = session
    
    def db_decorator(func):
        def db_use(self, *args, **kwargs):
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
        return db_use
    
    @db_decorator
    def get_first_filter(db_table, session=None, search=()):
        return session.query(db_table).filter(search).first()
    
    @db_decorator
    def get_all_filter(db_table, session=None, search=()):
        return session.query(db_table).filter(search).all()
    
    @db_decorator
    def add(db_table, session=None):
        session.add(db_table)
        session.commit()
        return db_table.id
    
    @db_decorator
    def update(db_table, reload={}, session=None, search=()):
        session.query(db_table).filter(search).update(reload)
        session.commit()
    
    @db_decorator
    def dell(db_table, session=None, search=()):
        db_list = session.query(db_table).filter(search).all()
        for db in db_list:
            session.delete(db)
        session.commit()
    
    @db_decorator
    def getlinkimage(file, session=None):
        db = add_linc_to_imag(file)
        session.add(db)
        session.commit()
        return f"/file?link={db.link}"


    @db_decorator
    def new_session(id, session=None):
        date_now = datetime.datetime.now(datetime.timezone.utc)
        user = User_session(user_id=id, last_using=date_now, session=(uuid4().hex))
        session.add(user)
        session.commit()

        return user.session
        
    @db_decorator
    def new_user(email, password, name, birthday, session=None):
        date_now = datetime.datetime.now(datetime.timezone.utc)
        _salt = ''.join(random.choice(string.ascii_letters) for x in range(30))
        _hashpass = _hash(password + _salt)

        db_user = User_profile(email=email, hashpass=_hashpass, salt=_salt, name=name, birthday=birthday, last_using=date_now)
        session.add(db_user)
        session.commit()

        db_user_session = User_session(user_id=db_user.id, last_using=date_now, session=(uuid4().hex))
        session.add(db_user_session)
        session.commit()

        return db_user_session.session
    
    @db_decorator
    def time_update(user_session, session=None):
        db_user = session.query(User_profile).filter_by(id=user_session.user_id).first()
        db_session = session.query(User_session).filter_by(session=user_session.session).first()
        db_user.last_using = datetime.datetime.now(datetime.timezone.utc)
        db_session.last_using = datetime.datetime.now(datetime.timezone.utc)
        session.commit()    
    
    
    
    @db_decorator
    def get_task(id, date_start, date_end, session=None):
        db_table = session.query(Task).filter(Task.user_id == id, date_start <= Task.date, Task.date <= date_end).all()
        tasks = []
        for element in db_table:
            task = TaskModel(id=element.id, name=element.name, date=str(element.date), completed=element.completed)

            bigtask = session.query(BigTask).filter(BigTask.id == element.bigtask_id).first()
            if bigtask != -1:
                db = add_linc_to_imag(bigtask.filelink)
                session.add(db)
                session.commit()

                task.bigtask = BigTaskModel(id=bigtask.id, icon=bigtask.icon, name=bigtask.name, filelink=f"/file?link={db.link}")
            
            tasks.append(task)

        return tasks
    

    @db_decorator
    def get_big_task(id, goal, session=None):
        if goal == -1:
            db_table = session.query(BigTask).filter(BigTask.user_id == id,).all()
        else:
            db_table = session.query(BigTask).filter(BigTask.user_id == id, BigTask.id == goal).first()
        bigtasks = []
        for element in db_table:
            bigtask = BigTaskModel(id=element.id, name=element.name, icon=element.icon)
            if element.filelink != None:
                db = add_linc_to_imag(bigtask.filelink)
                session.add(db)
                session.commit()

                bigtask.filelink = f"/file?link={db.link}"
            
            bigtasks.append(bigtask)
        
        return bigtasks