import os
import time
from google import genai
from google.genai import types
from backend.monitoring.model_monitor import model_monitor

class DynamicLLMOrchestrator:
    """
    Dynamically discovers, ranks, and falls back across available Gemini models.
    NEVER hardcodes a model. Uses only the Google AI Studio API Key.
    """
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self._available_models = []
        self._last_discovery = 0
        
    def _discover_models(self):
        """Fetches and filters models from Google AI Studio."""
        if not self.client:
            return
            
        # Discover every 1 hour maximum
        if time.time() - self._last_discovery < 3600 and self._available_models:
            return
            
        print("🔍 [Orchestrator] Discovering available Gemini models...")
        try:
            models = self.client.models.list()
            valid_models = []
            for m in models:
                # Filter for models supporting content generation
                if "generateContent" in m.supported_actions and "vision" not in m.name.lower():
                    # Rank logic: Prefer Pro > Flash > others
                    rank = 3
                    if "pro" in m.name:
                        rank = 1
                    elif "flash" in m.name:
                        rank = 2
                    valid_models.append({"name": m.name, "rank": rank})
            
            # Sort by rank ascending (1 is best)
            valid_models.sort(key=lambda x: x["rank"])
            self._available_models = [m["name"] for m in valid_models]
            self._last_discovery = time.time()
            print(f"✅ [Orchestrator] Discovered {len(self._available_models)} valid models.")
        except Exception as e:
            print(f"⚠️ [Orchestrator] Failed to discover models: {e}")
            # Failsafe in case the discovery API is unreachable, but we try to avoid hardcoding 
            self._available_models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"]

    def generate_content(self, prompt: str, schema: dict = None) -> str:
        self._discover_models()
        
        if not self.client:
            return '{"error": "API Key missing"}'
            
        for model_name in self._available_models:
            if not model_monitor.is_healthy(model_name):
                print(f"⏳ [Orchestrator] Skipping {model_name} (Cooldown active).")
                continue
                
            model_monitor.set_active_model(model_name)
            
            config = None
            if schema:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2
                )
            
            start_time = time.time()
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                latency = int((time.time() - start_time) * 1000)
                model_monitor.record_success(model_name, latency)
                return response.text
                
            except Exception as e:
                print(f"❌ [Orchestrator] Model {model_name} failed: {e}")
                model_monitor.record_failure(model_name, cooldown_seconds=120)
                # Loop continues to the next compatible model!
                
        # If all models fail
        return '{"error": "All available models failed or are in cooldown."}'

llm_orchestrator = DynamicLLMOrchestrator()

# Helper function to expose the same interface as before
def generate_json(prompt: str, schema: dict) -> dict:
    import json
    raw = llm_orchestrator.generate_content(prompt, schema)
    try:
        return json.loads(raw)
    except:
        return {}
