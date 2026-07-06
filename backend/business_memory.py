class BusinessMemory:
    def __init__(self):
        # Default Hardcoded Profile for immediate onboarding
        self.profile = {
            "industry": "Coffee Shop",
            "location": "Downtown Business District",
            "products": ["Espresso", "Cappuccino", "Pastries", "Sandwiches"],
            "employees": 5,
            "competitors": "Medium (2 nearby cafes)"
        }
        
        # Live KPIs
        self.kpis = {
            "revenue": 12000,
            "costs": 8000,
            "profit_margin": 33.3,
            "customer_growth": 2.5,
            "inventory_status": "Optimal",
            "business_health": 85
        }
        
        self.watchlist = ["Coffee Beans Price", "Weekend Footfall", "Local Weather", "Competitor Promotions"]
        self.past_decisions = []
        self.current_day = 1
        
    def update_kpis(self, deltas):
        """Update KPIs based on daily changes"""
        for key, value in deltas.items():
            if key in self.kpis:
                if isinstance(self.kpis[key], (int, float)):
                    self.kpis[key] += value
                else:
                    self.kpis[key] = value
                    
        # Ensure health stays 0-100
        self.kpis["business_health"] = max(0, min(100, self.kpis["business_health"]))

    def record_decision(self, decision, prediction, actual_result=None):
        self.past_decisions.append({
            "day": self.current_day,
            "decision": decision,
            "prediction": prediction,
            "actual_result": actual_result
        })

    def advance_day(self):
        self.current_day += 1
