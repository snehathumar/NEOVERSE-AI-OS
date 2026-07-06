from backend.llm_client import generate_json

QUESTION_ENGINE_SCHEMA = {
    "type": "object",
    "properties": {
        "missing_parameters": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Parameters that are still unknown."
        },
        "all_gathered": {
            "type": "boolean",
            "description": "True if we have enough information to run a simulation."
        },
        "follow_up_question": {
            "type": "string",
            "description": "If all_gathered is false, a natural conversational question asking the user for the missing parameters."
        },
        "extracted_data": {
            "type": "object",
            "description": "Key-value pairs of parameters that have been successfully identified so far."
        }
    },
    "required": ["missing_parameters", "all_gathered", "follow_up_question", "extracted_data"]
}

def analyze_missing_info(decision: str, required_parameters: list, conversation_history: list):
    history_str = "Conversation History:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    prompt = f"""
We are simulating the following business decision: "{decision}"
The required parameters for this domain are: {required_parameters}

{history_str}

Analyze the conversation history. Have we extracted enough of these parameters to run a simulation?
If not, identify what is missing and generate a natural follow-up question to ask the user.
Extract any parameters the user has already provided.
"""
    return generate_json(prompt, QUESTION_ENGINE_SCHEMA)
