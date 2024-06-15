import asyncio
from sqlalchemy import create_engine, Column, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
from bot import DATABASE_URL

BASE = declarative_base()


class BanList(BASE):
    __tablename__ = "banlist"
    user_id = Column(BigInteger, primary_key=True)

    def __init__(self, user_id):
        self.user_id = user_id


def start() -> scoped_session:
    engine = create_engine(DATABASE_URL, client_encoding="utf8", poolclass=StaticPool)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
INSERTION_LOCK = asyncio.Lock()


async def ban_user(user_id):
    async with INSERTION_LOCK:
        session = SESSION()
        try:
            usr = session.query(BanList).filter_by(user_id=user_id).one()
        except NoResultFound:
            usr = BanList(user_id=user_id)
            session.add(usr)
            session.commit()
            return True
        finally:
            session.close()


async def is_banned(user_id):
    async with INSERTION_LOCK:
        session = SESSION()
        try:
            usr = session.query(BanList).filter_by(user_id=user_id).one()
            return usr.user_id
        except NoResultFound:
            return False
        finally:
            session.close()


async def unban_user(user_id):
    async with INSERTION_LOCK:
        session = SESSION()
        try:
            usr = session.query(BanList).filter_by(user_id=user_id).one()
            session.delete(usr)
            session.commit()
            return True
        except NoResultFound:
            return False
        finally:
            session.close()
