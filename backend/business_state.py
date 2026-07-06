class BusinessState:
    def __init__(self):
        self.profile = {
            "industry": "Unknown",
            "location": "Unknown",
            "products": [],
            "employees": 0,
            "competitors": "Unknown"
        }
        
        self.kpis = {
            "revenue": 0,
            "costs": 0,
            "profit_margin": 0.0,
            "customer_growth": 0.0,
            "inventory_status": "Unknown",
            "business_health": 50
        }
        
        self.past_recommendations = []
        self.current_day = 1
        
    def update_profile(self, new_profile: dict):
        self.profile.update(new_profile)
        
    def update_kpis(self, deltas: dict):
        for key, value in deltas.items():
            if key in self.kpis:
                if isinstance(self.kpis[key], (int, float)):
                    self.kpis[key] += value
                else:
                    self.kpis[key] = value
        
        # Keep health bounded
        if isinstance(self.kpis.get("business_health"), (int, float)):
            self.kpis["business_health"] = max(0, min(100, self.kpis["business_health"]))

    def record_recommendation(self, recommendation: dict):
        self.past_recommendations.append({
            "day": self.current_day,
            "recommendation": recommendation,
            "status": "Active"
        })

    def advance_time(self):
        self.current_day += 1
