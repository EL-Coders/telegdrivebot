import asyncio
from sqlalchemy import create_engine, Column, BigInteger, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
from bot import DATABASE_URL, LOGGER


BASE = declarative_base()


class Forcesub(BASE):
    __tablename__ = "forcesub"
    channel_id = Column(BigInteger, primary_key=True)
    channel_link = Column(TEXT)

    def __init__(self, channel_id, channel_link):
        self.channel_id = channel_id
        self.channel_link = channel_link


def start() -> scoped_session:
    engine = create_engine(DATABASE_URL, client_encoding="utf8", poolclass=StaticPool)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
INSERTION_LOCK = asyncio.Lock()


async def set_channel(channel_id, channel_link):
    async with INSERTION_LOCK:
        try:
            session = SESSION()
            fsub = session.query(Forcesub).first()
            if fsub:
                fsub.channel_id = channel_id
                fsub.channel_link = channel_link
            else:
                fsub = Forcesub(channel_id=channel_id, channel_link=channel_link)
                session.add(fsub)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            LOGGER.warning("Error setting force sub channel: %s", str(e))
            return False
        finally:
            session.close()


async def get_channel():
    async with INSERTION_LOCK:
        try:
            session = SESSION()
            channel = session.query(Forcesub).one()
            return channel.channel_id
        except NoResultFound:
            return False
        finally:
            session.close()


async def get_link():
    async with INSERTION_LOCK:
        try:
            session = SESSION()
            channel = session.query(Forcesub).one()
            return channel.channel_link
        except NoResultFound:
            return False
        finally:
            session.close()


async def delete_channel():
    async with INSERTION_LOCK:
        try:
            session = SESSION()
            channel = session.query(Forcesub).one()
            session.delete(channel)
            session.commit()
            return True
        except NoResultFound:
            return False
        finally:
            session.close()
