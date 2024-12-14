import asyncio
import json
from threading import Thread

import aio_pika
import logging

from aio_pika import IncomingMessage

from src.adapters.notification_processor import NotificationProcessorFactory
from src.exceptions.base import CloudsellNotifyException
from src.schemas.notification import NotificationCreate

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self,
                 rabbit_url: str,
                 queue: str,
                 notification_processor_factory: NotificationProcessorFactory):
        self.rabbit_url = rabbit_url
        self.queue = queue
        self.notification_processor_factory = notification_processor_factory
        self.connection = None
        self.channel = None
        self.queue_object = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(self.rabbit_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            self.queue_object = await self.channel.declare_queue(self.queue, durable=True)
            logger.info(f"Connected to RabbitMQ and declared queue '{self.queue}'")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise e

    async def start_consuming(self):
        await self.connect()
        await self.queue_object.consume(self.on_message)
        logger.info("Started consuming messages")

    async def on_message(self, message: IncomingMessage):
        async with message.process():
            try:
                body = message.body.decode()
                data = json.loads(body)
                notification = NotificationCreate(**data)
                logger.info(f"Received notification: {notification}")
                Thread(target=self.do_task, args=(notification,), daemon=True).start()
                logger.info(f"Working with notification: {notification}")
            except CloudsellNotifyException as e:
                logger.error(f"Error processing message: {e}")

    def do_task(self, notification: NotificationCreate):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.__work(notification))
        finally:
            loop.close()

    async def __work(self, notification: NotificationCreate):
        processor = await self.notification_processor_factory.get_processor(notification.type)
        await processor.process(notification)

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
