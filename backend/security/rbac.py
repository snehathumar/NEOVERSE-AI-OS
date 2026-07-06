from typing import List, Dict, Any
from backend.security.models import SecurityContext

class RBACEngine:
    """
    Evaluates fine-grained Resource-level permissions based on Enterprise Policies.
    """
    def __init__(self):
        # Mock policy definition
        self.role_permissions = {
            "Organization Admin": ["*"],
            "Decision Reviewer": ["read:decision", "execute:workflow", "read:report"],
            "Standard User": ["read:decision", "create:decision"],
            "Judge Mode": ["read:*"] # Read-only strictly enforced
        }

    def validate_access(self, context: SecurityContext, resource: str, action: str) -> bool:
        """
        Check if the user's roles permit the requested action on the resource.
        """
        if context.is_judge_mode and action != "read":
            return False # Judge mode is strictly read-only
            
        requested_perm = f"{action}:{resource}"
        
        for role in context.roles:
            perms = self.role_permissions.get(role, [])
            if "*" in perms or requested_perm in perms or f"{action}:*" in perms:
                return True
                
        return False
