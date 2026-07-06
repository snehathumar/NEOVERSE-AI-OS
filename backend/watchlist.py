class Watchlist:
    def __init__(self):
        self.tracked_metrics = [
            "Fuel Prices",
            "Local Weather",
            "Competitor Activity",
            "Raw Material Costs",
            "Consumer Sentiment"
        ]
        
    def add_metric(self, metric: str):
        if metric not in self.tracked_metrics:
            self.tracked_metrics.append(metric)
            
    def remove_metric(self, metric: str):
        if metric in self.tracked_metrics:
            self.tracked_metrics.remove(metric)

    def get_watchlist(self):
        return self.tracked_metrics
