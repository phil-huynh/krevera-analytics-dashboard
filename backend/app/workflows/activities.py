import asyncio
import hashlib
import json
import httpx
from pathlib import Path
from temporalio import activity
from typing import Dict, Any
from sqlalchemy import text
from datetime import datetime

from app.core.database import SessionLocal
from app.models import Product, MachineState, Defect
from app.services.s3_service import s3_service


@activity.defn
async def download_dataset(url: str) -> Dict[str, Any]:
    """Download dataset and return metadata."""
    activity.logger.info(f"Downloading dataset from {url}")

    if url.startswith("file://"):
        filepath = url.replace("file://", "")
        activity.logger.info(f"Reading local file: {filepath}")
        with open(filepath, 'rb') as f:
            data_bytes = f.read()
    else:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                activity.logger.info(f"Download attempt {attempt + 1}/{max_retries}")

                async with httpx.AsyncClient(
                    timeout=300.0,
                    follow_redirects=True,
                    http2=True
                ) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    data_bytes = response.content
                    break

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if attempt < max_retries - 1:
                    activity.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    activity.logger.error(f"All {max_retries} attempts failed")
                    raise

        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json', dir='/tmp')
        temp_file.write(data_bytes)
        temp_file.close()
        filepath = temp_file.name
        activity.logger.info(f"Saved to temp file: {filepath}")

    data_hash = hashlib.sha256(data_bytes).hexdigest()

    activity.logger.info(f"Downloaded {len(data_bytes)} bytes (hash: {data_hash[:8]}...)")

    return {
        "url": url,
        "hash": data_hash,
        "size_bytes": len(data_bytes),
        "filepath": filepath,
    }


@activity.defn
async def upload_to_s3(dataset_info: Dict[str, Any]) -> str:
    """Upload dataset to S3."""
    filepath = dataset_info.get("filepath")

    if not filepath:
        raise ValueError("No filepath provided for S3 upload")

    with open(filepath, 'rb') as f:
        file_bytes = f.read()

    s3_key = f"datasets/{dataset_info['hash']}.json"
    s3_uri = s3_service.upload_file(file_bytes, s3_key)

    activity.logger.info(f"Uploaded {len(file_bytes)} bytes to {s3_uri}")
    return s3_uri


@activity.defn
async def batch_insert_to_db(dataset_info: Dict[str, Any]) -> Dict[str, int]:
    """Parse and insert dataset into database."""

    activity.logger.info("Starting database insertion")

    filepath = dataset_info.get("filepath")
    if not filepath:
        raise ValueError("No filepath provided")

    with open(filepath, 'r') as f:
        data = json.load(f)

    activity.logger.info(f"Parsed {len(data)} records")

    db = SessionLocal()
    try:
        activity.logger.info("Clearing existing data...")
        db.execute(text("TRUNCATE products CASCADE"))
        db.commit()

        products_count = 0
        machine_states_count = 0
        defects_count = 0

        batch_size = 500
        for i, record in enumerate(data):
            if i % batch_size == 0:
                activity.logger.info(f"Processing batch {i // batch_size + 1} ({i}/{len(data)})")

            product = Product(
                version=record.get("version"),
                timestamp=datetime.fromtimestamp(record.get("timestamp")),
                molding_machine_id=record.get("molding_machine_id"),
                overall_reject=record.get("object_detection", {}).get("reject", False),
                defect_count=0,
                total_severity_score=0.0,
            )
            db.add(product)
            db.flush()
            products_count += 1


            machine_data = record.get("molding-machine-state", {})
            machine_state = MachineState(
                product_id=product.id,
                cycle_time=machine_data.get("CycleTime"),
                shot_count=machine_data.get("ShotCount"),
            )
            db.add(machine_state)
            machine_states_count += 1

            object_detection = record.get("object_detection", {})
            defect_mapping = {
                "discoloration_defect": "discoloration_defect",
                "discoloration_patch_defect": "discoloration_patch_defect",
                "flash_defect": "flash_defect",
                "short_defect": "short_defect",
                "contamination_defect": "contamination_defect",
                "splay_defect": "splay_defect",
                "burn_mark_defect": "burn_mark_defect",
                "jetting_defect": "jetting_defect",
                "flow_mark_defect": "flow_mark_defect",
                "sink_mark_defect": "sink_mark_defect",
                "knit_line_defect": "knit_line_defect",
                "void_defect": "void_defect",
                "ejector_pin_mark_defect": "ejector_pin_mark_defect",
            }

            product_defect_count = 0
            for defect_key, defect_type in defect_mapping.items():
                defect_data = object_detection.get(defect_key)
                if defect_data and defect_data.get("reject"):
                    pixel_severity = defect_data.get("pixel_severity", {})
                    defect = Defect(
                        product_id=product.id,
                        defect_type=defect_type,
                        pixel_severity_value=pixel_severity.get("value", 0.0),
                        pixel_severity_reject=pixel_severity.get("reject", False),
                        reject=defect_data.get("reject", False)
                    )
                    db.add(defect)
                    defects_count += 1
                    product_defect_count += 1

            product.defect_count = product_defect_count

            if (i + 1) % batch_size == 0:
                db.commit()

        db.commit()

        activity.logger.info(
            f"Inserted {products_count} products, {machine_states_count} machine states"
        )

        return {
            "products": products_count,
            "machine_states": machine_states_count,
            "defects": defects_count,
        }

    except Exception as e:
        db.rollback()
        activity.logger.error(f"Database insertion failed: {e}")
        raise
    finally:
        db.close()