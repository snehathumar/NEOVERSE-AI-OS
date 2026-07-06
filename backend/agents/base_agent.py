import uuid
from typing import Dict, Any, List
from backend.platform.storage.factory import get_storage_manager
from backend.repositories.event_repo import EventRepository
import google.generativeai as genai

class BaseAgent:
    """
    Enterprise Base Agent for NEOVERSE AI OS.
    Every agent extends this and defines its own prompt, workflow, memory, and tools.
    """
    agent_name = "BaseAgent"
    system_prompt = "You are a helpful AI assistant."

    def __init__(self, ui_callback=None):
        self.storage = get_storage_manager()
        self.event_repo = EventRepository()
        self.agent_id = str(uuid.uuid4())
        self.ui_callback = ui_callback
        
    def _log_event(self, action: str, details: str):
        self.event_repo.log_event(
            event_type=f"AGENT_{self.agent_name.upper()}_{action.upper()}",
            message=details,
            metadata={"agent_id": self.agent_id}
        )
        if self.ui_callback:
            self.ui_callback(details)

    def _call_llm(self, prompt: str, history: List[Dict[str, str]] = None) -> str:
        self._log_event("CALLING_LLM", f"Prompting LLM with {len(prompt)} characters.")
        
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models.sort(key=lambda x: 0 if 'pro' in x else 1)
        
        if not models:
            raise Exception("No text models found.")
            
        model = genai.GenerativeModel(models[0], system_instruction=self.system_prompt)
        
        # Build prompt with history
        full_prompt = prompt
        if history:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            full_prompt = f"History:\n{history_text}\n\nTask:\n{prompt}"
            
        response = model.generate_content(full_prompt)
        self._log_event("LLM_RESPONDED", "Successfully received response from LLM.")
        return response.text.strip()

    def handle(self, user_input: str, session_id: str) -> str:
        """
        Main workflow entrypoint. Must be overridden by specific agents.
        """
        raise NotImplementedError("Each agent must implement handle()")
