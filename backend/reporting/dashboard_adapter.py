from typing import Dict, Any
from backend.reporting.models import VisualizationData

class DashboardAdapter:
    """
    Transforms core pipeline outputs into neutral, structured JSON visualization schemas.
    Does NOT output Chart.js/Recharts config. Just generic nodes, edges, heatmaps, and series.
    """
    
    def generate_visualizations(self, evidence_data: dict, decision_data: dict, debate_data: dict, simulation_data: dict) -> VisualizationData:
        # Extract Knowledge Graph from evidence
        kg_nodes = evidence_data.get("graph_nodes", [])
        kg_edges = evidence_data.get("graph_edges", [])
        
        # Build Decision Timeline
        decision_timeline = [
            {"timestamp": "t0", "event": "Information Gathered", "module": "Evidence"},
            {"timestamp": "t1", "event": "Reasoning Complete", "module": "Decision"},
            {"timestamp": "t2", "event": "Boardroom Consensus Reached", "module": "Debate"},
            {"timestamp": "t3", "event": "Simulations Concluded", "module": "Simulation"}
        ]
        
        # Build Confidence Timeline
        confidence_timeline = [
            {"step": "Initial", "score": 50},
            {"step": "Evidence Verified", "score": 75},
            {"step": "Decision Formulated", "score": 80},
            {"step": "Debate Challenged", "score": 70}, # Dip during challenge
            {"step": "Debate Consensus", "score": 85},
            {"step": "Simulation Verified", "score": 92}
        ]
        
        # Build Risk & Opportunity Matrices (Mock extraction)
        risk_matrix = {
            "x_axis": "Impact",
            "y_axis": "Probability",
            "data_points": [{"name": "Market Shift", "x": 8, "y": 4}, {"name": "Talent Loss", "x": 6, "y": 2}]
        }
        
        opportunity_matrix = {
            "x_axis": "ROI",
            "y_axis": "Feasibility",
            "data_points": [{"name": "New Segment", "x": 9, "y": 7}, {"name": "Cost Reduction", "x": 5, "y": 8}]
        }
        
        # Evidence Heatmap
        evidence_heatmap = {
            "x_axis": "Source Domain",
            "y_axis": "Trust Score Segment",
            "data": [{"x": "Finance", "y": "High Trust", "value": 15}, {"x": "Tech", "y": "Med Trust", "value": 5}]
        }
        
        # KPI Forecast
        kpi_forecast = [
            {"kpi": "Revenue", "current": 100, "projected_best": 150, "projected_worst": 90, "projected_expected": 120},
            {"kpi": "Costs", "current": 80, "projected_best": 75, "projected_worst": 95, "projected_expected": 82}
        ]
        
        return VisualizationData(
            decision_timeline=decision_timeline,
            confidence_timeline=confidence_timeline,
            risk_matrix=risk_matrix,
            opportunity_matrix=opportunity_matrix,
            evidence_heatmap=evidence_heatmap,
            kpi_forecast=kpi_forecast,
            knowledge_graph={"nodes": kg_nodes, "edges": kg_edges}
        )
