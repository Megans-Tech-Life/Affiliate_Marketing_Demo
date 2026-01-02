from pydantic import BaseModel
from typing import List

class DashboardMetric(BaseModel):
    name: str
    total: int

class DashboardResponse(BaseModel):
    metrics: List[DashboardMetric]