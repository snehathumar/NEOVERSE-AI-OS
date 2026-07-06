from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from enum import Enum

def generate_uuid() -> str:
    return str(uuid.uuid4())

def current_time_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class StorageModel(BaseModel):
    """Base class for all entities stored in the DB."""
    id: str = Field(default_factory=generate_uuid)
    created_at: str = Field(default_factory=current_time_iso)
    updated_at: str = Field(default_factory=current_time_iso)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class User(StorageModel):
    username: str
    email: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)

class Session(StorageModel):
    user_id: str
    active: bool = True
    context: Dict[str, Any] = Field(default_factory=dict)

class Message(StorageModel):
    session_id: str
    role: str
    content: str

class DecisionState(str, Enum):
    PENDING_REVIEW = "Pending Review"
    APPROVED = "Approved"
    APPROVED_WITH_COMMENTS = "Approved with Comments"
    REJECTED = "Rejected"
    OVERRIDE_REQUESTED = "Override Requested"
    OVERRIDE_APPROVED = "Override Approved"
    ESCALATED = "Escalated"
    EXPIRED = "Expired"

class ApprovalHistory(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    previous_state: Optional[str] = None
    new_state: str
    reviewer_id: str
    reviewer_name: str
    reviewer_role: str
    reviewed_at: str = Field(default_factory=current_time_iso)
    justification: Optional[str] = None
    comment: Optional[str] = None
    confidence_score: Optional[int] = None
    
class Decision(StorageModel):
    prompt: str
    facts: List[str] = Field(default_factory=list)
    confidence: int = 0
    recommendation: str
    state: DecisionState = DecisionState.PENDING_REVIEW
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    reviewer_role: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_duration_ms: Optional[int] = None
    approval_level: Optional[str] = None
    approval_source: Optional[str] = None
    review_comments: Optional[str] = None
    final_human_action: Optional[str] = None
    approval_history: List[ApprovalHistory] = Field(default_factory=list)

class Universe(StorageModel):
    decision_id: str
    scenario_name: str
    description: str
    predicted_outcome: str

class Debate(StorageModel):
    decision_id: str
    arguments_for: List[str] = Field(default_factory=list)
    arguments_against: List[str] = Field(default_factory=list)
    resolution: str

class Report(StorageModel):
    decision_id: str
    pdf_path: str
    generated_by: str

class Event(StorageModel):
    event_type: str
    message: str

class Memory(StorageModel):
    session_id: str
    key: str
    value: Any

class Learning(StorageModel):
    context: str
    insight: str
    applied: bool = False

class Analytics(StorageModel):
    metric_name: str
    value: float

class Monitoring(StorageModel):
    component: str
    status: str
    latency_ms: int

class ToolLog(StorageModel):
    tool_name: str
    execution_time_ms: int
    success: bool

class APILog(StorageModel):
    endpoint: str
    status_code: int
    response_time_ms: int
