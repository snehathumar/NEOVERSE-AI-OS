from backend.intelligence.advanced.models import ReasoningStep, ReasoningPipelineTrace
import time

class ReasoningTraceEngine:
    """
    Makes the AI's decision process 100% transparent.
    Records every step of the decision pipeline (Input, Output, Confidence, Time).
    """
    def __init__(self):
        self._current_trace = None
        
    def start_trace(self, decision_id: str):
        self._current_trace = {
            "decision_id": decision_id,
            "steps": [],
            "final_recommendation": ""
        }
        print(f"🔎 [ReasoningTrace] Started tracing for Decision ID: {decision_id}")

    def log_step(self, step_name: str, input_summary: str, output_summary: str, confidence: int, evidence_used: list, execution_ms: int):
        if not self._current_trace:
            return
            
        step = ReasoningStep(
            step_name=step_name,
            input_summary=input_summary,
            output_summary=output_summary,
            confidence=confidence,
            execution_time_ms=execution_ms,
            evidence_used=evidence_used
        )
        self._current_trace["steps"].append(step.dict())
        print(f"🔎 [ReasoningTrace] Logged Step: {step_name} ({execution_ms}ms)")

    def end_trace(self, final_recommendation: str) -> dict:
        if not self._current_trace:
            return {}
            
        self._current_trace["final_recommendation"] = final_recommendation
        print("🔎 [ReasoningTrace] Trace complete.")
        return self._current_trace

reasoning_trace_engine = ReasoningTraceEngine()
