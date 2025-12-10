from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class DefectRateDataPoint(BaseModel):
    timestamp: datetime
    total_products: int = Field(..., ge=0)
    rejected_products: int = Field(..., ge=0)
    defect_rate: float = Field(..., ge=0, le=1)


class DefectRateTrendResponse(BaseModel):
    data_points: List[DefectRateDataPoint]
    summary: Dict[str, float]


class HeatmapCell(BaseModel):
    product_id: int
    defect_type: str
    count: int = Field(..., ge=0)


class DefectHeatmapResponse(BaseModel):
    cells: List[HeatmapCell]
    product_labels: List[int]
    defect_labels: List[str]
    metadata: Dict[str, int]


class TimeRangeParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    machine_id: Optional[str] = None