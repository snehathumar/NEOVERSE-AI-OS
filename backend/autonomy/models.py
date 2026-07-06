from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class SystemEvent(BaseModel):
    event_id: str
    event_type: str # system_warning, system_failure, performance_degradation, auto_scale_trigger, auto_repair_action
    timestamp: str
    component: str
    severity: str # info, warning, critical
    details: Dict[str, Any]

class ResourceMetric(BaseModel):
    timestamp: str
    api_latency_ms: float
    cpu_utilization_pct: float
    memory_utilization_pct: float
    queue_depth: int

class RCAReport(BaseModel):
    report_id: str
    timestamp: str
    trigger_event_id: str
    root_cause_summary: str
    suggested_fix: str
    confidence_score: float

class ScalingDecision(BaseModel):
    timestamp: str
    target_component: str
    current_replicas: int
    desired_replicas: int
    reason: str
