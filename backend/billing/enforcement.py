from typing import Dict, Any, Optional
from fastapi import HTTPException
from backend.billing.models import OrgSubscription, SubscriptionPlan, FeatureEntitlement

class BillingEnforcement:
    """
    Validates organization subscription plans against quotas and feature entitlements.
    """
    def __init__(self):
        # Mock Database mapping
        self.plans = {
            "free": SubscriptionPlan(
                plan_id="free",
                name="Free Tier",
                price_monthly=0.0,
                entitlements=FeatureEntitlement(
                    max_tokens_per_month=10000,
                    max_simulations_per_month=3,
                    max_executions_per_month=5,
                    allowed_modules=["EvidenceModule", "DecisionModule", "ReportingModule"]
                )
            ),
            "enterprise": SubscriptionPlan(
                plan_id="enterprise",
                name="Enterprise Tier",
                price_monthly=999.0,
                entitlements=FeatureEntitlement(
                    max_tokens_per_month=10000000,
                    max_simulations_per_month=9999,
                    max_executions_per_month=9999,
                    allowed_modules=["EvidenceModule", "DecisionModule", "DebateModule", "SimulationModule", "ReportingModule", "ExecutionModule", "SelfEvolutionModule"]
                )
            )
        }
        
        # Mock active subscriptions
        self.org_subs = {
            "org-neo-enterprise": OrgSubscription(
                org_id="org-neo-enterprise",
                plan_id="enterprise",
                stripe_customer_id="cus_123",
                status="active",
                current_period_end="2030-01-01T00:00:00Z"
            )
        }

    def _get_org_subscription(self, org_id: str) -> OrgSubscription:
        # Default to free tier if no active sub exists
        if org_id not in self.org_subs:
            return OrgSubscription(
                org_id=org_id,
                plan_id="free",
                stripe_customer_id="unregistered",
                status="active",
                current_period_end="2030-01-01T00:00:00Z"
            )
        return self.org_subs[org_id]
        
    def validate_action(self, org_id: str, requested_module: str, requested_cost: int = 0):
        """
        Validates if the org is allowed to execute the requested module 
        and if they have enough quota remaining.
        Raises HTTP 402 if limits exceeded.
        """
        sub = self._get_org_subscription(org_id)
        
        if sub.status not in ["active", "trialing"]:
            raise HTTPException(status_code=402, detail=f"Subscription status is {sub.status}. Payment required.")
            
        plan = self.plans.get(sub.plan_id)
        if not plan:
            raise HTTPException(status_code=500, detail="Configuration error: Plan not found.")
            
        ent = plan.entitlements
        
        # 1. Check Feature Entitlement
        if requested_module not in ent.allowed_modules and "all" not in ent.allowed_modules:
            raise HTTPException(status_code=403, detail=f"Your current plan ({plan.name}) does not include access to the {requested_module}. Please upgrade.")
            
        # 2. Check Usage Quotas
        if requested_module == "SimulationModule" and sub.simulations_used >= ent.max_simulations_per_month:
            raise HTTPException(status_code=402, detail=f"Simulation quota exceeded for {plan.name} plan.")
            
        if requested_module == "ExecutionModule" and sub.executions_used >= ent.max_executions_per_month:
            raise HTTPException(status_code=402, detail=f"Execution workflow quota exceeded for {plan.name} plan.")
            
        if (sub.tokens_used + requested_cost) > ent.max_tokens_per_month:
            raise HTTPException(status_code=402, detail=f"Token limit exceeded for {plan.name} plan. Please upgrade to support heavier AI workloads.")
            
        return True
