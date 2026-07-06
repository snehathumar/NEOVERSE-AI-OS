import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from backend.reporting.models import ExecutiveReport, ReportMetadata, ExplainabilityAudit
from backend.reporting.synthesizer import ReportSynthesizer
from backend.reporting.dashboard_adapter import DashboardAdapter
from backend.reporting.generators import MarkdownGenerator, JSONGenerator, PDFGenerator, DOCXGenerator
from backend.memory.manager import StorageManager
from backend.platform.cloud.logging_provider import cloud_logger
from backend.platform.events.event_bus import EventBus

class ExecutiveReportingEngine:
    """
    Core engine for Phase 10: Executive Reporting & Explainability.
    """
    def __init__(self):
        self.synthesizer = ReportSynthesizer()
        self.dashboard_adapter = DashboardAdapter()
        self.storage_manager = StorageManager()
        self.event_bus = EventBus()

    async def execute_reporting(self, context: dict) -> Dict[str, Any]:
        session_id = context.get("session_id", str(uuid.uuid4()))
        
        # 1. Extract outputs from upstream modules
        evidence_data = context.get("upstream_results", {}).get("EvidenceModule", {})
        decision_data = context.get("upstream_results", {}).get("DecisionModule", {})
        debate_data = context.get("upstream_results", {}).get("DebateModule", {})
        simulation_data = context.get("upstream_results", {}).get("SimulationModule", {})
        
        cloud_logger.info("Synthesizing Executive Report Narratives...")
        
        # 2. Synthesize Narrative
        narrative = self.synthesizer.synthesize_narrative(
            evidence_data, decision_data, debate_data, simulation_data
        )
        
        # 3. Generate Visualizations
        visualizations = self.dashboard_adapter.generate_visualizations(
            evidence_data, decision_data, debate_data, simulation_data
        )
        
        # 4. Build Report Object
        report_id = str(uuid.uuid4())
        report = ExecutiveReport(
            id=report_id,
            metadata=ReportMetadata(
                decision_id=decision_data.get("decision_id", "unknown"),
                session_id=session_id,
                version_number=1,
                parent_report_id=None,
                generation_timestamp=datetime.now(timezone.utc).isoformat(),
                trigger_source="pipeline",
                change_summary="Initial Generation",
                processing_timeline={}
            ),
            visualizations=visualizations,
            explainability=ExplainabilityAudit(**narrative.get("explainability", {})),
            **{k: v for k, v in narrative.items() if k != "explainability"}
        )
        
        # 5. Save JSON metadata synchronously
        self.storage_manager.save_json(f"reports/{report_id}.json", report.model_dump())
        
        # 6. Fire off background tasks for PDF/DOCX generation
        asyncio.create_task(self._generate_and_store_exports(report))
        
        # 7. Return JSON immediately to unblock user
        return report.model_dump()

    async def _generate_and_store_exports(self, report: ExecutiveReport):
        """Runs in the background to generate heavy PDF/DOCX files and upload to GCS."""
        try:
            cloud_logger.info(f"Starting background export generation for report {report.id}")
            
            generators = {
                "pdf": PDFGenerator(),
                "docx": DOCXGenerator(),
                "md": MarkdownGenerator()
            }
            
            for ext, generator in generators.items():
                byte_content = generator.generate(report)
                # Save to StorageManager (which handles GCS with local fallback)
                path = f"reports/exports/{report.id}/executive_report.{ext}"
                self.storage_manager.save_bytes(path, byte_content)
                
            # Emit EventBus notification when ready
            self.event_bus.publish("report_exports_ready", {
                "report_id": report.id,
                "status": "success",
                "message": "PDF and DOCX exports are ready for download."
            })
            
            cloud_logger.info(f"Background exports complete for report {report.id}")
            
        except Exception as e:
            cloud_logger.error(f"Failed background export generation: {e}")
            self.event_bus.publish("report_exports_failed", {
                "report_id": report.id,
                "error": str(e)
            })
