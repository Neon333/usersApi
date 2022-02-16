from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Database


Base = declarative_base()
engine = create_async_engine(
    f'mysql+aiomysql://{Database.USER}:{Database.PASSWORD}@{Database.HOST}/{Database.NAME}', echo=True
)
current_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def get_session() -> AsyncSession:
    return current_session()
