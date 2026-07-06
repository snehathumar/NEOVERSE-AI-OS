from enum import Enum
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    GREETING = "Greeting"
    CONVERSATION = "Conversation"
    LEARNING = "Learning"
    BRAINSTORMING = "Brainstorming"
    PLANNING = "Planning"
    RESEARCH = "Research"
    DECISION = "Decision"
    MONITORING = "Monitoring"
    ANALYTICS = "Analytics"
    EMERGENCY = "Emergency"

class IntentClassification(BaseModel):
    intent: IntentType = Field(description="The classified intent of the user's input.")
    confidence: float = Field(description="Confidence score of the classification (0.0 to 1.0).")
    explanation: str = Field(description="Brief explanation of why this intent was chosen.")
