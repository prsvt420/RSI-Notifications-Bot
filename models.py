import sqlalchemy
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped

from settings import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    ...


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    telegram_id: Mapped[int] = sqlalchemy.Column(sqlalchemy.Integer)
    is_notifications: Mapped[bool] = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_superuser: Mapped[bool] = sqlalchemy.Column(sqlalchemy.Boolean, default=False)


async def check_user_exist(session, user_id):
    user_exists = await session.scalar(exists().where(User.telegram_id == user_id).select())
    return user_exists


async def insert_user(session, user_id):
    user = User(telegram_id=user_id)
    session.add(user)
    await session.commit()


async def insert_user_if_not_exist(message):
    async with async_session() as session:
        user_id = message.from_user.id
        user_is_exist = await check_user_exist(session, user_id)

        if not await check_user_exist(session, user_id):
            await insert_user(session, user_id)


async def update_notifications_status(telegram_id: int, is_notifications: bool):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user.scalars().first()
        user.is_notifications = is_notifications
        await session.commit()


async def async_model_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
