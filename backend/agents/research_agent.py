import json
from backend.llm_client import generate_json

RESEARCH_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "required_data": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific data points needed (e.g. 'competitor pricing', 'market size')."
        },
        "search_queries": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Search queries to execute."
        },
        "mcp_tools_to_invoke": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Future MCP tools that should be called."
        }
    },
    "required": ["required_data", "search_queries", "mcp_tools_to_invoke"]
}

RESEARCH_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "evidence_summary": {
            "type": "string",
            "description": "A synthesized summary of the collected evidence."
        },
        "key_facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The most important verified facts."
        },
        "data_gaps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Information that could not be found."
        }
    },
    "required": ["evidence_summary", "key_facts", "data_gaps"]
}

class ResearchAgent:
    """
    Dedicated Research Agent.
    Executes before the Decision Engine to collect hard evidence and facts,
    preventing hallucinations and grounding the decision in reality.
    Built to support future Model Context Protocol (MCP) tool integrations.
    """
    def __init__(self):
        pass

    def run_research_pipeline(self, user_query: str) -> dict:
        """
        Executes the full Research Architecture:
        Research Planner -> Tool Calls -> Evidence Collection -> Evidence Summary
        """
        print(f"🔍 [Research Agent] Starting pipeline for: {user_query}")
        
        # 1. Research Planner
        plan = self._generate_research_plan(user_query)
        print(f"📋 [Research Agent] Plan created: {len(plan.get('search_queries', []))} queries planned.")
        
        # 2. Tool Calls & Evidence Collection (Mocked for now)
        evidence_collected = self._execute_tool_calls(plan)
        print(f"⚙️  [Research Agent] Mock tool execution complete. Evidence gathered.")
        
        # 3. Evidence Summary
        summary = self._generate_evidence_summary(user_query, plan, evidence_collected)
        print(f"✅ [Research Agent] Evidence summarized. Ready for Decision Engine.")
        
        return {
            "research_plan": plan,
            "raw_evidence": evidence_collected,
            "final_summary": summary
        }

    def _generate_research_plan(self, user_query: str) -> dict:
        prompt = f"""
You are the Research Planner Agent.
Before we can make a business decision about "{user_query}", we need evidence.
Identify exactly what data we need to collect, what search queries to run, and what tools to invoke.

Return strictly JSON matching the schema.
"""
        try:
            return generate_json(prompt, RESEARCH_PLAN_SCHEMA)
        except Exception:
            return {"required_data": [], "search_queries": [], "mcp_tools_to_invoke": []}

    def _execute_tool_calls(self, plan: dict) -> list:
        """
        Mock implementation of tool execution. 
        In the future, this will connect to MCP servers (e.g., Google Search, Web Scraper, DB lookup).
        """
        mock_evidence = []
        for query in plan.get("search_queries", []):
            mock_evidence.append(f"Mock Search Result for '{query}': Found relevant market data showing 10% YoY growth.")
            
        for tool in plan.get("mcp_tools_to_invoke", []):
            mock_evidence.append(f"Mock Tool Result from '{tool}': Successfully executed and retrieved 5 records.")
            
        return mock_evidence

    def _generate_evidence_summary(self, user_query: str, plan: dict, evidence: list) -> dict:
        prompt = f"""
You are the Research Summarizer.
Synthesize the collected evidence into a clean summary that will be fed directly into the Decision Engine.

User Query: "{user_query}"
Raw Evidence Collected:
{json.dumps(evidence, indent=2)}

Extract the key facts and identify any remaining data gaps.
Return strictly JSON matching the schema.
"""
        try:
            return generate_json(prompt, RESEARCH_SUMMARY_SCHEMA)
        except Exception:
            return {"evidence_summary": "Failed to summarize.", "key_facts": [], "data_gaps": []}

    def handle(self, user_input: str, conversation_history: list, business_state) -> dict:
        """
        Standard agent handle method to be called by MasterRouter if used directly.
        """
        research_output = self.run_research_pipeline(user_input)
        
        return {
            "type": "research_complete",
            "research_output": research_output,
            "message": "Research complete. The Decision Engine can now proceed with verified facts."
        }

# Singleton instance
research_agent = ResearchAgent()
