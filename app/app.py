import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from sqlalchemy.orm import sessionmaker
from app.db_setup import TimeLinkGetImage, engine

from app.db_use import DBActivate

from app.router import authorization
from app.router import profile
from app.router import task
from app.router import bigtask


app = FastAPI()

# Работа с Базой Данных
DBSession = sessionmaker(engine)
DB = DBActivate(DBSession)

# Получение файла
@app.get("/file", response_class=FileResponse)
async def get_file(link: str):
    link_file = DB.get_first_filter(TimeLinkGetImage, search=(TimeLinkGetImage.link == link))

    if DB.get_first_filter(TimeLinkGetImage, search=(TimeLinkGetImage.link == link)) is None:
        raise HTTPException(status_code=325, detail='asd') # описать ошибку

    link_file = link_file.link_file
    # # DB.dell(TimeLinkGetImage, search=(TimeLinkGetImage.link == link))

    return FileResponse(link_file)

# Подключение авторизации
app.include_router(authorization.router, prefix="/authorization")
# Подключение профиля
app.include_router(profile.router, prefix="/profile")
# Подключение заданий
app.include_router(task.router, prefix="/task")
# Подключение больших целей
app.include_router(bigtask.router, prefix="/bigtask")

@app.get("/dell-time-it-up-image")
async def dell_time_it_up_image():
    DB.dell(TimeLinkGetImage, search=(TimeLinkGetImage.time_delete >= datetime.datetime.now(datetime.timezone.utc)))