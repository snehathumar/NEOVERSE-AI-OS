import asyncio
from typing import Dict, Any, List
from backend.debate.registry import registry
from backend.debate.devils_advocate import DevilsAdvocateEngine
from backend.debate.consensus import ConsensusEngine
from backend.debate.models import DebateTrace, ValidationScores
from backend.platform.cloud.logging_provider import cloud_logger

# Import experts so they register themselves
import backend.debate.experts.implementations as impls

class DebateEngine:
    """
    The Core Multi-Agent Decision Validation Engine.
    Executes the async, multi-round AI Boardroom debate.
    """
    
    def __init__(self):
        self.devils_advocate = DevilsAdvocateEngine()
        self.consensus = ConsensusEngine()
        
    def _instantiate_expert(self, role: str):
        # Find the correct expert class from implementations based on role
        for name, cls in impls.__dict__.items():
            if isinstance(cls, type) and issubclass(cls, impls.BaseExpert) and cls != impls.BaseExpert:
                if cls().role == role:
                    return cls()
        raise ValueError(f"Expert role {role} not found in implementations.")

    async def execute_debate(self, decision_context: dict) -> Dict[str, Any]:
        cloud_logger.info("Starting Enterprise Multi-Agent Decision Validation Debate")
        
        # 1. Select Expert Panel
        decision_type = decision_context.get("business_understanding", {}).get("decision_type", "Enterprise Strategy")
        panel_roles = registry.select_experts(decision_type)
        experts = [self._instantiate_expert(role) for role in panel_roles]
        
        cloud_logger.info(f"Expert Panel selected: {panel_roles}")
        
        # 2. Round 1: Independent Analysis
        cloud_logger.info("Executing Round 1: Independent Analysis")
        round_1_tasks = [expert.analyze(decision_context) for expert in experts]
        round_1_opinions = await asyncio.gather(*round_1_tasks)
        
        # 3. Round 2: Cross Review
        cloud_logger.info("Executing Round 2: Cross Examination")
        round_2_tasks = []
        for expert in experts:
            opposing = [op for op in round_1_opinions if op.expert_role != expert.role]
            round_2_tasks.append(expert.challenge(decision_context, opposing))
        round_2_challenges = await asyncio.gather(*round_2_tasks)
        
        # 4. Round 3: Defense
        cloud_logger.info("Executing Round 3: Defense & Revision")
        round_3_tasks = []
        for expert in experts:
            # Find my opinion
            my_opinion = next(op for op in round_1_opinions if op.expert_role == expert.role)
            # Find challenges directed at me
            challenges_at_me = [c for c in round_2_challenges if c.target_expert == expert.role]
            round_3_tasks.append(expert.defend(my_opinion, challenges_at_me))
        round_3_defenses = await asyncio.gather(*round_3_tasks)
        
        # 5. Final Vote
        cloud_logger.info("Executing Final Vote")
        vote_tasks = [expert.vote(decision_context, round_3_defenses) for expert in experts]
        final_votes = await asyncio.gather(*vote_tasks)
        
        # 6. Devil's Advocate
        cloud_logger.info("Executing Devil's Advocate")
        final_defenses_dicts = [d.model_dump() for d in round_3_defenses]
        da_report = self.devils_advocate.execute(decision_context, final_defenses_dicts)
        
        # 7. Consensus
        cloud_logger.info("Building Consensus")
        consensus_res = self.consensus.execute(final_votes, da_report)
        
        # 8. Validation Scores
        # Simple heuristic mapping for now
        v_scores = ValidationScores(
            consensus_score=consensus_res.consensus_confidence,
            debate_strength=consensus_res.disagreement_score if consensus_res.disagreement_score > 20 else 50,
            evidence_strength=80, # Ideally calculated from evidence engine injected state
            assumption_risk=len(da_report.catastrophic_risks) * 10,
            overall_validation_score=(consensus_res.consensus_confidence + consensus_res.agreement_score) // 2
        )
        
        trace = DebateTrace(
            expert_panel=panel_roles,
            round_1_opinions=round_1_opinions,
            round_2_challenges=round_2_challenges,
            round_3_defenses=round_3_defenses,
            devils_advocate=da_report,
            final_votes=final_votes,
            consensus=consensus_res,
            validation_scores=v_scores,
            learning_insights={} # Placeholder for memory engine to fill
        )
        
        return trace.model_dump()
