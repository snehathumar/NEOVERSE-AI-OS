import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone

from backend.evolution.models import (
    LearningEvent, StrategyPattern, AIHealthIndex, EvolutionReport
)
from backend.evolution.evaluators import EvolutionEvaluator
from backend.evolution.strategy_extractor import StrategyExtractor
from backend.memory.manager import MemoryManager, StorageManager
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger

class SelfEvolutionEngine:
    """
    Core engine for Phase 11: Enterprise Self-Evolution & Continuous Learning.
    Executes entirely in the background.
    """
    def __init__(self):
        self.evaluator = EvolutionEvaluator()
        self.strategy_extractor = StrategyExtractor()
        self.memory_manager = MemoryManager()
        self.storage_manager = StorageManager()
        self.bq = BigQueryProvider()

    async def execute_evolution(self, context: dict, outcome_feedback: str = "Unknown Outcome") -> Dict[str, Any]:
        """
        Runs asynchronously after the Report is generated.
        `outcome_feedback` can be provided later via the Feedback API.
        """
        decision_id = context.get("upstream_results", {}).get("DecisionModule", {}).get("decision_id", "unknown")
        cloud_logger.info(f"Starting Self-Evolution Loop for Decision {decision_id}")
        
        # Extract context
        decision_context = context.get("upstream_results", {}).get("DecisionModule", {})
        evidence_context = context.get("upstream_results", {}).get("EvidenceModule", {})
        
        # 1. Evaluate Decision Quality
        actual_success = self.evaluator.evaluate_decision_quality(decision_context, outcome_feedback)
        
        # 2. Calibrate Confidence
        predicted_conf = decision_context.get("confidence", 50.0)
        calibration = self.evaluator.calibrate_confidence(predicted_conf, actual_success)
        
        # 3. Extract Strategies
        domain = decision_context.get("business_understanding", {}).get("decision_type", "General")
        strategies = self.strategy_extractor.extract_strategies(decision_context, outcome_feedback, domain)
        
        # 4. Save to StrategyLibrary (via MemoryManager)
        for strategy in strategies:
            # We assume a Memory category 'strategy' exists
            self.memory_manager.create_memory(
                user_id="NEOVERSE_SYSTEM",
                category="strategy",
                content=strategy.model_dump_json(),
                insight=f"Extracted strategy for {strategy.industry}",
                metadata={"strategy_id": strategy.strategy_id}
            )
            
        # 5. Build Learning Event for Audit
        learning_event = LearningEvent(
            learning_id=str(uuid.uuid4()),
            source_decision_id=decision_id,
            trigger="post_decision" if outcome_feedback == "Unknown Outcome" else "user_feedback",
            timestamp=datetime.now(timezone.utc).isoformat(),
            previous_state={"predicted_confidence": predicted_conf},
            new_state={"actual_success": actual_success, "calibration_trend": calibration.calibration_trend},
            reason=f"Outcome recorded: {outcome_feedback}",
            evidence_used=[e.get("id") for e in evidence_context.get("evidence_collected", [])],
            version=1
        )
        
        # 6. Stream Analytics
        self.bq.stream_analytics("learning_events", learning_event.model_dump())
        self.bq.stream_analytics("confidence_calibration", calibration.model_dump())
        
        cloud_logger.info(f"Self-Evolution complete for Decision {decision_id}")
        return {"status": "success", "learning_event": learning_event.model_dump()}
        
    async def process_delayed_feedback(self, decision_id: str, feedback: dict):
        """
        Entry point for the Feedback API. Re-runs the learning loop using actual outcomes.
        """
        cloud_logger.info(f"Processing delayed feedback for Decision {decision_id}: {feedback}")
        
        # In a real system, we'd fetch the historical decision context from StorageManager
        # and re-run execute_evolution with the new outcome_feedback.
        # For now, we mock the retrieval.
        mock_context = {
            "upstream_results": {
                "DecisionModule": {"decision_id": decision_id, "confidence": 80.0},
                "EvidenceModule": {"evidence_collected": []}
            }
        }
        
        await self.execute_evolution(mock_context, outcome_feedback=feedback.get("outcome", "Partial Success"))
