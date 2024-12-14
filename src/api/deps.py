from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.exceptions import InvalidToken
from src.core.jwt_decoder import JWTDecoder
from src.db.database import AsyncSessionFactory
from src.exceptions.base import CloudsellNotifyException
from src.repositories.admin_repository import SqlaAdminRepository
from src.repositories.notification_repository import SqlaNotificationRepository
from src.repositories.template_repository import SqlaTemplateRepository
from src.services.admin_service import AdminService
from src.services.notification_service import NotificationService
from src.services.template_service import TemplateService

http_bearer = HTTPBearer()


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_admin_service(session: AsyncSession = Depends(get_session)) -> AdminService:
    repository = SqlaAdminRepository(session)
    return AdminService(repository)

def get_notification_service(session: AsyncSession = Depends(get_session)) -> NotificationService:
    repository = SqlaNotificationRepository(session)
    return NotificationService(repository)

def get_template_service(session: AsyncSession = Depends(get_session)) -> TemplateService:
    repository = SqlaTemplateRepository(session)
    return TemplateService(repository)


async def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> UUID:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = JWTDecoder.decode(token)
        if not token_data.get('sub'):
            raise credentials_exception
        return token_data["sub"]
    except InvalidToken as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
                            admin_service: AdminService = Depends(get_admin_service)):
    token = credentials.credentials
    try:
        admin = await admin_service.verify_admin(token)
        return admin
    except CloudsellNotifyException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))