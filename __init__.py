class DB_activate():
    def __init__(self, session):
        self.session = session
    
    def db_decorator(func):
        def db_use(self, *args, **kwargs):
            session = None
            result = None

            try:
                session = self.session
                result = func(*args, **kwargs, session=session)
            except Exception as err:
                print(f'Error: {err}')
                if session is not None:
                    session.rollback()
            if session is not None:
                session.close()
            return result
        return db_use
    
    @db_decorator
    def get_filter(db_table, session=None, search=()):
        return session.query(db_table).filter(search).all()
    
    @db_decorator
    def add(db_table, session=None):
        session.add(db_table)
        session.commit()
        return db_table.id
    
    @db_decorator
    def update(db_table, session=None, search=(), reload={}):
        session.query(db_table).filter(search).update(reload)
        session.commit()
    
    @db_decorator
    def delete(db_table, session=None, search=()):
        result_line = session.query(db_table).filter(search).all()
        for db_line in result_line:
            session.delete(db_line)
        session.commit()


