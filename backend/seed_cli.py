import asyncio
import argparse
import sys
from datetime import datetime
from temporalio.client import Client

from app.workflows.ingestion import DataIngestionWorkflow
from app.core.config import settings


async def seed_database(url: str) -> None:
    print(f"🚀 Starting data ingestion workflow")
    print(f"📊 Dataset URL: {url}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        print(f"🔌 Connecting to Temporal at {settings.TEMPORAL_HOST}...")
        client = await Client.connect(settings.TEMPORAL_HOST)
        print("✅ Connected to Temporal")
        print()

        workflow_id = f"data-ingestion-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        print(f"🎬 Starting workflow: {workflow_id}")
        handle = await client.start_workflow(
            DataIngestionWorkflow.run,
            url,
            id=workflow_id,
            task_queue="data-ingestion",
        )

        print(f"⏳ Workflow running (ID: {workflow_id})")
        print("   This may take several minutes for large datasets...")
        print()

        result = await handle.result()

        print("=" * 60)
        print("✅ DATA INGESTION COMPLETED!")
        print("=" * 60)
        print()
        print(f"📍 S3 Location: {result['s3_uri']}")
        print(f"🔐 Dataset Hash: {result['dataset_hash'][:16]}...")
        print(f"📦 Dataset Size: {result['dataset_size_bytes']:,} bytes")
        print()
        print("📊 Records Inserted:")
        print(f"   Products:        {result['statistics']['products']:,}")
        print(f"   Machine States:  {result['statistics']['machine_states']:,}")
        print(f"   Defects:         {result['statistics']['defects']:,}")
        print()
        print("⏰ Completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print()

    except Exception as e:
        print()
        print("❌ ERROR: Data ingestion failed")
        print(f"   {type(e).__name__}: {e}")
        print()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Seed database with manufacturing quality data")
    parser.add_argument("--url", required=True, help="URL of dataset JSON file to download and ingest")
    args = parser.parse_args()
    asyncio.run(seed_database(args.url))


if __name__ == "__main__":
    main()