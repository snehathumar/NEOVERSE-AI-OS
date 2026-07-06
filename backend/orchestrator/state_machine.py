from typing import Optional
from enum import Enum
from datetime import datetime, timezone
from backend.memory.manager import MemoryManager
from backend.memory.models import AgentStateMemory

class ConversationState(Enum):
    GREETING = "Greeting"
    INFORMATION_GATHERING = "Information Gathering"
    CLARIFICATION = "Clarification"
    DECISION_ANALYSIS = "Decision Analysis"
    RECOMMENDATION = "Recommendation"
    FOLLOW_UP = "Follow-up"
    REPORT_GENERATION = "Report Generation"
    SESSION_RESUME = "Session Resume"

class ConversationStateMachine:
    """
    Manages the multi-turn conversational context for the Enterprise AI Router.
    Replaces the simple 'Interview Mode' with a robust state tracking system using AgentStateMemory.
    """
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        
    def get_or_create_state(self, session_id: str, current_task: str) -> AgentStateMemory:
        """Retrieves active state or creates a new one for the workflow."""
        state = self.memory.get_agent_state(current_task)
        if state and state.session_id == session_id:
            # Check if this session is old (e.g. > 1 hr)
            pass
        else:
            state = AgentStateMemory(
                session_id=session_id,
                current_task=current_task,
                tags=["conversation_state"],
                planner_state={"current_phase": ConversationState.GREETING.value}
            )
            self.memory.remember(state)
        return state
        
    def transition_state(self, state: AgentStateMemory, next_phase: ConversationState, reason: str = ""):
        """Transitions the conversation to a new phase and logs the evolution."""
        old_phase = state.planner_state.get("current_phase")
        state.planner_state["current_phase"] = next_phase.value
        state.audit_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "state_transition",
            "from": old_phase,
            "to": next_phase.value,
            "reason": reason
        })
        # Save updated state
        self.memory.remember(state)
        
    def add_missing_fields(self, state: AgentStateMemory, fields: list):
        """During Information Gathering, tracking exactly what is missing."""
        state.simulation_state["missing_fields"] = fields
        self.memory.remember(state)
