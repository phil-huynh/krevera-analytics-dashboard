"""
Analytics API endpoints for manufacturing quality data.
Location: backend/app/api/endpoints/analytics.py
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, case, text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.models.defect import Defect
from app.models.machine_state import MachineState
from app.schemas.analytics import (
    DefectRateTrendResponse,
    DefectRateDataPoint,
    DefectHeatmapResponse,
    HeatmapCell
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ============================================================================
# DEFECT RATE TREND (Time Series Line Chart)
# ============================================================================

@router.get("/defect-rate-trend", response_model=DefectRateTrendResponse)
async def get_defect_rate_trend(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    machine_id: Optional[str] = Query(None, description="Filter by machine ID"),
    interval: str = Query("day", regex="^(hour|day|week)$", description="Time grouping interval")
):
    """
    Get defect rate trend over time for line chart visualization.

    Returns time-series data grouped by hour/day/week showing:
    - Total products produced
    - Number rejected
    - Defect rate percentage

    **Query Pattern:**
    - Uses PostgreSQL date_trunc() for time bucketing
    - Aggregates reject counts
    - Calculates rate as rejected/total
    """

    # Build base query with time truncation
    trunc_format = {
        "hour": "hour",
        "day": "day",
        "week": "week"
    }[interval]

    query = db.query(
        func.date_trunc(trunc_format, Product.timestamp).label("time_bucket"),
        func.count(Product.id).label("total"),
        func.sum(case((Product.overall_reject == True, 1), else_=0)).label("rejected")
    )

    # Apply filters
    if start_date:
        query = query.filter(Product.timestamp >= start_date)
    if end_date:
        query = query.filter(Product.timestamp <= end_date)
    if machine_id:
        query = query.filter(Product.molding_machine_id == machine_id)

    # Group and order
    query = query.group_by("time_bucket").order_by("time_bucket")

    results = query.all()

    # Transform to response format
    data_points = []
    for row in results:
        total = row.total
        rejected = row.rejected or 0
        rate = rejected / total if total > 0 else 0.0

        data_points.append(DefectRateDataPoint(
            timestamp=row.time_bucket,
            total_products=total,
            rejected_products=rejected,
            defect_rate=round(rate, 4)
        ))

    # Calculate summary statistics
    all_totals = [dp.total_products for dp in data_points]
    all_rates = [dp.defect_rate for dp in data_points]

    summary = {
        "avg_rate": round(sum(all_rates) / len(all_rates), 4) if all_rates else 0.0,
        "min_rate": round(min(all_rates), 4) if all_rates else 0.0,
        "max_rate": round(max(all_rates), 4) if all_rates else 0.0,
        "total_products": sum(all_totals)
    }

    return DefectRateTrendResponse(data_points=data_points, summary=summary)




# ============================================================================
# MACHINE-DEFECT HEATMAP (Machine × Defect Type)
# ============================================================================

@router.get("/machine-defect-heatmap")
async def get_machine_defect_heatmap(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Get heatmap showing which machines produce which defect types.
    Much more actionable than arbitrary product IDs!

    Example insight: "Machine 2 produces 80% of all flash defects → check mold clamping"
    """

    query = db.query(
        Product.molding_machine_id,
        Defect.defect_type,
        func.count(Defect.id).label("count")
    ).join(Product, Defect.product_id == Product.id)

    # Apply filters
    if start_date:
        query = query.filter(Product.timestamp >= start_date)
    if end_date:
        query = query.filter(Product.timestamp <= end_date)

    query = query.group_by(Product.molding_machine_id, Defect.defect_type)
    results = query.all()

    if not results:
        return {
            "cells": [],
            "machine_labels": [],
            "defect_labels": [],
            "metadata": {"total_defects": 0, "max_defects_per_cell": 0}
        }

    # Build labels
    machine_labels = sorted(list(set([r.molding_machine_id for r in results])))
    defect_labels = sorted(list(set([r.defect_type for r in results])))

    # Build cells - [machineIndex, defectIndex, count]
    cells = []
    max_count = 0
    total_defects = 0

    for row in results:
        machine_idx = machine_labels.index(row.molding_machine_id)
        defect_idx = defect_labels.index(row.defect_type)
        count = row.count

        cells.append([machine_idx, defect_idx, count])
        max_count = max(max_count, count)
        total_defects += count

    return {
        "cells": cells,
        "machine_labels": machine_labels,
        "defect_labels": defect_labels,
        "metadata": {
            "total_defects": total_defects,
            "max_defects_per_cell": max_count,
            "machine_count": len(machine_labels),
            "defect_type_count": len(defect_labels)
        }
    }


