from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class BiasReport(BaseModel):
    source_bias: int = Field(default=0, ge=0, le=100)
    temporal_bias: int = Field(default=0, ge=0, le=100)
    confirmation_bias: int = Field(default=0, ge=0, le=100)
    overall_bias_score: int = Field(default=0, ge=0, le=100)
    explanation: str

class VerificationStatus(BaseModel):
    is_verified: bool
    verified_by: List[str]
    contradictions_found: bool

class EvidenceItem(BaseModel):
    id: str
    source_name: str
    source_type: str
    title: str
    content_summary: str
    author: Optional[str]
    timestamp: str
    trust_score: int = Field(default=50, ge=0, le=100)
    confidence: int = Field(default=50, ge=0, le=100)
    freshness: str # Real-Time, Recent, Current, Historical, Outdated
    relevance_score: int = Field(default=50, ge=0, le=100)
    verification: VerificationStatus
    bias_report: BiasReport
    citation_metadata: Dict[str, Any]

class SourceReputation(BaseModel):
    source_name: str
    reliability_score: int = Field(default=50, ge=0, le=100)
    historical_accuracy: int = Field(default=50, ge=0, le=100)
    trust_trend: str
    usage_frequency: int = 0
    verification_history: List[Dict[str, Any]]
    last_updated: str

class ConflictReport(BaseModel):
    conflicting_sources: List[str]
    trust_scores: Dict[str, int]
    confidence_levels: Dict[str, int]
    possible_reasons_for_conflict: str
    recommended_resolution: str
    additional_evidence_required: List[str]

class KnowledgeGraphNode(BaseModel):
    id: str
    label: str
    type: str # Evidence, Claim, Decision, Assumption, Risk, Opportunity
    properties: Dict[str, Any]

class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relationship: str # supports, contradicts, derives_from, infers

class ResearchTrace(BaseModel):
    evidence_collected: List[EvidenceItem]
    conflict_reports: List[ConflictReport]
    graph_nodes: List[KnowledgeGraphNode]
    graph_edges: List[KnowledgeGraphEdge]
    explanation: Dict[str, str] # Why selected, why rejected, most influential, uncertain
    minimum_trust_threshold_used: int
    is_sufficient: bool
