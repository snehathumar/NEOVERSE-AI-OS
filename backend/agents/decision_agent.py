import json
from backend.agents.base_agent import BaseAgent
from backend.repositories.memory_repo import ConversationMemoryRepository
from backend.repositories.decision_repo import DecisionRepository

class DecisionAgent(BaseAgent):
    agent_name = "DecisionAgent"
    system_prompt = """
    You are NEOVERSE Master AI, the Enterprise Decision Intelligence Platform. 
    Your objective is to help the user make complex business decisions.
    
    CRITICAL RULES:
    1. If the user input is a casual greeting (like "hi", "hello", "hey"), politely introduce yourself, explain briefly that you are here to assist with business decisions, and ask how you can help them today. Do NOT immediately ask for business facts in this case.
    2. If the user is stating a problem or asking for a decision, your goal is to gather facts. If you lack business facts (e.g., current price, scale/volume, competitors/market), ask ONE precise question at a time to build context.
    3. If you have gathered sufficient facts to run a decision simulation, output exactly [START_SIMULATION] and nothing else.
    """

    def __init__(self, ui_callback=None):
        super().__init__(ui_callback=ui_callback)
        self.conv_repo = ConversationMemoryRepository()
        self.decision_repo = DecisionRepository()

    def handle(self, user_input: str, session_id: str, current_facts: list) -> str:
        self._log_event("START_ROUTING", f"Processing user decision request: {user_input}")
        
        # 1. Fetch conversation history
        history = self.conv_repo.get_history(session_id)
        
        # 2. Formulate prompt
        prompt = f"User input: {user_input}\nCurrent known facts: {current_facts}\nRespond appropriately."
        
        # 3. Call LLM
        response = self._call_llm(prompt, history)
        
        if "[START_SIMULATION]" in response:
            self._log_event("SIMULATION_TRIGGERED", "All facts gathered. Triggering decision simulation.")
            # Note: The actual simulation and debate orchestration would be called here or by the Master Router.
            
        return response
