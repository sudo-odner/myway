from sqlalchemy import LargeBinary, create_engine, Column, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    "postgresql://postgres:6236@localhost:5432/myway", 

    execution_options={
        "isolation_level": "REPEATABLE READ"
    }
    )
class BaseRepr():
    def __repr__(self):
        data = self.__dict__
        print(data)
        data = dict(filter(lambda x: x[0] not in '_sa_instance_state', data.items()))
        nl_char = '\n'
        return f"""{nl_char.join([f"{i[0]}: {i[1]}" for i in data.items()])}{nl_char}{nl_char}"""

Base = declarative_base()

class Auth(Base, BaseRepr):
    __tablename__ = 'auth'
    id = Column(Integer, primary_key=True)
    hashpass = Column(String)
    salt = Column(String)
    name = Column(String)
    email = Column(String)
    image = Column(String)

class Auth_session(Base, BaseRepr):
    __tablename__ = 'auth_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    session = Column(String)
    last_using = Column(DateTime)

class Task(Base, BaseRepr):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    task = Column(String)
    date = Column(DateTime)
    big_task_id = Column(Integer)
    completed = Column(Integer)

class BigTask(Base, BaseRepr):
    __tablename__ = "bigtask"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    image = Column(String)
    icon = Column(String)
    name = Column(String)

class Completed_bigtask(Base, BaseRepr):
    __tablename__ = "completed_bigtask"
    id = Column(Integer, primary_key=True)
    bigtask_id = Column(Integer)
    user_id = Column(Integer)

    task_id = Column(Integer)
    date = Column(DateTime)
    completed = Column(String)

class Completed_all(Base, BaseRepr):
    __tablename__ = "completed_all"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    task_id = Column(Integer)
    date = Column(DateTime)
    completed = Column(String)

class TimeLinkGetImage(Base, BaseRepr):
    __tablename__ = "timelinkgetimage"
    id = Column(Integer, primary_key=True)
    link = Column(String)
    image = Column(String)
    time_delete = Column(DateTime)

Base.metadata.bind = engine
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)