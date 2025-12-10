import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from app.workflows.ingestion import DataIngestionWorkflow
from app.workflows.activities import download_dataset, upload_to_s3, batch_insert_to_db
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info(f"Connecting to Temporal at {settings.TEMPORAL_HOST}")

    client = await Client.connect(settings.TEMPORAL_HOST)

    logger.info("Starting Temporal worker on task queue: data-ingestion")

    worker = Worker(
        client,
        task_queue="data-ingestion",
        workflows=[DataIngestionWorkflow],
        activities=[download_dataset, upload_to_s3, batch_insert_to_db],
    )

    logger.info("✅ Temporal worker started and ready to process workflows")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())