# from fastapi import APIRouter, HTTPException
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import and_

# from app.db_setup import BigTask, Task, engine
# from app.db_use import DB_Activate

# from app.model.task import AddTaskModel, GetTaskModel, ListTaskModel
# from app.model.model import IDResult, SessionAndID

# from app.help_func import object_to_datetime, cheak_user_session

# router = APIRouter()

# # Работа с Базой Данных
# DBSession = sessionmaker(engine)
# DB = DB_Activate(DBSession)


# ########################################################### Получение цели

# @router.get('/get-task', response_model=ListTaskModel)
# def get_task(_app: GetTaskModel):
#     user_session = cheak_user_session(_app.session)

#     tasks = DB.get_task(user_session.user_id, object_to_datetime(_app.date_start), object_to_datetime(_app.date_end))
#     return ListTaskModel(result=tasks)


# ########################################################### Добавление цели

# @router.post('/add-task', response_model=IDResult)
# def add_task(_app: AddTaskModel):
#     user_session = cheak_user_session(_app.session)

#     if DB.get_all_filter(BigTask, search=(BigTask.id == _app.bigtask)) is None and _app.bigtask != -1:
#         raise HTTPException(status_code=404, detail='Such target does not exist or is not available')
#     if _app.bigtask != -1 and DB.get_first_filter(BigTask, search=(BigTask.id == _app.bigtask)).user_id != user_session.user_id:
#         raise HTTPException(status_code=423, detail="To this user is not accessing the big goal")
    
#     task_id = DB.add(Task(user_id=user_session.user_id, task=_app.task, date=object_to_datetime(_app.date), big_task_id=_app.big_task_id, completed=False))
#     return IDResult(id=task_id)


# ########################################################### Удаление цели

# @router.delete('/deleted-task')
# def deleted_task(_app: SessionAndID):
#     user_session = cheak_user_session(_app.session)

#     if DB.get_first_filter(Task, search=(and_(Task.id == _app.id, Task.user_id == user_session.user_id))) is None:
#         raise HTTPException(status_code=404, detail='Such target does not exist or is not available')
    
#     DB.dell(Task, search=(and_(Task.id == id, Task.user_id == user_session.user_id)))


# ########################################################### Завершение цели

# @router.put('completed-task')
# def completed_taks(_app: SessionAndID):
#     user_session = cheak_user_session(_app.session)

#     if DB.get_first_filter(Task, search=(and_(Task.id == _app.id, Task.user_id == user_session.user_id))) is None:
#         raise HTTPException(status_code=404, detail='Such target does not exist or is not available')
    
#     DB.update(Task, search=(and_(Task.id == id, Task.user_id == user_session.user_id)), reload={'completed': True})