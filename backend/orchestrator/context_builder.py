from typing import Dict, Any
from backend.memory.manager import MemoryManager

class UnifiedContext:
    def __init__(self):
        self.user_input: str = ""
        self.session_id: str = ""
        self.conversation_history: list = []
        self.user_profile: dict = {}
        self.relevant_learnings: list = []
        self.knowledge: list = []
        self.business_state: dict = {}
        self.agent_state = None

class ContextBuilder:
    """
    Assembles the context before routing the request.
    Pulls from MemoryManager to construct the UnifiedContext.
    """
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        
    async def build(self, user_input: str, session_id: str) -> UnifiedContext:
        context = UnifiedContext()
        context.user_input = user_input
        context.session_id = session_id
        
        # 1. Fetch conversation history (session)
        # Using placeholder empty list if no session memory logic handles standard arrays
        session_mem = self.memory.get("session", session_id)
        if session_mem:
            context.conversation_history = session_mem.context_summary.get("messages", [])
            
        # 2. Fetch User Profile
        # For multi-tenant, user_profile is usually 1 per user
        profiles = self.memory.retrieve("user_profile")
        if profiles:
            context.user_profile = profiles[0].preferences
            
        # 3. Retrieve relevant learnings and knowledge semantically based on input
        context.relevant_learnings = self.memory.retrieve_semantic("learning", user_input, limit=2)
        context.knowledge = self.memory.retrieve_semantic("knowledge", user_input, limit=2)
        
        # 4. Fetch Agent State if exists
        context.agent_state = self.memory.get_agent_state(f"task_{session_id}")
        
        return context

    def to_dict(self, context: UnifiedContext) -> Dict[str, Any]:
        """Serializes context for module consumption"""
        return {
            "user_input": context.user_input,
            "session_id": context.session_id,
            "conversation_history": context.conversation_history,
            "user_profile": context.user_profile,
            "relevant_learnings": [l.model_dump() for l in context.relevant_learnings],
            "knowledge": [k.model_dump() for k in context.knowledge],
            "business_state": context.business_state,
            "agent_state": context.agent_state.model_dump() if context.agent_state else None
        }
