from typing import Sequence
from uuid import UUID
from abc import ABC, abstractmethod

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import NotificationType
from src.models.notifications import Notification


class NotificationRepository(ABC):
    @abstractmethod
    async def create(self, notification):
        raise NotImplementedError

    @abstractmethod
    async def update(self, notification):
        raise NotImplementedError

    @abstractmethod
    async def get(self, notification_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    async def get_unread(self, user_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    async def set_viewed_many(self, user_id: int | UUID, notification_ids: list[UUID]):
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, user_id: int | UUID, quantity: int = None):
        raise NotImplementedError


class SqlaNotificationRepository(NotificationRepository):

    def __init__(self, session: AsyncSession):
        self._session = session


    async def create(self, notification: Notification) -> Notification:
        try:
            self._session.add(notification)
            await self._session.commit()
            await self._session.refresh(notification)
            return notification
        except:
            await self._session.rollback()
            raise

    async def update(self, notification: Notification) -> Notification:
        try:
            self._session.add(notification)
            await self._session.commit()
            await self._session.refresh(notification)
            return notification
        except:
            await self._session.rollback()
            raise

    async def get(self, notification_id: int | UUID) -> Notification:
        stmt = select(Notification).where(Notification.id == notification_id)
        notification = await self._session.execute(stmt)
        return notification.unique().scalars().first()

    async def get_by_user_id(self, user_id: int | UUID) -> Sequence[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        notifications = await self._session.execute(stmt)
        return notifications.scalars().all()

    async def get_unread(self, user_id: int | UUID):
        stmt = select(Notification).where(Notification.user_id == user_id,
                                          Notification.viewed == False,
                                          Notification.type == NotificationType.SITE)
        notifications = await self._session.execute(stmt)
        return notifications.unique().scalars().all()

    async def set_viewed_many(self, user_id: UUID, notification_ids: list[UUID]):
        stmt = (
            update(Notification)
            .where(Notification.id.in_(notification_ids), Notification.user_id == user_id)
            .values(viewed=True)
            .execution_options(synchronize_session="fetch")
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result

    async def get_many(self, user_id: int | UUID, quantity: int = None):
        if not quantity:
            stmt = select(Notification).where(Notification.user_id == user_id)
            notifications = await self._session.execute(stmt)
            return notifications.scalars().all()
        stmt = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at).limit(quantity)
        notifications = await self._session.execute(stmt)
        return notifications.scalars().all()