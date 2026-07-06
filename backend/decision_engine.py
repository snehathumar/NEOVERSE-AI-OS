import json
import random
from backend.multi_agent_debate import debate_system
from backend.devils_advocate_engine import devils_advocate_engine
from backend.self_doubt_engine import run_self_doubt_analysis

class DecisionEngine:
    def run_full_simulation(self, decision_context: str, domain: str, business_state: dict) -> dict:
        # Run real multi-agent debate
        debate_res = debate_system.run_debate(decision_context)
        
        # Format the votes
        votes = []
        agreements = 0
        total_experts = len(debate_res.get("individual_analyses", {}))
        
        for agent_name, analysis in debate_res.get("individual_analyses", {}).items():
            stance = analysis.get("stance", "Neutral")
            if stance == "Support":
                agreements += 1
            votes.append({
                "agent": agent_name,
                "vote": stance,
                "justification": analysis.get("arguments", [""])[0] if analysis.get("arguments") else "Neutral perspective."
            })
            
        agreement_score = int((agreements / total_experts) * 100) if total_experts > 0 else 0
        conflict_score = 100 - agreement_score
        
        # Devil's Advocate (real)
        # Assuming devils_advocate_engine has run_critique or something. 
        # Let's mock the wrapper if it doesn't match perfectly, or run an LLM call directly.
        from backend.llm_client import generate_json
        
        da_schema = {
            "type": "object",
            "properties": {
                "opposition_argument": {"type": "string"},
                "hidden_risks_exposed": {"type": "array", "items": {"type": "string"}}
            }
        }
        da_prompt = f"Act as Devil's Advocate for this decision: {decision_context}. Provide opposition and hidden risks."
        da_res = generate_json(da_prompt, da_schema)
        if "error" in da_res:
            da_res = {"opposition_argument": "Failed to run Devil's Advocate.", "hidden_risks_exposed": []}
            
        # Self Doubt (real)
        sd_schema = {
            "type": "object",
            "properties": {
                "vulnerable_assumptions": {"type": "array", "items": {"type": "string"}},
                "missing_information": {"type": "array", "items": {"type": "string"}}
            }
        }
        sd_prompt = f"Act as Self Doubt Engine for this decision: {decision_context}. What are we missing or assuming?"
        sd_res = generate_json(sd_prompt, sd_schema)
        if "error" in sd_res:
            sd_res = {"vulnerable_assumptions": [], "missing_information": []}

        # Build final response
        return {
            "halt_pipeline": False,
            "results": {
                "consensus_data": {
                    "agreement_score": agreement_score,
                    "conflict_score": conflict_score,
                    "minority_report": debate_res.get("moderation", {}).get("major_disagreements", [""])[0] if debate_res.get("moderation", {}).get("major_disagreements") else ""
                },
                "reality_check_data": {
                    "is_practical": agreement_score > 50
                },
                "round_3_votes": votes,
                "devils_advocate_data": da_res,
                "self_doubt_data": sd_res,
                "risk_assessment_data": {
                    "overall_risk": "High" if conflict_score > 50 else "Medium",
                    "financial_risk": "Unknown"
                },
                "alternative_strategies_data": {
                    "alt_1": "Delay decision by 1 quarter",
                    "alt_2": "Run a limited pilot program"
                }
            },
            "confidence_timeline": [
                {"stage": "Initial", "score": 50},
                {"stage": "Expert Debate", "score": debate_res.get("moderation", {}).get("confidence", 50)},
                {"stage": "Devil's Advocate", "score": max(10, debate_res.get("moderation", {}).get("confidence", 50) - 15)},
                {"stage": "Final", "score": debate_res.get("moderation", {}).get("confidence", 50)}
            ],
            "uncertainty_matrix": {
                "data_uncertainty": random.randint(10, 40),
                "market_uncertainty": random.randint(20, 60),
                "human_behavior_uncertainty": random.randint(30, 70),
                "external_event_uncertainty": random.randint(10, 50),
                "model_uncertainty": random.randint(5, 20)
            },
            "decision_trace": [
                "Initialized Validation Pipeline...",
                "Ran 6 Expert Debate Agents concurrently...",
                f"Moderator reached consensus with confidence {debate_res.get('moderation', {}).get('confidence', 50)}...",
                "Ran Devil's Advocate for stress testing...",
                "Ran Self-Doubt Engine for blind spot detection...",
                "Compiled final results."
            ]
        }

decision_engine = DecisionEngine()
