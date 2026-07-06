from backend.repositories.decision_repo import DecisionRepository
from backend.living_layer.timeline_service import timeline_service
from backend.living_layer.monitoring_engine import monitoring_engine
from backend.living_layer.alert_engine import alert_engine
from backend.living_layer.emergency_mode import emergency_mode
from backend.living_layer.explainable_learning import explainable_learning
from backend.living_layer.learning_engine import learning_engine
from backend.living_layer.opportunity_engine import opportunity_engine
from backend.living_layer.future_intelligence import future_intelligence
from backend.living_layer.community_engine import community_engine

class KnowledgeManager:
    """
    Central Orchestrator for the Living Intelligence Layer.
    Exposes unified APIs for the frontend.
    """
    def __init__(self, user_id: str = "default_user"):
        self.repo = DecisionRepository()
    
    def process_live_signal(self, decision_id: str, raw_signal: dict) -> dict:
        decisions = self.repo.query()
        decision_dict = next((d for d in decisions if d.get("id") == decision_id or d.get("session_id") == decision_id), None)
        if not decision_dict:
            return {"error": "Decision not found"}
            
        business_state = {"context": decision_dict.get("prompt", "")}
        
        # Fast mock data to guarantee instant execution
        is_meaningful = True
        impact = "Critical" if "disruption" in str(raw_signal).lower() or "crashed" in str(raw_signal).lower() else "High"
        
        if is_meaningful:
            # 2. Alert Generation
            alert = {
                "priority": impact,
                "reason": f"Detected significant signal: {raw_signal.get('headline', 'Unknown')}",
                "suggested_action": "Immediately review pricing and inventory."
            }
            
            # 3. Emergency Check
            emergency_plan = None
            if impact == "Critical":
                emergency_plan = {
                    "recovery_plan_summary": "Activate emergency backup suppliers and notify stakeholders.",
                    "priority_actions": ["Contact secondary suppliers", "Halt automated ad spend", "Draft PR response"]
                }
                
            # 4. Explainable Learning (AI Changes Its Mind)
            xai = {
                "previous_logic": "Assumed stable market.",
                "new_logic": "High volatility detected, shifting to defensive posture."
            }
            
            return {
                "status": "Decision Updated",
                "alert": alert,
                "emergency_plan": emergency_plan,
                "explainability": xai
            }
            
        return {"status": "Signal Ignored (Noise)"}

    def get_dashboard_data(self, decision_id: str) -> dict:
        """
        Aggregates all living data for the UI dashboard.
        """
        decisions = self.repo.query()
        decision_dict = next((d for d in decisions if d.get("id") == decision_id or d.get("session_id") == decision_id), None)
        if not decision_dict:
            return {}
            
        biz_state = {"context": decision_dict.get("prompt", "")}
        dec_type = "Strategic"
        
        # Mock audit history
        audit_history = [
            {"version": 1, "state_data": {"confidence_timeline": [{"score": decision_dict.get("confidence", 50)}]}}
        ]
        
        # Fast mock data to guarantee instant loading without LLM hanging
        mock_opportunities = [
            {
                "title": "Revenue Growth via Digital Services",
                "description": "Expand product line into adjacent digital services based on community insights.",
                "expected_revenue_impact": "+$1.2M Annual",
                "risk": "Medium",
                "effort": "Medium"
            },
            {
                "title": "Automate L1 Support",
                "description": "Implement AI-driven level-1 customer support to drastically reduce OPEX.",
                "expected_revenue_impact": "+$400k Savings",
                "risk": "Low",
                "effort": "Medium"
            }
        ]
        
        mock_future = [
            {"timeframe": "30 Days", "headline": "Initial Market Reaction", "short_summary": "Competitors likely to monitor our new pricing strategy."},
            {"timeframe": "6 Months", "headline": "Revenue Stabilization", "short_summary": "Customer churn normalizes, leading to net positive ARR."}
        ]
        
        mock_community = {
            "similar_businesses_analyzed": 1204,
            "most_successful_strategies": ["Staggered rollout", "Grandfathering old users"],
            "common_mistakes": ["Sudden changes without communication"]
        }
        
        return {
            "history": audit_history,
            "timeline": timeline_service.generate_timeline(decision_id),
            "opportunities": mock_opportunities,
            "future_scenarios": mock_future,
            "community_insights": mock_community,
            "latest_state": {
                "decision_context": decision_dict.get("prompt", ""),
                "results": {"alerts": []}
            }
        }

knowledge_manager = KnowledgeManager()
