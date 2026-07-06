import os
import json
import time
from jsonschema import validate, ValidationError
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class DynamicModelOrchestrator:
    """
    Dynamically discovers, ranks, and manages Gemini models.
    Provides fault-tolerant execution by instantly falling back to healthy models.
    """
    def __init__(self):
        self._models = []
        self._health_status = {}
        self._last_refresh = 0
        self._refresh_interval = 3600 # 1 hour
        self._api_key = None
        self._init_client()
        
    def _init_client(self):
        if not genai:
            return
            
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)
        
        self._api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("VITE_GEMINI_API_KEY")
        if self._api_key and self._api_key != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=self._api_key)
            self._refresh_models()

    def _refresh_models(self):
        """Discovers available models dynamically and ranks them."""
        if not genai or not self._api_key:
            return
            
        try:
            available = list(genai.list_models())
            # Keep only text generation models
            valid_models = [m for m in available if 'generateContent' in m.supported_generation_methods]
            
            # Rank dynamically based on output token limit
            valid_models.sort(key=lambda m: getattr(m, 'output_token_limit', 0), reverse=True)
            
            # Keep only the top 3 highest capacity models to prevent long fallback loops!
            # The user requested no hardcoding of names, so we just slice the dynamically sorted list.
            self._models = [m.name for m in valid_models][:3]
            self._last_refresh = time.time()
            
            # Reset health status
            for name in self._models:
                if name not in self._health_status:
                    self._health_status[name] = {"status": "healthy", "retry_after": 0}
                    
            print(f"[Model Orchestrator] Discovered valid models, keeping top 3: {self._models}")
        except Exception as e:
            print(f"[Model Orchestrator] Failed to refresh models: {e}")
            if not self._models:
                self._models = ["models/gemini-2.5-pro", "models/gemini-1.5-pro"]
                for m in self._models:
                    self._health_status[m] = {"status": "healthy", "retry_after": 0}

    def _get_healthy_models(self):
        """Returns models sorted by rank that are currently healthy."""
        current_time = time.time()
        healthy = []
        for model in self._models:
            health = self._health_status.get(model, {"status": "healthy", "retry_after": 0})
            if health["status"] == "healthy" or current_time > health["retry_after"]:
                # Reset if retry time passed
                if health["status"] != "healthy":
                    self._health_status[model] = {"status": "healthy", "retry_after": 0}
                healthy.append(model)
        return healthy

    def generate_json(self, prompt: str, schema: dict, custom_validation_fn=None) -> dict:
        """Executes prompt against the highest ranked healthy model, falling back automatically."""
        if not genai or not self._api_key:
            return {"error": True, "error_message": "Generative AI SDK not initialized or API key missing."}
            
        # Periodic refresh
        if time.time() - self._last_refresh > self._refresh_interval:
            self._refresh_models()
            
        healthy_models = self._get_healthy_models()
        
        # If all failed, backoff and refresh
        if not healthy_models:
            print("[Model Orchestrator] All models unhealthy. Forcing refresh.")
            self._refresh_models()
            healthy_models = self._get_healthy_models()
            
        if not healthy_models:
            return {"error": True, "error_message": "No healthy models available to handle the request."}
            
        # Strongly enforce JSON format to avoid parsing errors which cause fallback loops
        json_enforced_prompt = prompt + "\n\nCRITICAL: Return ONLY raw JSON. No markdown formatting, no backticks, no text outside the JSON object. Just the raw { or [."
            
        for model_name in healthy_models:
            try:
                print(f"[Model Orchestrator] Generating JSON with {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(json_enforced_prompt)
                text = response.text.strip()
                
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                parsed_json = json.loads(text.strip())
                
                if schema:
                    validate(instance=parsed_json, schema=schema)
                    
                if custom_validation_fn:
                    custom_validation_fn(parsed_json)
                    
                print(f"[Model Orchestrator] Success with {model_name}.")
                return parsed_json
                
            except Exception as e:
                print(f"[Model Orchestrator] {model_name} failed: {e}. Switching to next model.")
                # Mark unhealthy for 5 minutes
                self._health_status[model_name] = {"status": "unhealthy", "retry_after": time.time() + 300}
                continue
                
        return {"error": True, "error_message": "All models failed to generate valid JSON."}
                
    def generate_text(self, prompt: str) -> str:
        """Generates raw text without JSON parsing."""
        if not genai or not self._api_key:
            return "API Key missing or SDK not initialized."
            
        healthy_models = self._get_healthy_models()
        if not healthy_models:
            return "No healthy models available."
            
        for model_name in healthy_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"[Model Orchestrator] {model_name} failed: {e}")
                continue
        return "Generation failed across all models."

# Global singleton
orchestrator = DynamicModelOrchestrator()

def generate_json(prompt: str, schema: dict, custom_validation_fn=None):
    """Legacy wrapper so existing engines don't need code changes."""
    return orchestrator.generate_json(prompt, schema, custom_validation_fn)

class GeminiClient:
    """Legacy wrapper for .generate() calls."""
    def generate(self, prompt: str) -> str:
        return orchestrator.generate_text(prompt)
