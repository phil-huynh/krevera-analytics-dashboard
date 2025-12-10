from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from typing import Dict, Any


@workflow.defn
class DataIngestionWorkflow:
    @workflow.run
    async def run(self, url: str) -> Dict[str, Any]:
        workflow.logger.info(f"Starting data ingestion for: {url}")

        dataset_info = await workflow.execute_activity(
            "download_dataset",
            url,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        workflow.logger.info(f"Downloaded {dataset_info['size_bytes']} bytes")

        s3_uri = await workflow.execute_activity(
            "upload_to_s3",
            dataset_info,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        workflow.logger.info(f"Uploaded to S3: {s3_uri}")

        stats = await workflow.execute_activity(
            "batch_insert_to_db",
            dataset_info,
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )

        workflow.logger.info(f"Inserted {stats['products']} products")

        return {
            "url": url,
            "s3_uri": s3_uri,
            "dataset_hash": dataset_info["hash"],
            "dataset_size_bytes": dataset_info["size_bytes"],
            "statistics": stats,
            "status": "completed",
        }