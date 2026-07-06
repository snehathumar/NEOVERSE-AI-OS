from backend.llm_client import generate_json

class LearningEngine:
    """
    Compares past predictions against actual outcomes.
    Calculates accuracy metrics and learning scores.
    """
    def calculate_learning_metrics(self, past_prediction: dict, actual_outcome: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "prediction_accuracy": {"type": "integer"},
                "learning_score": {"type": "integer"},
                "error_rate": {"type": "integer"}
            },
            "required": ["prediction_accuracy", "learning_score", "error_rate"]
        }
        prompt = f"""
Compare the AI's past prediction with the actual outcome that occurred.
Past Prediction: {past_prediction}
Actual Outcome: {actual_outcome}

Calculate the prediction accuracy (0-100), learning score (amount of new knowledge gained 0-100), and error rate (0-100).
"""
        return generate_json(prompt, schema)

learning_engine = LearningEngine()
