from typing import Any

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    data_quality: dict[str, Any]
    summary: dict[str, Any]
    at_risk_customers: list[dict[str, Any]]
    customer_metrics: list[dict[str, Any]]
    feedback_patterns: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
