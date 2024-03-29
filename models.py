from datetime import datetime

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

    def __str__(self):
        return f"{self.symbol} - {self.interval}"


class NotificationUser(Base):
    __tablename__ = 'notification_user'

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id), primary_key=True)
    notification_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(Notification.id), primary_key=True)
    is_active: Mapped[bool] = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)

    def __str__(self):
        return f"{self.user_id} - {self.notification_id}"


class Subscribed(Base):
    __tablename__ = 'subscribed'

    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.telegram_id), primary_key=True)
    subscription_end_datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    def __str__(self):
        return f"{self.telegram_id} - {self.subscription_end_datetime}"


async def is_user_subscribed(telegram_id):
    async with async_session() as session:
        return bool(
            await session.scalar(exists()
                                 .where(Subscribed.telegram_id == telegram_id)
                                 .where(Subscribed.subscription_end_datetime > datetime.now())
                                 .select())
        )


async def is_user_subscribed_is_exist(session, telegram_id):
    return bool(await session.scalar(exists().where(Subscribed.telegram_id == telegram_id).select()))


async def is_user_exist(session, telegram_id):
    return bool(await session.scalar(exists().where(User.telegram_id == telegram_id).select()))


async def is_notification_exist(session, symbol, interval):
    return bool(await session.scalar(
        exists().where(Notification.symbol == symbol).where(Notification.interval == interval).select()
    ))


async def is_user_notification_exist(session, user_id, notification_id):
    return bool(await session.scalar(
        exists()
        .where(NotificationUser.user_id == user_id)
        .where(NotificationUser.notification_id == notification_id).select()
    ))


async def is_user_admin(telegram_id):
    async with async_session() as session:
        return bool(await session.scalar(
            exists()
            .where(User.telegram_id == telegram_id)
            .where(User.is_superuser == 1).select()
        ))


async def insert_subscribed(session, telegram_id):
    subscription_end_datetime = datetime.strptime('2024-04-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    subscribed = Subscribed(telegram_id=telegram_id, subscription_end_datetime=subscription_end_datetime)
    session.add(subscribed)
    await session.commit()


async def insert_subscribed_is_not_exist(telegram_id):
    async with async_session() as session:
        if not await is_user_subscribed_is_exist(session, telegram_id):
            await insert_subscribed(session, telegram_id)
            return True
        return False


async def insert_user(session, telegram_id):
    user = User(telegram_id=telegram_id)
    session.add(user)
    await session.commit()


async def insert_user_is_not_exist(telegram_id):
    async with async_session() as session:
        if not await is_user_exist(session, telegram_id):
            await insert_user(session, telegram_id)
            return True
        return False


async def insert_notification(symbol, interval):
    async with async_session() as session:
        if not await is_notification_exist(session, symbol, interval):
            notification = Notification(symbol=symbol, interval=interval)
            session.add(notification)
            await session.commit()
            return True
        return False


async def insert_user_notification(notification_id, user_id):
    async with async_session() as session:
        if not await is_user_notification_exist(session, user_id, notification_id):
            user_notification = NotificationUser(user_id=user_id, notification_id=notification_id, is_active=True)
            session.add(user_notification)
            await session.commit()
            return True
        return False


async def select_subscription_end_datetime_by_telegram_id(telegram_id):
    async with async_session() as session:
        user_subscribe = await session.execute(select(Subscribed).where(Subscribed.telegram_id == telegram_id))
        user_subscribe = user_subscribe.scalars().first()
    return user_subscribe.subscription_end_datetime


async def select_user_id_by_telegram_id(telegram_id):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user.scalars().first()
    return user.id


async def select_notifications():
    async with async_session() as session:
        notifications = await session.execute(select(Notification))
    return notifications.scalars().all()


async def select_user_notifications_by_user_id(user_id):
    async with async_session() as session:
        notifications = await session.execute(
            select(Notification).join(NotificationUser)
            .where(NotificationUser.user_id == user_id)
        )
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


async def select_notification_by_user_id_and_notification_id(user_id, notification_id):
    async with async_session() as session:
        notification = await session.execute(
            select(NotificationUser).join(Notification).join(User)
            .where(User.id == user_id)
            .where(Notification.id == notification_id)
        )
    return notification.scalars().first()


async def select_notification_by_symbol_and_interval(symbol, interval):
    async with async_session() as session:
        notification = await session.execute(
            select(Notification).where(Notification.symbol == symbol)
            .where(Notification.interval == interval)
        )
    return notification.scalars().first()


async def select_user_notification_by_user_id_and_notification_id(user_id, notification_id):
    async with async_session() as session:
        user_notification = await session.execute(
            select(NotificationUser).join(Notification).join(User)
            .where(User.id == user_id)
            .where(Notification.id == notification_id)
        )
    return user_notification.scalars().first()


async def update_notifications_status(telegram_id: int, is_notifications: bool):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user.scalars().first()
        user.is_notifications = is_notifications
        await session.commit()


async def update_user_notification_status(user_notification, is_active):
    async with async_session() as session:
        user_notification = await session.execute(
            select(NotificationUser).join(Notification).join(User)
            .where(User.id == user_notification.user_id)
            .where(Notification.id == user_notification.notification_id)
        )
        user_notification = user_notification.scalars().first()
        user_notification.is_active = is_active
        await session.commit()


async def update_subscription_end_datetime(telegram_id, subscription_end_datetime):
    subscription_end_datetime = datetime.strptime(subscription_end_datetime, '%Y-%m-%d %H:%M:%S')

    async with async_session() as session:
        user_subscription = await session.execute(select(Subscribed).where(Subscribed.telegram_id == telegram_id))
        user_subscription = user_subscription.scalars().first()
        user_subscription.subscription_end_datetime = subscription_end_datetime
        await session.commit()


async def async_model_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
