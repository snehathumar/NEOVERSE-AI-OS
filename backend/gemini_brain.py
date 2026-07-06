import json
import os
from jsonschema import validate, ValidationError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

# Try to import google-generativeai, but don't fail immediately if not installed
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Define the strictly expected JSON schema
GEMINI_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "universes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price_strategy": {"type": "string"},
                    "revenue_impact": {"type": "string"},
                    "risk_level": {"type": "string"},
                    "customer_change": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["name", "price_strategy", "revenue_impact", "risk_level", "customer_change", "reason"]
            },
            "minItems": 3,
            "maxItems": 3
        },
        "recommendation": {
            "type": "object",
            "properties": {
                "best_universe": {"type": "string"},
                "confidence": {"type": "string"},
                "reason": {"type": "string"}
            },
            "required": ["best_universe", "confidence", "reason"]
        }
    },
    "required": ["universes", "recommendation"]
}

def get_fallback_structure(error_message):
    """Returns a safe default structure with an error flag."""
    return {
        "error": True,
        "error_message": error_message,
        "universes": [
            {
                "name": "Conservative",
                "price_strategy": "N/A",
                "revenue_impact": "N/A",
                "risk_level": "N/A",
                "customer_change": "N/A",
                "reason": "Fallback default due to parsing/API error"
            },
            {
                "name": "Balanced",
                "price_strategy": "N/A",
                "revenue_impact": "N/A",
                "risk_level": "N/A",
                "customer_change": "N/A",
                "reason": "Fallback default due to parsing/API error"
            },
            {
                "name": "Aggressive",
                "price_strategy": "N/A",
                "revenue_impact": "N/A",
                "risk_level": "N/A",
                "customer_change": "N/A",
                "reason": "Fallback default due to parsing/API error"
            }
        ],
        "recommendation": {
            "best_universe": "N/A",
            "confidence": "LOW",
            "reason": "Failed to parse AI response or API error. Manual review required."
        }
    }

def call_gemini_brain(question, universes_summary):
    """
    Calls the Gemini API with the Universe summaries and the user's question,
    enforcing a strict JSON response. Retries once on validation failure.
    """
    if not genai:
        return get_fallback_structure("google-generativeai package is not installed.")

    if "GEMINI_API_KEY" not in os.environ and "VITE_GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY_HERE"

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("VITE_GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return get_fallback_structure("GEMINI_API_KEY environment variable not set. Please check your .env file.")
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
You are the NEOVERSE AI Decision Engine. The user has asked the following decision question:
"{question}"

Here are the 3 simulated Universe summaries based on different scenarios:
{json.dumps(universes_summary, indent=2)}

Analyze these summaries and provide a structured JSON response evaluating the strategies.
Your response MUST strictly conform to the following JSON structure:

{{
  "universes": [
    {{"name": "...", "price_strategy": "...", "revenue_impact": "...", "risk_level": "...", "customer_change": "...", "reason": "..."}},
    {{"name": "...", "price_strategy": "...", "revenue_impact": "...", "risk_level": "...", "customer_change": "...", "reason": "..."}},
    {{"name": "...", "price_strategy": "...", "revenue_impact": "...", "risk_level": "...", "customer_change": "...", "reason": "..."}}
  ],
  "recommendation": {{"best_universe": "...", "confidence": "...", "reason": "..."}}
}}

CRITICAL INSTRUCTIONS:
- Ensure the 'confidence' field in 'recommendation' is expressed ONLY as a percentage (e.g. '85%') or as HIGH/MEDIUM/LOW. NEVER use absolute claims like '100% certain' or '100%'.
- Ensure there are exactly 3 universes matching the input summaries.
"""

    last_error = None
    
    # Dynamically fetch available models that support text generation
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        available_models = ["models/gemini-1.5-pro", "models/gemini-1.5-flash", "models/gemini-pro"]

    # Try every available model until one succeeds
    for model_name in available_models:
        print(f"Trying model: {model_name}...")
        try:
            # Not using response_mime_type to ensure compatibility with all model versions
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Cleanup in case the model wraps the output in markdown
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            parsed_json = json.loads(text.strip())
            
            # JSON Schema Validation
            validate(instance=parsed_json, schema=GEMINI_OUTPUT_SCHEMA)
            
            # Custom constraint check for confidence
            confidence = str(parsed_json.get("recommendation", {}).get("confidence", "")).upper()
            if "100%" in confidence or "CERTAIN" in confidence:
                raise ValueError("Invalid confidence level generated (absolute certainty is forbidden).")
                
            print(f"Successfully generated response using {model_name}.")
            return parsed_json
            
        except Exception as e:
            print(f"[Warning] Model {model_name} failed: {e}")
            last_error = str(e)
            continue
            
    # If we exhaust all models, return safe default structure
    print("[Error] All Gemini models failed. Falling back to default.")
    return get_fallback_structure(f"All models failed. Last error: {last_error}")


if __name__ == "__main__":
    # Example usage for testing the fallback locally
    dummy_question = "Should we increase the price for the weekend promotion?"
    dummy_summaries = [
        {"universe": "Conservative", "projected_revenue_change": 30, "risk_level": 0},
        {"universe": "Balanced", "projected_revenue_change": 10, "risk_level": 5},
        {"universe": "Aggressive", "projected_revenue_change": -100, "risk_level": 50}
    ]
    
    print("Testing gemini_brain module (ensure GEMINI_API_KEY is set in environment to test actual API call)...")
    res = call_gemini_brain(dummy_question, dummy_summaries)
    print(json.dumps(res, indent=2))