# ============================================================================
# PRODUCT DEFECT DETAILS (For Modal)
# ============================================================================

@router.get("/product/{product_id}/defects")
async def get_product_defects(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed defect information for a specific product.

    Used when clicking a heatmap cell to show details in a modal.
    """

    # Get product info
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}

    # Get all defects for this product
    defects = db.query(Defect).filter(Defect.product_id == product_id).all()

    # Get machine state
    machine_state = db.query(MachineState).filter(
        MachineState.product_id == product_id
    ).first()

    return {
        "product": {
            "id": product.id,
            "timestamp": product.timestamp,
            "machine_id": product.molding_machine_id,
            "overall_reject": product.overall_reject,
            "defect_count": len(defects)
        },
        "defects": [
            {
                "defect_type": d.defect_type,
                "severity": d.pixel_severity_value,
                "reject": d.reject
            }
            for d in defects
        ],
        "machine_state": {
            "cycle_time": machine_state.cycle_time if machine_state else None,
            "shot_count": machine_state.shot_count if machine_state else None
        } if machine_state else None
    }


# ============================================================================
# TOP DEFECTS (Bar Chart)
# ============================================================================

@router.get("/top-defects")
async def get_top_defects(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    machine_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=20)
):
    """
    Get top N most common defect types with counts and percentages.
    """

    # Build base query
    query = db.query(
        Defect.defect_type,
        func.count(Defect.id).label("count")
    ).join(Product, Defect.product_id == Product.id)

    # Apply filters
    if start_date:
        query = query.filter(Product.timestamp >= start_date)
    if end_date:
        query = query.filter(Product.timestamp <= end_date)
    if machine_id:
        query = query.filter(Product.molding_machine_id == machine_id)

    # Group and order
    query = query.group_by(Defect.defect_type).order_by(func.count(Defect.id).desc()).limit(limit)

    results = query.all()

    # Calculate totals for percentages
    total_defects = sum(r.count for r in results)
    affected_products = db.query(func.count(func.distinct(Defect.product_id))).scalar()

    defects = [
        {
            "defect_type": r.defect_type,
            "count": r.count,
            "percentage": (r.count / total_defects * 100) if total_defects > 0 else 0
        }
        for r in results
    ]

    return {
        "defects": defects,
        "summary": {
            "total_defects": total_defects,
            "most_common": defects[0]["defect_type"] if defects else "N/A",
            "affected_products": affected_products or 0
        }
    }


# ============================================================================
# MACHINE COMPARISON (Grouped Bar Chart)
# ============================================================================

@router.get("/machine-comparison")
async def get_machine_comparison(db: Session = Depends(get_db)):
    """
    Compare performance across all machines.
    """

    query = db.query(
        Product.molding_machine_id,
        func.count(Product.id).label("total"),
        func.sum(case((Product.overall_reject == True, 1), else_=0)).label("rejected")
    ).group_by(Product.molding_machine_id)

    results = query.all()

    machines = [
        {
            "machine_id": r.molding_machine_id,
            "total": r.total,
            "rejected": r.rejected or 0,
            "accepted": r.total - (r.rejected or 0),
            "defect_rate": (r.rejected or 0) / r.total if r.total > 0 else 0
        }
        for r in results
    ]

    return {"machines": machines}


# ============================================================================
# DEFECT COUNT DISTRIBUTION (Histogram - replaces pie chart)
# ============================================================================

@router.get("/defect-distribution")
async def get_defect_distribution(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    machine_id: Optional[str] = Query(None)
):
    """
    Get distribution of products by defect count (0, 1, 2, 3, 4, 5+ defects).
    Much more useful than simple accept/reject pie chart.
    Shows: How many products have exactly N defects?
    """

    # Subquery to count defects per product
    defect_counts = db.query(
        Product.id,
        func.count(Defect.id).label("defect_count")
    ).outerjoin(Defect, Product.id == Defect.product_id)

    # Apply filters
    if start_date:
        defect_counts = defect_counts.filter(Product.timestamp >= start_date)
    if end_date:
        defect_counts = defect_counts.filter(Product.timestamp <= end_date)
    if machine_id:
        defect_counts = defect_counts.filter(Product.molding_machine_id == machine_id)

    defect_counts = defect_counts.group_by(Product.id).subquery()

    # Count how many products fall into each bucket
    distribution_query = db.query(
        defect_counts.c.defect_count,
        func.count(defect_counts.c.id).label("product_count")
    ).group_by(defect_counts.c.defect_count).order_by(defect_counts.c.defect_count)

    results = distribution_query.all()

    # Build buckets: 0, 1, 2, 3, 4, 5+
    buckets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, '5+': 0}
    total_products = 0

    for row in results:
        count = row.defect_count
        product_count = row.product_count
        total_products += product_count

        if count >= 5:
            buckets['5+'] += product_count
        else:
            buckets[count] = product_count

    # Convert to list format
    distribution = [
        {"defect_count": k, "product_count": v, "percentage": (v / total_products * 100) if total_products > 0 else 0}
        for k, v in buckets.items()
    ]

    return {
        "distribution": distribution,
        "summary": {
            "total_products": total_products,
            "zero_defects": buckets[0],
            "perfect_rate": (buckets[0] / total_products * 100) if total_products > 0 else 0
        }
    }


# ============================================================================
# CYCLE TIME SCATTER (Correlation Analysis)
# ============================================================================

@router.get("/cycle-time-scatter")
async def get_cycle_time_scatter(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    machine_id: Optional[str] = Query(None),
    limit: int = Query(500, ge=100, le=2000)
):
    """
    Get cycle time vs defect count for scatter plot correlation analysis.
    Shows ALL products (both accepted and rejected) to reveal true correlation.
    """

    query = db.query(
        Product.id,
        MachineState.cycle_time,
        func.count(Defect.id).label("defect_count"),
        Product.overall_reject
    ).join(MachineState, Product.id == MachineState.product_id
    ).outerjoin(Defect, Product.id == Defect.product_id)

    # Apply filters
    if start_date:
        query = query.filter(Product.timestamp >= start_date)
    if end_date:
        query = query.filter(Product.timestamp <= end_date)
    if machine_id:
        query = query.filter(Product.molding_machine_id == machine_id)

    # REMOVED: query = query.filter(Product.overall_reject == True)
    # NOW SHOWS ALL PRODUCTS - both accepted (0 defects) and rejected (1+ defects)

    query = query.group_by(Product.id, MachineState.cycle_time, Product.overall_reject)
    query = query.limit(limit)

    results = query.all()

    points = [
        {
            "cycle_time": float(r.cycle_time) if r.cycle_time else 0,
            "defect_count": r.defect_count,
            "product_id": r.id,
            "is_rejected": r.overall_reject
        }
        for r in results if r.cycle_time is not None
    ]

    # Calculate correlation and statistics
    if len(points) > 1:
        import statistics
        cycle_times = [p["cycle_time"] for p in points]
        defect_counts = [p["defect_count"] for p in points]

        avg_cycle = statistics.mean(cycle_times)
        avg_defects = statistics.mean(defect_counts)

        # Separate accepted vs rejected
        accepted = [p for p in points if not p["is_rejected"]]
        rejected = [p for p in points if p["is_rejected"]]

        try:
            correlation = statistics.correlation(cycle_times, defect_counts)
        except:
            correlation = 0
    else:
        avg_cycle = 0
        avg_defects = 0
        correlation = 0
        accepted = []
        rejected = []

    return {
        "points": points,
        "stats": {
            "average_cycle_time": round(avg_cycle, 2),
            "average_defect_count": round(avg_defects, 2),
            "correlation": round(correlation, 3),
            "sample_size": len(points),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected)
        }
    }


@router.get("/machines")
async def get_machines(
    db: Session = Depends(get_db)
):
    """
    Get list of all unique machines in the database
    """
    try:
        machines = db.query(Product.molding_machine_id).distinct().all()
        machine_list = [m[0] for m in machines if m[0]]  # Filter out None values

        return {
            "machines": sorted(machine_list),  # Sort alphabetically
            "count": len(machine_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))