from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FeatureEntitlement(BaseModel):
    max_tokens_per_month: int
    max_simulations_per_month: int
    max_executions_per_month: int
    allowed_modules: List[str]

class SubscriptionPlan(BaseModel):
    plan_id: str
    name: str # e.g., "Free", "Pro", "Enterprise"
    price_monthly: float
    entitlements: FeatureEntitlement

class OrgSubscription(BaseModel):
    org_id: str
    plan_id: str
    stripe_customer_id: str
    stripe_subscription_id: Optional[str] = None
    status: str # active, past_due, canceled, trialing
    current_period_end: str
    tokens_used: int = 0
    simulations_used: int = 0
    executions_used: int = 0

class UsageRecord(BaseModel):
    record_id: str
    org_id: str
    user_id: str
    timestamp: str
    resource_type: str # e.g., 'token', 'simulation', 'execution'
    quantity: int
    module_name: str

class Invoice(BaseModel):
    invoice_id: str
    org_id: str
    amount_due: float
    status: str
    pdf_url: Optional[str] = None
