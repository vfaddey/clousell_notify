import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.adapters.email_sender import SMTPEmailSender
from src.adapters.notification_processor import NotificationProcessorFactory
from src.adapters.rabbitmq_consumer import RabbitMQConsumer
from src.api.v1.notifications import router as notification_router
from src.api.v1.templates import router as template_router
from src.core.config import settings
from src.api.deps import get_template_service, get_notification_service, get_session
from src.db.database import AsyncSessionFactory

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/",
    title=settings.APP_NAME
)

app.include_router(template_router)
app.include_router(notification_router)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
consumer: RabbitMQConsumer

@app.on_event("startup")
async def startup():
    global consumer

    email_sender = SMTPEmailSender(
        smtp_server=settings.SMTP_SERVER,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password=settings.SMTP_PASSWORD
    )

    processor_factory = NotificationProcessorFactory(
        email_sender=email_sender,
        session_factory=AsyncSessionFactory
    )

    consumer = RabbitMQConsumer(
        rabbit_url=settings.RABBITMQ_URL,
        queue=settings.RABBITMQ_QUEUE,
        notification_processor_factory=processor_factory,
    )
    asyncio.create_task(consumer.start_consuming())


@app.on_event("shutdown")
async def shutdown():
    global consumer
    if consumer:
        await consumer.close()