import asyncio
from sqlalchemy import create_engine, Column, TEXT, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
from bot import DATABASE_URL

BASE = declarative_base()


class Broadcast(BASE):
    __tablename__ = "broadcast"
    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(TEXT)

    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name


def start() -> scoped_session:
    engine = create_engine(DATABASE_URL, client_encoding="utf8", poolclass=StaticPool)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
INSERTION_LOCK = asyncio.Lock()


async def add_user(user_id, user_name):
    async with INSERTION_LOCK:
        session = SESSION()
        try:
            usr = session.query(Broadcast).filter_by(user_id=user_id).one()
        except NoResultFound:
            usr = Broadcast(user_id=user_id, user_name=user_name)
            session.add(usr)
            session.commit()
        finally:
            session.close()


async def is_user(user_id):
    async with INSERTION_LOCK:
        session = SESSION()
        try:
            usr = session.query(Broadcast).filter_by(user_id=user_id).one()
            return usr.user_id
        except NoResultFound:
            return False
        finally:
            session.close()


async def query_msg():
    async with INSERTION_LOCK:
        session = SESSION()
        try:
            query = session.query(Broadcast.user_id).order_by(Broadcast.user_id)
            return query.all()
        finally:
            session.close()


async def del_user(user_id):
    async with INSERTION_LOCK:
        session = SESSION()
        try:
            usr = session.query(Broadcast).filter_by(user_id=user_id).one()
            session.delete(usr)
            session.commit()
        except NoResultFound:
            pass
        finally:
            session.close()
