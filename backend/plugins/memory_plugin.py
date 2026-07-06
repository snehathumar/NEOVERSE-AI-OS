import uuid
import json
from datetime import datetime, timezone
from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus

class DecisionMemorySystem(NeoversePlugin):
    """
    Decision Memory System.
    Stores every decision, prediction, confidence, and outcome.
    Calculates prediction accuracy and allows future decisions to learn from the past.
    """
    def initialize(self):
        # We use a local dictionary for hackathon/prototype purposes instead of Firestore here.
        # In production, this data resides in Firestore/BigQuery.
        self.memory_store = []
        
        event_bus.subscribe("DecisionCreated", self.store_decision)
        event_bus.subscribe("DecisionOutcomeResolved", self.store_outcome_and_calculate_accuracy)

    def store_decision(self, payload: dict):
        """
        Stores the initial decision, its predictions, and confidence.
        """
        record = {
            "memory_id": str(uuid.uuid4()),
            "decision_id": payload.get("decision_id"),
            "query": payload.get("decision_query"),
            "business_type": payload.get("business_type"),
            "prediction": payload.get("final_recommendation"),
            "confidence": payload.get("confidence_score"),
            "outcome": None,
            "accuracy_score": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.memory_store.append(record)
        print(f"🧠 [Memory System] Stored decision memory for: {payload.get('decision_query')[:20]}...")

    def store_outcome_and_calculate_accuracy(self, payload: dict):
        """
        Triggered when a decision's real-world outcome is known.
        Stores the outcome and mathematically calculates how accurate the original prediction was.
        """
        decision_id = payload.get("decision_id")
        actual_outcome = payload.get("actual_outcome") # e.g. "Revenue increased by 15%"
        outcome_success_score = payload.get("outcome_success_score", 0) # 0 to 100
        
        for record in self.memory_store:
            if record.get("decision_id") == decision_id:
                record["outcome"] = actual_outcome
                
                # Calculate accuracy: How close was the AI's confidence to the actual success?
                # If confidence was 90% and success was 100%, accuracy is high.
                # If confidence was 90% but success was 10%, accuracy is terrible.
                confidence = record.get("confidence", 50)
                accuracy_score = 100 - abs(confidence - outcome_success_score)
                record["accuracy_score"] = accuracy_score
                
                print(f"🧠 [Memory System] Outcome resolved. Prediction Accuracy: {accuracy_score}%")
                
                # Publish the learning event so other modules can adapt
                event_bus.publish("LearningUpdated", record)
                break

    def retrieve_relevant_past_knowledge(self, current_query: str, business_type: str) -> str:
        """
        Allows future decisions to use previous knowledge.
        Scans memory for past decisions in the same business domain that have a resolved outcome.
        Returns a formatted knowledge string to inject into the LLM context.
        """
        relevant_memories = [
            m for m in self.memory_store 
            if m.get("outcome") is not None and m.get("business_type") == business_type
        ]
        
        if not relevant_memories:
            return "No relevant past decision memory found for this business type."
            
        knowledge_blocks = []
        for m in relevant_memories:
            knowledge_blocks.append(
                f"- Past Query: {m['query']}\n"
                f"  Predicted: {m['prediction']} (Confidence: {m['confidence']}%)\n"
                f"  Actual Outcome: {m['outcome']}\n"
                f"  AI Prediction Accuracy: {m['accuracy_score']}%"
            )
            
        return "Past Knowledge & Accuracy:\n" + "\n".join(knowledge_blocks)

# Expose singleton for direct imports if needed
decision_memory_system = DecisionMemorySystem()
