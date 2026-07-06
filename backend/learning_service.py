from backend.cloud_config import cloud_config
import uuid
from datetime import datetime, timezone
import math

class LearningService:
    """
    Dedicated Learning Service to allow NEOVERSE AI to improve over time.
    Calculates prediction errors against actual outcomes and stores them in Firestore.
    Provides methods to retrieve historical learning data to adjust future recommendations.
    """
    def __init__(self):
        self._client = None

    @property
    def db(self):
        if self._client is None:
            self._client = cloud_config.get_firestore_client()
        return self._client

    def _calculate_prediction_error(self, predicted: float, actual: float) -> float:
        """
        Calculates the Mean Absolute Percentage Error (MAPE) or simple deviation.
        Returns the error percentage.
        """
        if actual == 0:
            return 0.0 # Prevent division by zero
        error = abs(predicted - actual) / abs(actual)
        return round(error * 100, 2)

    def _calculate_learning_score(self, error_percentage: float) -> int:
        """
        Converts a prediction error into a Learning Score (0 to 100).
        0 error = 100 Learning Score.
        """
        score = 100 - error_percentage
        return max(0, min(100, int(score)))

    # -------------------------------------------------------------------------
    # Reusable Learning Methods
    # -------------------------------------------------------------------------
    
    def log_prediction(self, user_id: str, decision_id: str, metric_name: str, predicted_value: float):
        """
        Logs an initial AI prediction. The actual outcome will be filled later.
        """
        prediction_id = str(uuid.uuid4())
        data = {
            "prediction_id": prediction_id,
            "user_id": user_id,
            "decision_id": decision_id,
            "metric_name": metric_name,
            "predicted_value": predicted_value,
            "actual_value": None,
            "prediction_error": None,
            "learning_score": None,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None
        }
        self.db.collection("learning_history").document(prediction_id).set(data)
        return prediction_id

    def resolve_prediction(self, prediction_id: str, actual_value: float):
        """
        Updates a pending prediction with the actual outcome, calculates the error,
        and computes the Learning Score.
        """
        doc_ref = self.db.collection("learning_history").document(prediction_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise ValueError(f"Prediction ID {prediction_id} not found.")
            
        data = doc.to_dict()
        predicted_value = data.get("predicted_value")
        
        error_percentage = self._calculate_prediction_error(predicted_value, actual_value)
        learning_score = self._calculate_learning_score(error_percentage)
        
        updates = {
            "actual_value": actual_value,
            "prediction_error": error_percentage,
            "learning_score": learning_score,
            "status": "resolved",
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }
        doc_ref.update(updates)
        return updates

    def get_historical_learning_context(self, user_id: str, metric_name: str, limit: int = 5) -> str:
        """
        Retrieves past prediction performance to feed into future AI recommendations.
        """
        docs = self.db.collection("learning_history") \
                      .where("user_id", "==", user_id) \
                      .where("metric_name", "==", metric_name) \
                      .where("status", "==", "resolved") \
                      .order_by("resolved_at", direction="DESCENDING") \
                      .limit(limit) \
                      .stream()
                      
        history = [doc.to_dict() for doc in docs]
        
        if not history:
            return f"No historical learning data available for {metric_name}."
            
        avg_error = sum(item["prediction_error"] for item in history) / len(history)
        avg_score = sum(item["learning_score"] for item in history) / len(history)
        
        context = (
            f"[LEARNING ENGINE METRICS FOR {metric_name.upper()}]\n"
            f"Past Predictions Evaluated: {len(history)}\n"
            f"Average AI Error Margin: {avg_error}%\n"
            f"Historical Accuracy Score: {int(avg_score)}/100\n"
            "ADJUSTMENT DIRECTIVE: If Error Margin > 15%, the AI MUST explicitly generate more conservative estimates in the current prediction."
        )
        return context

# Singleton instance
learning_service = LearningService()
