from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from backend.platform.storage.models import StorageModel, generate_uuid, current_time_iso

class CognitiveMemory(StorageModel):
    """
    Base model for all enterprise cognitive memories.
    Enforces the Memory Graph relationships and Smart Retrieval metadata.
    """
    category: str = "general"
    priority: str = "normal"
    importance_score: int = Field(default=50, ge=0, le=100)
    confidence: int = Field(default=50, ge=0, le=100)
    business_impact: int = Field(default=50, ge=0, le=100)
    retrieval_frequency: int = 0
    last_access_time: Optional[str] = None
    
    tags: List[str] = Field(default_factory=list)
    related_memory_ids: List[str] = Field(default_factory=list)
    
    # Knowledge Graph Relationship Schemas
    references: List[str] = Field(default_factory=list)
    derived_from: List[str] = Field(default_factory=list)
    contradicts: List[str] = Field(default_factory=list)
    supports: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    
    business_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: str = "default_user"  # Strict multi-tenancy enforcement
    lifecycle_state: str = "active" # active, archived, deleted
    source_agent: str = "system"
    
    # Versioning and Audit
    version: int = 1
    audit_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Future embedding placeholder (JSON array of floats for VectorStore simulation)
    embedding_placeholder: Optional[List[float]] = None

class ConversationMemory(CognitiveMemory):
    """Stores full conversation contexts, summaries, and linguistic traits."""
    category: str = "conversation"
    role: str = "user"
    content: str
    is_summary: bool = False
    language: str = "en"
    key_facts: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)

class DecisionMemory(CognitiveMemory):
    """Stores every executed AI decision."""
    category: str = "decision"
    original_question: str
    business_context: str
    collected_evidence: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    universes: List[Dict[str, Any]] = Field(default_factory=list)
    debate: Dict[str, Any] = Field(default_factory=dict)
    recommendation: str
    final_outcome: Optional[str] = None
    decision_status: str = "completed"

class LearningMemory(CognitiveMemory):
    """Stores what the AI learned after decisions and corrections."""
    category: str = "learning"
    lessons_learned: List[str] = Field(default_factory=list)
    prediction_errors: List[str] = Field(default_factory=list)
    successful_strategies: List[str] = Field(default_factory=list)
    failed_strategies: List[str] = Field(default_factory=list)
    confidence_changes: Dict[str, int] = Field(default_factory=dict)
    self_corrections: List[str] = Field(default_factory=list)

class KnowledgeMemory(CognitiveMemory):
    """Stores reusable facts and deduplicated insights."""
    category: str = "knowledge"
    domain: str
    insight: str
    source_document: Optional[str] = None
    framework: Optional[str] = None

class MonitoringMemory(CognitiveMemory):
    """Stores system health, failures, and execution times."""
    category: str = "monitoring"
    event_name: str
    is_failure: bool = False
    execution_time_ms: int = 0
    system_health_status: str = "healthy"
    alert_details: Optional[str] = None

class UserProfileMemory(CognitiveMemory):
    """Stores long-term user profiles."""
    category: str = "user_profile"
    business_name: Optional[str] = None
    industry: Optional[str] = None
    goals: List[str] = Field(default_factory=list)
    risk_appetite: str = "moderate"
    preferred_language: str = "en"
    preferred_report_style: str = "executive"
    decision_style: str = "data_driven"
    favorite_tools: List[str] = Field(default_factory=list)
    frequently_asked_topics: List[str] = Field(default_factory=list)

class SessionMemory(CognitiveMemory):
    """Tracks resumable session states."""
    category: str = "session"
    tools_used: List[str] = Field(default_factory=list)
    generated_reports: List[str] = Field(default_factory=list)
    is_resumable: bool = True

class AgentStateMemory(CognitiveMemory):
    """Maintains state for multi-agent workflows."""
    category: str = "agent_state"
    current_task: str
    intermediate_reasoning: List[str] = Field(default_factory=list)
    tool_execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    debate_state: Dict[str, Any] = Field(default_factory=dict)
    simulation_state: Dict[str, Any] = Field(default_factory=dict)
    planner_state: Dict[str, Any] = Field(default_factory=dict)
    active_objectives: List[str] = Field(default_factory=list)

class DigitalTwinMemory(CognitiveMemory):
    """Persists the business digital twin state over time."""
    category: str = "digital_twin"
    business_profile: Dict[str, str] = Field(default_factory=dict)
    organization_structure: Dict[str, str] = Field(default_factory=dict)
    financial_snapshot: Dict[str, Any] = Field(default_factory=dict)
    operational_kpis: Dict[str, Any] = Field(default_factory=dict)
    market_position: str = ""
    strategic_goals: List[str] = Field(default_factory=list)
    simulation_history: List[str] = Field(default_factory=list) # IDs of past simulation sessions
    last_updated_timestamp: Optional[str] = None

