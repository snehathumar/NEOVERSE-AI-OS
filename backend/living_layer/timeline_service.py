from backend.repositories.decision_repo import DecisionRepository

repo = DecisionRepository()

class TimelineService:
    """
    Builds the visual history timeline for any decision, extracting key events.
    """
    def generate_timeline(self, decision_id: str) -> list[dict]:
        history = repo.query() # In a real scenario, filter by decision_id
        if not history:
            return []

        timeline = []
        for i, record in enumerate(history):
            version = record.get("version", 1)
            timestamp = record.get("created_at") or record.get("timestamp")
            
            # Initial Creation
            if i == 0:
                timeline.append({
                    "event": "Decision Created",
                    "timestamp": timestamp,
                    "version": version,
                    "details": record.get("prompt")
                })
            else:
                # Changes and updates
                timeline.append({
                    "event": "Decision Updated",
                    "timestamp": timestamp,
                    "version": version,
                    "details": record.get("recommendation")
                })

        return timeline

timeline_service = TimelineService()
