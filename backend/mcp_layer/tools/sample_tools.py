from backend.mcp_layer.tool_registry import BaseTool, tool_registry

class WeatherTool(BaseTool):
    @property
    def name(self) -> str: return "Weather"
    
    @property
    def description(self) -> str: return "Gets current weather for a location."

    def execute(self, location: str, **kwargs) -> dict:
        # Simulate API Call
        return {
            "location": location,
            "temperature_c": 24,
            "condition": "Clear skies",
            "forecast": "No major weather events expected."
        }

class FinanceTool(BaseTool):
    @property
    def name(self) -> str: return "Finance"
    
    @property
    def description(self) -> str: return "Gets market trends and stock data."

    def execute(self, symbol: str, **kwargs) -> dict:
        # Simulate API Call
        return {
            "symbol": symbol,
            "current_price": 150.25,
            "trend": "bullish",
            "volatility": "low"
        }

class TrafficTool(BaseTool):
    @property
    def name(self) -> str: return "Traffic"
    
    @property
    def description(self) -> str: return "Gets live traffic data."

    def execute(self, city: str, **kwargs) -> dict:
        # Simulate failing API call to test resilience
        raise Exception("Traffic API Rate Limit Exceeded")

# Auto-register tools on import
tool_registry.register(WeatherTool())
tool_registry.register(FinanceTool())
tool_registry.register(TrafficTool())
