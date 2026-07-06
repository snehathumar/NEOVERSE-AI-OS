import json
import threading
from backend.llm_client import generate_json

class DebateAgentBase:
    """
    Base class for an independent Debate Agent.
    """
    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description

    def analyze(self, decision_context: str) -> dict:
        """
        Independently analyzes the decision context based on the agent's specific role.
        """
        schema = {
            "type": "object",
            "properties": {
                "stance": {"type": "string", "enum": ["Support", "Oppose", "Neutral"]},
                "arguments": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Arguments supporting your stance."
                },
                "counter_arguments": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Counter arguments anticipating opposing views."
                }
            },
            "required": ["stance", "arguments", "counter_arguments"]
        }
        
        prompt = f"""
You are the {self.name}. Your role is: {self.role_description}.
Independently evaluate the following business decision.
You MUST disagree and generate brutal counter arguments if the decision violates the core principles of your role.
Do not agree just to be polite. Provide your honest analysis.

Decision Context:
"{decision_context}"

Generate your stance, arguments, and counter arguments.
Return strictly JSON matching the schema.
"""
        try:
            return generate_json(prompt, schema)
        except Exception as e:
            return {"stance": "Neutral", "arguments": [f"Failed to generate analysis: {e}"], "counter_arguments": []}


class CEOAgent(DebateAgentBase):
    def __init__(self):
        super().__init__("CEO", "Focuses on vision, overall strategy, leadership, and balancing all departmental inputs.")

class FinanceExpert(DebateAgentBase):
    def __init__(self):
        super().__init__("Finance Expert", "Focuses strictly on cash flow, ROI, margins, profitability, and financial risk.")

class MarketingExpert(DebateAgentBase):
    def __init__(self):
        super().__init__("Marketing Expert", "Focuses on brand perception, customer acquisition, market positioning, and growth.")

class RiskAnalyst(DebateAgentBase):
    def __init__(self):
        super().__init__("Risk Analyst", "Focuses on identifying hidden vulnerabilities, regulatory compliance, and worst-case scenarios.")

class CustomerExpert(DebateAgentBase):
    def __init__(self):
        super().__init__("Customer Expert", "Focuses entirely on customer satisfaction, retention, ethical treatment, and user experience.")

class OperationsExpert(DebateAgentBase):
    def __init__(self):
        super().__init__("Operations Expert", "Focuses on execution feasibility, supply chain, scaling, and daily logistics.")


class ModeratorAgent:
    """
    Synthesizes the independent analyses of all registered debate agents into a final verdict.
    """
    def summarize_debate(self, decision_context: str, agent_responses: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "consensus": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Points where multiple experts agreed."
                },
                "major_disagreements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Major points of conflict between specific experts."
                },
                "final_verdict": {
                    "type": "string",
                    "description": "The final moderated recommendation after weighing all opinions."
                },
                "confidence": {
                    "type": "integer",
                    "description": "Overall confidence (0-100) in the final verdict."
                }
            },
            "required": ["consensus", "major_disagreements", "final_verdict", "confidence"]
        }
        
        prompt = f"""
You are the Moderator Agent.
Your job is to synthesize the following independent expert opinions on a business decision.
Analyze their arguments and counter arguments. Do not just copy them.

Business Decision:
"{decision_context}"

Expert Opinions:
{json.dumps(agent_responses, indent=2)}

Generate a final summary including:
1. Consensus
2. Disagreements
3. Final Verdict
4. Confidence Score

Return strictly JSON matching the schema.
"""
        return generate_json(prompt, schema)


class DebateSystem:
    """
    Orchestrates the Multi-Agent Debate.
    """
    def __init__(self):
        self.agents = []
        self.moderator = ModeratorAgent()

    def register_agent(self, agent: DebateAgentBase):
        self.agents.append(agent)

    def run_debate(self, decision_context: str) -> dict:
        agent_responses = {}
        
        # Run independent agents sequentially to avoid Free Tier Rate Limits (15 RPM)
        # which causes the SDK to hang in automatic retries.
        for agent in self.agents:
            try:
                result = agent.analyze(decision_context)
                agent_responses[agent.name] = result
            except Exception as e:
                agent_responses[agent.name] = {"stance": "Neutral", "arguments": [f"Error: {e}"], "counter_arguments": []}

        # Moderator synthesizes the final verdict
        try:
            moderation_result = self.moderator.summarize_debate(decision_context, agent_responses)
        except Exception as e:
            moderation_result = {"consensus": "Failed", "disagreements": [str(e)], "final_verdict": "Pipeline Error", "confidence_score": 0}
        
        return {
            "individual_analyses": agent_responses,
            "moderation": moderation_result
        }

# Default Initialization with the required agents
debate_system = DebateSystem()
debate_system.register_agent(CEOAgent())
debate_system.register_agent(FinanceExpert())
debate_system.register_agent(MarketingExpert())
debate_system.register_agent(RiskAnalyst())
debate_system.register_agent(CustomerExpert())
debate_system.register_agent(OperationsExpert())
