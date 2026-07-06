import httpx
from typing import Dict, Any
from backend.execution.plugins.base import BaseActionPlugin
from backend.platform.cloud.logging_provider import cloud_logger

class RestAPIPlugin(BaseActionPlugin):
    """
    Executes raw HTTP REST requests.
    Supports idempotent executions via headers.
    """
    
    @property
    def name(self) -> str:
        return "RestAPIPlugin"

    async def execute(self, action_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        url = inputs.get("url")
        method = inputs.get("method", "POST")
        headers = inputs.get("headers", {})
        payload = inputs.get("payload", {})
        
        # Enforce idempotency key for POST/PUT/PATCH
        if method.upper() in ["POST", "PUT", "PATCH"]:
            if "Idempotency-Key" not in headers and "x-idempotency-key" not in [k.lower() for k in headers.keys()]:
                # Automatically inject idempotency if missing for safety
                headers["Idempotency-Key"] = f"{action_name}-{inputs.get('task_id', 'unknown')}"
                
        cloud_logger.info(f"RestAPIPlugin executing {method} {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Assume JSON response, fallback to text
            try:
                data = response.json()
            except:
                data = {"raw": response.text}
                
            return {
                "status_code": response.status_code,
                "data": data
            }

    async def rollback(self, action_name: str, execution_result: Dict[str, Any], rollback_steps: Dict[str, Any]) -> bool:
        """
        Executes a reverse REST call if defined (e.g. DELETE /resource/{id}).
        """
        if not rollback_steps:
            cloud_logger.warning(f"No rollback steps defined for RestAPIPlugin action {action_name}")
            return False
            
        url = rollback_steps.get("url")
        method = rollback_steps.get("method", "DELETE")
        headers = rollback_steps.get("headers", {})
        
        if not url:
            return False
            
        cloud_logger.info(f"RestAPIPlugin rolling back via {method} {url}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=headers)
                response.raise_for_status()
                return True
            except Exception as e:
                cloud_logger.error(f"RestAPIPlugin rollback failed: {e}")
                return False

    async def health_check(self) -> bool:
        return True
