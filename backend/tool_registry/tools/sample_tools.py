from backend.tool_registry.tool_base import BaseTool, tool_registry
import random

class WeatherTool(BaseTool):
    @property
    def name(self) -> str: return "Weather"
    
    @property
    def description(self) -> str: return "Current weather conditions."

    def execute(self, location: str, **kwargs) -> dict:
        return {
            "location": location,
            "temperature_c": 22,
            "condition": "Cloudy",
            "wind_speed": "15 km/h"
        }

class FinanceTool(BaseTool):
    @property
    def name(self) -> str: return "Finance"
    
    @property
    def description(self) -> str: return "Financial market data."

    def execute(self, symbol: str, **kwargs) -> dict:
        return {
            "symbol": symbol,
            "current_price": round(random.uniform(100, 500), 2),
            "trend": "Bullish",
            "volume": "High"
        }

class TrafficTool(BaseTool):
    @property
    def name(self) -> str: return "Traffic"
    
    @property
    def description(self) -> str: return "Live traffic data."

    def execute(self, location: str, **kwargs) -> dict:
        # Simulate API failure to demonstrate fallback
        raise Exception("Traffic API Rate Limit Exceeded.")

class NewsTool(BaseTool):
    @property
    def name(self) -> str: return "News"
    
    @property
    def description(self) -> str: return "Latest business news."

    def execute(self, query: str, **kwargs) -> dict:
        return {
            "query": query,
            "headlines": ["AI OS Adoption Surges", "New Regulations in Tech Sector"],
            "sentiment": "Positive"
        }

# Auto-register
tool_registry.register(WeatherTool)
tool_registry.register(FinanceTool)
tool_registry.register(TrafficTool)
tool_registry.register(NewsTool)
