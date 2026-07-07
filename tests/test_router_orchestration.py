import pytest
import asyncio
from unittest.mock import patch, MagicMock

from backend.orchestrator.router import EnterpriseRouter
from backend.orchestrator.modules.base import ExecutionModule
from backend.orchestrator.registry import module_registry

# Mock Module for testing
class MockAuthModule(ExecutionModule):
    @property
    def name(self) -> str: return "MockAuthModule"
    @property
    def is_critical(self) -> bool: return True
    async def initialize(self) -> bool: return True
    async def validate(self, context) -> bool: return True
    async def execute(self, context): return {"auth": "success"}
    async def cancel(self) -> bool: return True
    async def cleanup(self) -> None: pass
    async def health_check(self) -> bool: return True

class MockReportModule(ExecutionModule):
    @property
    def name(self) -> str: return "MockReportModule"
    @property
    def is_critical(self) -> bool: return False
    async def initialize(self) -> bool: return True
    async def validate(self, context) -> bool: return True
    async def execute(self, context): raise Exception("Simulated Report Failure")
    async def cancel(self) -> bool: return True
    async def cleanup(self) -> None: pass
    async def health_check(self) -> bool: return True

# Register mocks
module_registry.register(MockAuthModule())
module_registry.register(MockReportModule())

@pytest.mark.asyncio
@patch("backend.orchestrator.classifier.generate_json")
async def test_router_partial_failure(mock_generate_json):
    """
    Test that the router gracefully handles a non-critical module failure,
    while still returning the overall response.
    """
    
    # Mock the classifier to request both our mock modules
    mock_generate_json.return_value = {
        "intent": "Business Analysis",
        "confidence": 95,
        "complexity": "High",
        "urgency": "Medium",
        "missing_information": [],
        "required_modules": ["MockAuthModule", "MockReportModule"]
    }
    
    router = EnterpriseRouter(user_id="test_tenant")
    
    # We patch the composer to just echo the results for easy asserting
    with patch("backend.orchestrator.composer.generate_json") as mock_composer:
        mock_composer.return_value = {"natural_response": "Mocked Composition"}
        
        # Disable BQ streaming for unit test
        with patch.object(router, '_stream_analytics', return_value=None):
            result = await router.process_request("Analyze this report", session_id="session123")
            
            # The report module should have failed but the router succeeded
            assert result["_routing_trace"]["status"] == "success"
            
            # Verify the raw outputs contain the error for the non-critical module
            raw = result.get("_raw_module_outputs", {})
            assert "MockAuthModule" in raw
            assert raw["MockAuthModule"]["auth"] == "success"
            assert "MockReportModule" in raw
            assert raw["MockReportModule"]["status"] == "failed"
            assert "exhausted all" in raw["MockReportModule"]["error"]
