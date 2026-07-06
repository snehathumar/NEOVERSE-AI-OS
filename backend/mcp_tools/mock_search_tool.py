from backend.mcp_tool_base import McpToolBase

class MockSearchTool(McpToolBase):
    @property
    def name(self) -> str:
        return "mock_market_search"

    @property
    def description(self) -> str:
        return "Mocks searching the web for real-time market data."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }

    @property
    def output_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["results"]
        }

    def execute(self, inputs: dict) -> dict:
        # Architecture is built, no real APIs are called.
        query = inputs.get("query", "Unknown query")
        return {
            "results": [
                f"Mock API Data for: {query}",
                "Growth expected to be 15% YoY.",
                "Competitor pricing dropped by 5%."
            ]
        }
