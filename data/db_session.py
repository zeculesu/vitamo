from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

SQLAlchemyBase = declarative_base()

__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return None
    db_file = db_file.strip()
    if not db_file:
        raise Exception('Необходимо указать файл данных')
    engine = create_engine(db_file.replace('postgres', 'postgresql'), echo=False)
    __factory = sessionmaker(bind=engine)

    from . import __all_models

    SQLAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()