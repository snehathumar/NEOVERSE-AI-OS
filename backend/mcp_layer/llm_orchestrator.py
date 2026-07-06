import os
import time
from google import genai
from google.genai import types
from backend.mcp_layer.health_monitor import health_monitor

class DynamicLLMOrchestrator:
    """
    Dynamically discovers, ranks, and falls back across available Gemini models.
    Never crashes on a single model failure.
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
                # Filter for content generation models (excluding embedding/vision-only if needed)
                if "generateContent" in m.supported_actions and "vision" not in m.name.lower():
                    # Rank logic: Prefer Pro over Flash over others
                    rank = 3
                    if "pro" in m.name:
                        rank = 1
                    elif "flash" in m.name:
                        rank = 2
                    valid_models.append({"name": m.name, "rank": rank})
            
            # Sort by rank
            valid_models.sort(key=lambda x: x["rank"])
            self._available_models = [m["name"] for m in valid_models]
            self._last_discovery = time.time()
            print(f"✅ [Orchestrator] Discovered {len(self._available_models)} models. Top pick: {self._available_models[0] if self._available_models else 'None'}")
        except Exception as e:
            print(f"⚠️ [Orchestrator] Failed to discover models: {e}")
            # Fallback hardcoded if discovery fails completely
            self._available_models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-pro-exp-02-05", "gemini-2.0-flash"]

    def generate_content(self, prompt: str, schema: dict = None) -> str:
        self._discover_models()
        
        if not self.client:
            return '{"error": "API Key missing"}'
            
        for model_name in self._available_models:
            # Check Health
            if not health_monitor.is_healthy(model_name):
                print(f"⏳ [Orchestrator] Skipping {model_name} (Cooldown active).")
                continue
                
            config = None
            if schema:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2
                )
            
            start_time = time.time()
            try:
                # print(f"🧠 [Orchestrator] Routing request to {model_name}...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                latency = int((time.time() - start_time) * 1000)
                health_monitor.record_success(model_name, latency)
                return response.text
                
            except Exception as e:
                print(f"❌ [Orchestrator] Model {model_name} failed: {e}")
                health_monitor.record_failure(model_name, cooldown_seconds=120)
                # Loop continues to the next model!
                
        # If all models fail
        return '{"error": "All available models failed or are in cooldown."}'

llm_orchestrator = DynamicLLMOrchestrator()
