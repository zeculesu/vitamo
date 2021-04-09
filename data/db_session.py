from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

SQLAlchemyBase = declarative_base()

__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return None
    if not db_file or not db_file.strip():
        raise Exception('Необходимо указать файл данных')
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    engine = create_engine(conn_str, echo=False)
    __factory = sessionmaker(bind=engine)

    from . import __all_models

    SQLAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()