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
    telegram_id: Mapped[int] = sqlalchemy.Column(sqlalchemy.Integer, unique=True, nullable=False)
    is_notifications: Mapped[bool] = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)

    def __str__(self):
        return str(self.telegram_id)


class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    symbol: Mapped[str] = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)
    interval: Mapped[str] = sqlalchemy.Column(sqlalchemy.String(10), nullable=False)
    is_active: Mapped[bool] = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)

    def __str__(self):
        return f"{self.symbol} - {self.interval}"


class NotificationUser(Base):
    __tablename__ = 'notification_user'

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id), primary_key=True)
    notification_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(Notification.id), primary_key=True)
    is_active: Mapped[bool] = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)

    def __str__(self):
        return f"{self.user_id} - {self.notification_id}"


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


async def select_notifications():
    async with async_session() as session:
        notifications = await session.execute(
            select(Notification).where(Notification.is_active == 1))
    return notifications.scalars().all()


async def select_users_by_notification_id(notification_id):
    async with async_session() as session:
        users = await session.execute(
            select(User).join(NotificationUser)
            .where(NotificationUser.notification_id == notification_id)
            .where(NotificationUser.is_active == 1)
            .where(User.is_notifications == 1)
        )
    return users.scalars().all()


async def async_model_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
