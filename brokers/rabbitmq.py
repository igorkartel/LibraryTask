import aio_pika
from fastapi import HTTPException, status

from configs.logger import logger
from configs.settings import settings


async def connect_to_rabbitmq_channel():
    try:
        connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD,
        )
        return await connection.channel()
    except Exception as e:
        logger.error(f"Failed to connect RabbitMQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An unexpected error occurred. Please try again later",
        )


async def send_message_to_rabbitmq(message, queue_name: str):
    try:
        async with await connect_to_rabbitmq_channel() as channel:
            await channel.declare_queue(queue_name, durable=True, arguments={"x-queue-type": "quorum"})
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key=queue_name,
            )
    except Exception as e:
        logger.error(f"Failed to send a message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An unexpected error occurred. Please try again later",
        )
