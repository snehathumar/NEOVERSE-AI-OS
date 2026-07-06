from backend.agents.base_agent import BaseAgent
from backend.repositories.memory_repo import ConversationMemoryRepository

class ChatAgent(BaseAgent):
    agent_name = "ChatAgent"
    system_prompt = "You are NEOVERSE AI OS, a friendly and highly intelligent strategic conversational agent."

    def __init__(self, ui_callback=None):
        super().__init__(ui_callback=ui_callback)
        self.conv_repo = ConversationMemoryRepository()

    def handle(self, user_input: str, session_id: str) -> str:
        self._log_event("CHAT_STARTED", f"Processing general chat: {user_input}")
        
        history = self.conv_repo.get_history(session_id)
        response = self._call_llm(user_input, history)
        
        self._log_event("CHAT_COMPLETED", "Responded to user.")
        return response
