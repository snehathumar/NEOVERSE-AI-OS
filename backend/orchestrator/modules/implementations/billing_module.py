from backend.orchestrator.modules.base import ExecutionModule
from backend.billing.enforcement import BillingEnforcement
from backend.billing.metering import UsageMeteringEngine
from backend.platform.cloud.logging_provider import cloud_logger

class BillingModule(ExecutionModule):
    """
    Executes immediately after SecurityModule to enforce subscription plans and usage quotas.
    Returns structured HTTP 402/403 errors if the organization has insufficient quota or plan entitlements.
    """
    def __init__(self):
        self.enforcement = BillingEnforcement()
        self.metering = UsageMeteringEngine()
        
    @property
    def name(self) -> str:
        return "BillingModule"

    @property
    def is_critical(self) -> bool:
        return True # Without billing, we lose revenue. Must halt on failure.

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        return "security_context" in context

    async def execute(self, context: dict) -> dict:
        sec_context = context.get("security_context", {})
        org_id = sec_context.get("org_id")
        user_id = sec_context.get("user_id")
        
        # Determine what features the user is trying to access based on the payload
        # For this prototype, we'll validate the core routing capabilities.
        # In a real scenario, this would inspect `context['user_request']`.
        
        try:
            # 1. Enforce Plan Limits
            # The enforcer will raise an HTTPException (402 or 403) if limits are exceeded,
            # which will bubble up through FastAPI directly to the user.
            self.enforcement.validate_action(org_id, requested_module="DecisionModule")
            
            # 2. Async Metering
            # This is fire-and-forget; does not block the pipeline
            self.metering.record_usage(
                org_id=org_id,
                user_id=user_id,
                resource_type="api_request",
                quantity=1,
                module_name="EnterpriseRouter"
            )
            
            cloud_logger.info(f"Billing limits validated for {org_id}")
            
            return {
                "status": "billing_verified",
                "org_id": org_id
            }
            
        except Exception as e:
            cloud_logger.error(f"BillingModule Enforcement Failed: {e}")
            raise e # Will be caught by FastAPI global exception handler

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
