from backend.llm_client import generate_json
import json

LESSONS_SCHEMA = {
    "type": "object",
    "properties": {
        "lessons_learned": {
            "type": "string",
            "description": "What the AI learned from comparing the prediction to the actual result."
        }
    },
    "required": ["lessons_learned"]
}

SIMILARITY_SCHEMA = {
    "type": "object",
    "properties": {
        "is_similar": {"type": "boolean"},
        "relevant_lesson": {"type": "string"},
        "confidence_boost": {"type": "integer"}
    },
    "required": ["is_similar", "relevant_lesson", "confidence_boost"]
}

class LearningEngine:
    def __init__(self):
        # In a real app, this would be a database table
        self.decision_memory = []

    def log_decision(self, decision: str, prediction: str, confidence: int):
        record = {
            "Decision": decision,
            "Prediction": prediction,
            "Actual Result": None,
            "Prediction Error": None,
            "Confidence": confidence,
            "Lessons Learned": None
        }
        self.decision_memory.append(record)
        return record

    def log_actual_result(self, decision_index: int, actual_result: str, prediction_error: str):
        if decision_index < len(self.decision_memory):
            record = self.decision_memory[decision_index]
            record["Actual Result"] = actual_result
            record["Prediction Error"] = prediction_error
            
            prompt = f"""
Decision: {record['Decision']}
AI Predicted: {record['Prediction']}
Actual Result was: {actual_result}
Error/Delta: {prediction_error}

Analyze what went wrong or right. Extract the core business lesson learned.
"""
            res = generate_json(prompt, LESSONS_SCHEMA)
            record["Lessons Learned"] = res.get("lessons_learned", "No clear lesson.")
            return record
        return None

    def reference_previous_experience(self, new_situation: str):
        if not self.decision_memory:
            return {"is_similar": False, "relevant_lesson": "", "confidence_boost": 0}
            
        completed_lessons = [r for r in self.decision_memory if r.get("Lessons Learned")]
        if not completed_lessons:
            return {"is_similar": False, "relevant_lesson": "", "confidence_boost": 0}
            
        prompt = f"""
New Situation: "{new_situation}"

Previous Experiences (Lessons Learned):
{json.dumps(completed_lessons, indent=2)}

Are any of the previous experiences highly similar to this new situation?
If yes, extract the relevant lesson and determine a confidence boost (e.g., +5 to +15) because the AI has learned from past data.
"""
        return generate_json(prompt, SIMILARITY_SCHEMA)

# Initialize a global instance for the session
learning_engine = LearningEngine()
