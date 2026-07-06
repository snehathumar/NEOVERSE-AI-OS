import uuid
from typing import Dict, Any
from backend.orchestrator.modules.base import ExecutionModule
from backend.security.auth import JWTValidator
from backend.security.tenant_manager import TenantManager
from backend.security.rbac import RBACEngine
from backend.security.audit_logger import AuditLogger
from backend.security.models import SecurityContext
from backend.platform.cloud.logging_provider import cloud_logger

class SecurityModule(ExecutionModule):
    """
    The central Enterprise Security & Governance Module.
    Executes FIRST in the pipeline to enforce authentication, tenant isolation, and RBAC.
    """
    def __init__(self):
        self.jwt_validator = JWTValidator()
        self.tenant_manager = TenantManager()
        self.rbac = RBACEngine()
        self.audit = AuditLogger()
        
    @property
    def name(self) -> str:
        return "SecurityModule"

    @property
    def is_critical(self) -> bool:
        return True # Without security, the pipeline must HALT immediately

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # Requires HTTP headers to be injected by the Router
        return "http_headers" in context

    async def execute(self, context: dict) -> dict:
        headers = context.get("http_headers", {})
        
        try:
            # 1. Authenticate Request
            payload = self.jwt_validator.authenticate_request(headers)
            user_id = payload.get("user_id")
            org_id = payload.get("org_id")
            roles = payload.get("roles", [])
            session_id = headers.get("X-Session-ID", str(uuid.uuid4()))
            
            # 2. Enforce Tenant Isolation
            self.tenant_manager.validate_tenant_access(org_id)
            
            # 3. Build Security Context
            sec_context = SecurityContext(
                org_id=org_id,
                user_id=user_id,
                session_id=session_id,
                roles=roles,
                is_judge_mode=False
            )
            
            # 4. Optional: Resource-level RBAC Check 
            # (In reality, we'd check against the specific action requested by the Router payload)
            if not self.rbac.validate_access(sec_context, resource="pipeline", action="execute"):
                raise PermissionError("User lacks pipeline execution permissions.")
                
            # 5. Log successful authentication
            self.audit.log_event(
                sec_context, 
                action="PIPELINE_EXECUTE", 
                resource="NEOVERSE_ROUTER", 
                status="SUCCESS", 
                details={"ip": headers.get("X-Forwarded-For", "unknown")}
            )
            
            cloud_logger.info(f"SecurityContext established for {user_id}@{org_id}")
            
            # Return context to be injected into downstream modules
            return {
                "security_context": sec_context.model_dump(),
                "status": "authenticated"
            }
            
        except Exception as e:
            cloud_logger.error(f"SecurityModule Authorization Failed: {e}")
            # If we had partial context, we'd log the failure, but we just log generically
            raise PermissionError(f"Security Exception: {e}")

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
