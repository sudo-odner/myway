from email.mime import image
from uuid import uuid4
import datetime
from app.db_setup import Auth, Auth_session, Task, BigTask, Completed_bigtask, Completed_all, TimeLinkGetImage

import hashlib

import random
import string


_hash = lambda x : hashlib.md5((x).encode()).hexdigest()

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
    def get(db_table, where, value, session=None):
        return session.query(db_table).filter(where == value).first()
    
    @DBdecorator
    def add(db_table, session=None):
        session.add(db_table)
        session.commit()
        return db_table.id
    
    @DBdecorator
    def new_session(user_id, session=None):
        _session_ = uuid4().hex

        date_now = datetime.datetime.now(datetime.timezone.utc)
        session.add(Auth_session(user_id=user_id, last_using=date_now, session=_session_))
        session.commit()
        return _session_
        
    @DBdecorator
    def new_user(email, password, name, image="None", session=None):
        _salt = ''.join(random.choice(string.ascii_letters) for x in range(30))
        _hashpass = _hash(password + _salt)

        db_table = Auth(email=email, hashpass=_hashpass, salt=_salt, name=name, image=image)
        session.add(db_table)
        session.commit()
        return db_table.id

    @DBdecorator
    def edit_complete_task(db_table, where, value, session=None):
        db = session.query(db_table).filter(where == value).first()
        db.completed = 1
        session.commit()
    
    @DBdecorator
    def get_task(idd, date_start, date_end, session=None):

        db_table = session.query(Task).filter(Task.user_id == idd, date_start <= Task.date, Task.date <= date_end).all()
        tasks = []
        for i in db_table:
            db_table_big = session.query(BigTask).filter(BigTask.id == i.big_task_id).first()
            db_table_comp = session.query(Completed_all).filter(Completed_all.task_id == i.id).first()
            if i.big_task_id == -1:
                tasks.append({"id": i.id, "tasks": i.task, "date": i.date, "image": "None", "name_big_task": "None", "icon": "None", "big_task_id": i.big_task_id, "completed": db_table_comp.completed})
            else:
                link = str(uuid4().hex)
                db = TimeLinkGetImage(link=link, image=db_table_big.image, time_delete=(datetime.datetime.now() + datetime.timedelta(minutes=60)))

                session.add(db)
                session.commit()
                tasks.append({"id": i.id, "tasks": i.task, "date": i.date, "image":  f"/image?link={link}", "name_big_task": db_table_big.name, "icon": db_table_big.icon, "big_task_id": i.big_task_id,  "completed": db_table_comp.completed})
            
        if tasks == []:
            tasks = None
        return tasks

    @DBdecorator
    def get_bigtask(idd, goal, session=None):

        if goal == -1:
            db_table_bigtask = session.query(BigTask).filter(BigTask.user_id == idd).all()
        else:
            db_table_bigtask = session.query(BigTask).filter(BigTask.user_id == idd, BigTask.id == goal).all()

        bigtask = []
        for i in db_table_bigtask:
            statistic = []
            db_table_statistic = session.query(Completed_bigtask).filter(Completed_bigtask.bigtask_id == i.id).all()
            for j in db_table_statistic:
                statistic.append({"date": j.date, "completed": j.completed})

            link = str(uuid4().hex)
            db = TimeLinkGetImage(link=link, image=i.image, time_delete=(datetime.datetime.now() + datetime.timedelta(minutes=60)))
            session.add(db)
            session.commit()
            print(1)
            bigtask.append({"id": i.id, "image": f"/image?link={link}", "icon": i.icon, "name": i.name, "statistic": statistic})
        return bigtask
    
    @DBdecorator
    def set_statistic_copm(db_table, where, value, session=None):
        data = [[str(item.date.date()), item.completed] for item in session.query(db_table).where(where == value).all()]
        out = dict()

        for date, compl in data:
            if date in out:
                out[date] = out[date] + int(compl)
            else:
                out[date] = int(compl)
        return [{'date': date, "status": value} for date, value in list(out.items())]
    
    @DBdecorator
    def set_statistic_all(db_table, where, value, session=None):
        data = [[str(item.date.date()), item.completed] for item in session.query(db_table).where(where == value).all()]
        out = dict()
        
        for date, z in data:
            if date in out:
                out[date] = out[date] + 1
            else:
                out[date] = 1
        return [{'date': date, "status": value} for date, value in list(out.items())]
    
    @DBdecorator
    def edit_profile_db(db_table, where, value, session=None, **kwargs):
        db = session.query(db_table).filter(where == value).first()

        for key, val in kwargs.items():
            if key == "photo":
                setattr(db, key, (" ".join(map(lambda x: str(x), val))))
            else:
                setattr(db, key, val)
        
        session.commit()
    
    @DBdecorator
    def add_image(db_table, where, value, link, session=None):
        db = session.query(db_table).filter(where == value).first()
        db.image = link
        session.commit() 
    
    @DBdecorator
    def getlinkimage(image, session=None):
        link = str(uuid4().hex)
        db = TimeLinkGetImage(link=link, image=image, time_delete=(datetime.datetime.now() + datetime.timedelta(minutes=60)))
        session.add(db)
        session.commit()
        return f"/image?link={link}"
    
    @DBdecorator
    def dellinkimage(link, session=None):
        db = session.query(TimeLinkGetImage).filter(TimeLinkGetImage.link == link).first()
        session.delete(db)
        session.commit()
    
    @DBdecorator
    def dellallimage(session=None):
        db = session.query(TimeLinkGetImage).filter(TimeLinkGetImage.time_delete >= datetime.datetime.now()).all()
        for item in db:
            session.delete(item)
        session.commit()