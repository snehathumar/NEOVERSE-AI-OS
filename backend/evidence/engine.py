import asyncio
from typing import Dict, Any, List

from backend.evidence.providers import InternalMemoryProvider, KnowledgeBaseProvider, WebSearchProvider
from backend.evidence.evaluators import EvidenceEvaluator
from backend.evidence.scorer import TrustScorer
from backend.evidence.graph import EvidenceGraphBuilder
from backend.evidence.models import EvidenceItem, VerificationStatus, ConflictReport, ResearchTrace
from backend.platform.cloud.logging_provider import cloud_logger

class EvidenceTrustEngine:
    """
    Core engine for Enterprise Evidence Trust & Research Intelligence.
    Validates facts and scores trust before reasoning occurs.
    """
    def __init__(self):
        self.providers = [
            InternalMemoryProvider(),
            KnowledgeBaseProvider(),
            WebSearchProvider() # Interface placeholder
        ]
        self.evaluator = EvidenceEvaluator()
        self.scorer = TrustScorer()
        self.graph_builder = EvidenceGraphBuilder()

    def _determine_thresholds(self, decision_type: str) -> dict:
        """Dynamically configure trust threshold and freshness based on domain."""
        config = {
            "Strategic": {"trust": 75, "outdated_days": 365, "historical_days": 180, "recent_days": 30},
            "Financial": {"trust": 85, "outdated_days": 90, "historical_days": 30, "recent_days": 7},
            "Technology": {"trust": 65, "outdated_days": 365, "historical_days": 180, "recent_days": 30},
            "Healthcare": {"trust": 90, "outdated_days": 180, "historical_days": 90, "recent_days": 30},
            "Law": {"trust": 85, "outdated_days": 365*5, "historical_days": 365*2, "recent_days": 90},
            "Default": {"trust": 60, "outdated_days": 365*2, "historical_days": 365, "recent_days": 30}
        }
        return config.get(decision_type, config["Default"])

    async def _fetch_raw_evidence(self, query: str, context: dict) -> List[Dict[str, Any]]:
        tasks = [provider.search(query, context) for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        aggregated = []
        for res in results:
            if isinstance(res, list):
                aggregated.extend(res)
            else:
                cloud_logger.error(f"Provider failed: {res}")
        return aggregated

    async def execute_research(self, query: str, context: dict, max_retries: int = 2) -> Dict[str, Any]:
        decision_type = context.get("business_understanding", {}).get("decision_type", "Default")
        policy = self._determine_thresholds(decision_type)
        minimum_trust = policy["trust"]
        
        cloud_logger.info(f"Starting Evidence Research for query: '{query}' (Target Trust: {minimum_trust})")
        
        final_evidence = []
        conflict_reports = []
        
        for attempt in range(max_retries):
            raw_evidence_list = await self._fetch_raw_evidence(query, context)
            
            # Detect contradictions
            conflicts = self.evaluator.detect_contradictions(raw_evidence_list)
            for c in conflicts:
                conflict_reports.append(ConflictReport(**c))
                
            processed_items = []
            for raw in raw_evidence_list:
                # Mock source reputation for now
                source_rep = 80 if raw["source_type"] == "internal" else 60
                
                bias = self.evaluator.evaluate_bias(raw["content_summary"], raw["source_name"])
                freshness = self.evaluator.determine_freshness(raw["timestamp"], policy)
                
                trust_score = self.scorer.calculate_trust(raw, bias.overall_bias_score, freshness, source_rep)
                
                # Check Verification
                is_verified = trust_score >= minimum_trust
                
                item = EvidenceItem(
                    id=raw["id"],
                    source_name=raw["source_name"],
                    source_type=raw["source_type"],
                    title=raw["title"],
                    content_summary=raw["content_summary"],
                    author=raw.get("author"),
                    timestamp=raw["timestamp"],
                    trust_score=trust_score,
                    confidence=75, # Mock heuristic
                    freshness=freshness,
                    relevance_score=85, # Mock heuristic
                    verification=VerificationStatus(
                        is_verified=is_verified,
                        verified_by=["NEOVERSE_EVIDENCE_ENGINE"],
                        contradictions_found=len(conflicts) > 0
                    ),
                    bias_report=bias,
                    citation_metadata=raw.get("citation_metadata", {})
                )
                processed_items.append(item)
                
            # Filter to trusted evidence
            trusted = [item for item in processed_items if item.verification.is_verified]
            
            if trusted or attempt == max_retries - 1:
                final_evidence = trusted
                break
                
            cloud_logger.warning(f"Attempt {attempt + 1}: Insufficient trusted evidence. Retrying...")
            
        # Build Graph
        nodes, edges = self.graph_builder.build_graph(final_evidence, context)
        
        trace = ResearchTrace(
            evidence_collected=final_evidence,
            conflict_reports=conflict_reports,
            graph_nodes=nodes,
            graph_edges=edges,
            explanation={"summary": f"Found {len(final_evidence)} verified items."},
            minimum_trust_threshold_used=minimum_trust,
            is_sufficient=len(final_evidence) > 0
        )
        
        return trace.model_dump()
