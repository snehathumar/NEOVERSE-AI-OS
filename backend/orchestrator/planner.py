from typing import Dict, Any, List
from backend.orchestrator.classifier import IntentClassifier
from backend.orchestrator.context_builder import UnifiedContext
from backend.orchestrator.registry import module_registry
from backend.platform.cloud.logging_provider import cloud_logger

class ExecutionPlan:
    def __init__(self):
        self.priority: int = 1
        self.estimated_latency: float = 0.0
        self.estimated_cost: float = 0.0
        self.parallel_groups: List[List[str]] = []
        self.fallback_modules: Dict[str, str] = {}
        self.required_permissions: List[str] = []
        self.is_interview_mode: bool = False
        self.missing_fields: List[str] = []

class ExecutionPlanner:
    """
    Constructs the ExecutionPlan based on classification.
    Optimizes parallel groups and dependencies.
    """
    
    def __init__(self):
        # We could load adaptive routing stats from BigQuery here
        self.historical_stats = {} 

    def create_plan(self, classification: Dict[str, Any], context: UnifiedContext) -> ExecutionPlan:
        plan = ExecutionPlan()
        
        # 1. Handle Missing Information (Interview Mode / Information Gathering State)
        missing_info = classification.get("missing_information", [])
        if missing_info and classification.get("complexity") in ["High", "Critical"]:
            plan.is_interview_mode = True
            plan.missing_fields = missing_info
            # Route directly to the Chat/Interview module to ask for info
            plan.parallel_groups = [["ChatModule"]]
            return plan

        # 2. Extract modules requested by Classifier
        requested_modules = classification.get("required_modules", [])
        if not requested_modules:
            requested_modules = ["ChatModule"]
            
        # 3. Filter by available modules in Registry
        available_modules = module_registry.list_modules()
        valid_modules = [m for m in requested_modules if m in available_modules]
        
        if not valid_modules:
            valid_modules = ["ChatModule"] # Safe fallback
            
        # 4. Dependency Resolution & Parallel Groups Optimization
        # Simple heuristic for now: Critical / Heavy engines run first or parallel, 
        # Report generators run last.
        
        early_group = []
        compute_group = []
        final_group = []
        
        for mod in valid_modules:
            if mod in ["SecurityModule"]:
                # Security is handled explicitly below as priority 0
                pass
            elif mod in ["BillingModule"]:
                # Billing is handled explicitly below as priority 1
                pass
            elif mod in ["MemoryModule", "AuthModule"]:
                early_group.append(mod)
            elif mod in ["EvidenceModule", "DecisionModule", "DebateModule", "SimulationModule", "MarketplaceModule", "ReportGeneratorModule", "SelfEvolutionModule", "ExecutionModule"]:
                # We will handle these explicitly below for sequential ordering
                pass
            else:
                compute_group.append(mod)
                
        # 2. Add structural groups explicitly in order
        if "SecurityModule" in valid_modules:
            plan.parallel_groups.append(["SecurityModule"])
            
        if "BillingModule" in valid_modules:
            plan.parallel_groups.append(["BillingModule"])
            
        if early_group:
            plan.parallel_groups.append(early_group)
            
        # Hardcode Evidence before Decision
        if "EvidenceModule" in valid_modules:
            plan.parallel_groups.append(["EvidenceModule"])
            
        if compute_group:
            plan.parallel_groups.append(compute_group)
            
        # Hardcode Decision after Evidence
        if "DecisionModule" in valid_modules:
            plan.parallel_groups.append(["DecisionModule"])
            
        # Hardcode Debate after Decision if Debate is in valid modules
        if "DebateModule" in valid_modules and "DecisionModule" in valid_modules:
            plan.parallel_groups.append(["DebateModule"])
            
        # Hardcode Simulation after Debate if Simulation is in valid modules
        if "SimulationModule" in valid_modules and "DecisionModule" in valid_modules:
            plan.parallel_groups.append(["SimulationModule"])
            
        if "ReportGeneratorModule" in valid_modules:
            plan.parallel_groups.append(["ReportGeneratorModule"])
            
        if "MarketplaceModule" in valid_modules:
            plan.parallel_groups.append(["MarketplaceModule"])
            
        if "SelfEvolutionModule" in valid_modules:
            plan.parallel_groups.append(["SelfEvolutionModule"])
            
        if "ExecutionModule" in valid_modules:
            plan.parallel_groups.append(["ExecutionModule"])
            
        # 5. Adaptive Routing adjustments (placeholder for stats-based ordering)
        plan.priority = 10 if classification.get("urgency") in ["High", "Immediate"] else 5
        
        cloud_logger.info(f"Execution Plan generated: {plan.parallel_groups}")
        return plan
