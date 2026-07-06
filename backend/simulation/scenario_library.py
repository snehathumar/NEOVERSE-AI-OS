from typing import List

class ScenarioLibrary:
    """
    Manages the standard base universes we simulate for every decision.
    """
    
    @staticmethod
    def get_standard_scenarios() -> List[str]:
        return [
            "Best Case",
            "Expected Case",
            "Worst Case",
            "Economic Downturn",
            "Competitor Price Cut",
            "Customer Churn",
            "Supply Chain Failure",
            "Talent Shortage",
            "AI Automation",
            "Regulatory Change",
            "Technology Disruption",
            "Market Expansion"
        ]
