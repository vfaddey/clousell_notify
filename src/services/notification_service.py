from uuid import UUID

from src.exceptions.notification import NotificationInsertFailed
from src.models.notifications import Notification
from src.repositories.notification_repository import NotificationRepository
from src.schemas.notification import NotificationOut, NotificationCreate


class NotificationService:
    def __init__(self,
                 repository: NotificationRepository):
        self.__repository = repository

    async def create(self, notification: NotificationCreate) -> NotificationOut:
        try:
            to_insert = Notification(**notification.dict())
            inserted = await self.__repository.create(to_insert)
            return NotificationOut.from_orm(inserted)
        except Exception as e:
            print(e)
            raise NotificationInsertFailed('Failed to create notification')

    async def get_unread(self, user_id: UUID) -> list[NotificationOut]:
        notifications = await self.__repository.get_unread(user_id)
        result = [NotificationOut.from_orm(n) for n in notifications]
        return result

    async def set_viewed_many(self, user_id: UUID, notification_ids: list[UUID]) -> bool:
        result = await self.__repository.set_viewed_many(user_id, notification_ids)
        if result:
            return True

    async def get_last(self, user_id, quantity = 15) -> list[NotificationOut]:
        notifications = await self.__repository.get_many(user_id, quantity)
        result = [NotificationOut.from_orm(n) for n in notifications]
        return result