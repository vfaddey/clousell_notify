from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_user_id, get_notification_service
from src.schemas.notification import NotificationOut
from src.services.notification_service import NotificationService

router = APIRouter(prefix='/notifications', tags=['Notifications'])

@router.get('/unread', response_model=list[NotificationOut])
async def get_unread_notifications(user_id: UUID = Depends(get_user_id),
                                   notification_service: NotificationService = Depends(get_notification_service)):
    result = await notification_service.get_unread(user_id)
    return result


@router.get('/', response_model=list[NotificationOut])
async def get_last(quantity: Optional[int] = 15,
                   user_id: UUID = Depends(get_user_id),
                   notification_service: NotificationService = Depends(get_notification_service)):
    result = await notification_service.get_last(user_id, quantity)
    return result


@router.patch('/viewed')
async def mark_viewed(notification_ids: list[UUID],
                      user_id: UUID = Depends(get_user_id),
                      notification_service: NotificationService = Depends(get_notification_service)):
    result = await notification_service.set_viewed_many(user_id, notification_ids)
    if result:
        return {'status': 'ok'}
    raise HTTPException(status_code=400, detail='Something went wrong')