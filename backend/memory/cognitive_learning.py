from typing import Optional
from backend.memory.models import DecisionMemory, LearningMemory
from backend.llm_client import GeminiClient
from backend.platform.cloud.logging_provider import cloud_logger
import json

class CognitiveLearningEngine:
    """
    Evaluates completed decisions to extract lessons learned, predictions, 
    and confidence calibrations for the Learning Memory store.
    """
    def __init__(self, memory_manager):
        self.manager = memory_manager
        self.llm = GeminiClient()
        
    def evaluate_decision(self, decision: DecisionMemory) -> Optional[LearningMemory]:
        """
        Runs post-mortem on a completed decision to extract cognitive learnings.
        """
        if decision.decision_status != "completed":
            return None
            
        cloud_logger.info(f"Extracting cognitive learning from decision {decision.id}")
        
        prompt = f"""
        Analyze this AI decision and extract cognitive learnings for future reference.
        
        BUSINESS CONTEXT: {decision.business_context}
        QUESTION: {decision.original_question}
        RECOMMENDATION: {decision.recommendation}
        OUTCOME: {decision.final_outcome or 'Unknown'}
        
        Provide JSON output:
        {{
            "lessons_learned": ["..."],
            "prediction_errors": ["..."],
            "successful_strategies": ["..."],
            "failed_strategies": ["..."],
            "confidence_adjustment": 5, // -100 to 100 based on outcome match
            "self_corrections": ["..."]
        }}
        """
        
        try:
            res_text = self.llm.generate(prompt)
            import re
            json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
            
            if json_match:
                data = json.loads(json_match.group(0))
                
                learning = LearningMemory(
                    user_id=decision.user_id,
                    business_id=decision.business_id,
                    related_memory_ids=[decision.id],
                    derived_from=[decision.id],
                    lessons_learned=data.get("lessons_learned", []),
                    prediction_errors=data.get("prediction_errors", []),
                    successful_strategies=data.get("successful_strategies", []),
                    failed_strategies=data.get("failed_strategies", []),
                    self_corrections=data.get("self_corrections", []),
                    confidence_changes={"adjustment": data.get("confidence_adjustment", 0)}
                )
                
                saved_learning = self.manager.remember(learning)
                
                # Push analytics
                try:
                    from backend.analytics.memory_analytics import memory_analytics
                    is_success = "success" in str(decision.final_outcome).lower()
                    memory_analytics.record_learning_effectiveness(
                        decision.user_id, decision.id, data.get("confidence_adjustment", 0), is_success
                    )
                except Exception:
                    pass
                    
                return saved_learning
                
        except Exception as e:
            cloud_logger.error(f"Failed to generate cognitive learning for {decision.id}: {e}")
            
        return None
