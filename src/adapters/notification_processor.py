import asyncio
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.email_sender import EmailSender
from src.api.deps import get_template_service, get_notification_service
from src.models.notifications import NotificationType
from src.schemas.notification import NotificationCreate
from src.schemas.template import TemplateOut
from jinja2 import Template as JinjaTemplate



class NotificationProcessorFactory:
    def __init__(self,
                 email_sender: EmailSender,
                 session_factory):
        self.email_sender = email_sender
        self.session_factory = session_factory
        self.processors = {
            NotificationType.EMAIL: EmailNotificationProcessor,
            NotificationType.SITE: SiteNotificationProcessor
        }

    async def get_processor(self, notification_type: NotificationType):
        processor_class = self.processors.get(notification_type)
        async with self.session_factory() as session:
            if not processor_class:
                raise ValueError(f"No processor found for notification type: {notification_type}")
            return processor_class(session, email_sender=self.email_sender)



class NotificationProcessor(ABC):

    # def process(self, notification: NotificationCreate):
    #     asyncio.run(self._process(notification))

    async def process(self, notification: NotificationCreate):
        await self._process(notification)

    @abstractmethod
    async def _process(self, notification: NotificationCreate):
        raise NotImplementedError


class EmailNotificationProcessor(NotificationProcessor):
    def __init__(self,
                 session: AsyncSession,
                 email_sender: EmailSender):
        self._notification_service = get_notification_service(session)
        self._template_service = get_template_service(session)
        self._email_sender = email_sender

    async def _process(self, notification: NotificationCreate):
        if not notification.email:
            raise
        if not notification.template_id:
            raise
        template: TemplateOut = await self._template_service.get(notification.template_id)
        email_fields: dict = notification.extra_data
        if not self.__validate_fields(template.required_fields, email_fields):
            raise
        if not email_fields:
            raise

        subject, body = self.__render_email(template, email_fields)
        inserted_notification = await self._notification_service.create(notification)
        result = await self._email_sender.send_email_html(notification.email, subject, body)
        return result

    def __validate_fields(self, required_fields: str, to_validate: dict) -> bool:
        required_fields_list = required_fields.split()
        to_validate_list = to_validate.keys()
        if set(required_fields_list) == set(to_validate_list):
            return True
        return False

    def __render_email(self, template: TemplateOut, data: dict):
        subject_template = JinjaTemplate(template.subject)
        body_template = JinjaTemplate(template.body)

        rendered_subject = subject_template.render(**data)
        rendered_body = body_template.render(**data)
        return rendered_subject, rendered_body


class SiteNotificationProcessor(NotificationProcessor):
    def __init__(self,
                 session: AsyncSession,
                 **kwargs):
        self._notification_service = get_notification_service(session)

    async def _process(self, notification: NotificationCreate):
        result = await self._notification_service.create(notification)
        return result