import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

class EnterpriseReportGenerator:
    """
    Generates professional Enterprise Decision Reports using ReportLab.
    """
    def __init__(self, output_dir: str = "exports/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(name='ReportTitle', parent=self.styles['Heading1'], fontSize=24, spaceAfter=20, alignment=1, textColor=colors.HexColor('#2c3e50')))
        self.styles.add(ParagraphStyle(name='SectionHeader', parent=self.styles['Heading2'], fontSize=16, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor('#34495e')))
        self.styles.add(ParagraphStyle(name='CustomBodyText', parent=self.styles['Normal'], fontSize=11, spaceAfter=10, leading=14))
        self.styles.add(ParagraphStyle(name='CustomEmphasis', parent=self.styles['Normal'], fontName='Helvetica-Oblique', textColor=colors.HexColor('#7f8c8d')))

    def generate_decision_report(self, decision_id: str, data: dict) -> str:
        """
        Generates a PDF report for a given decision.
        Returns the absolute path to the generated PDF.
        """
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"Decision_Report_{decision_id}_{timestamp_str}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        elements = []
        
        # 1. Title & Meta
        elements.append(Paragraph(f"NEOVERSE AI OS: Strategic Decision Report", self.styles['ReportTitle']))
        elements.append(Paragraph(f"<b>Decision ID:</b> {decision_id}", self.styles['CustomBodyText']))
        elements.append(Paragraph(f"<b>Generated At:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", self.styles['CustomBodyText']))
        elements.append(Spacer(1, 20))
        
        # 2. Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Paragraph(data.get("prompt", "No objective provided."), self.styles['CustomBodyText']))
        
        # 3. Collected Evidence / Facts
        elements.append(Paragraph("Collected Business Evidence", self.styles['SectionHeader']))
        facts = data.get("facts", [])
        if facts:
            fact_data = [[Paragraph(f"• {f}", self.styles['CustomBodyText'])] for f in facts]
            t = Table(fact_data, colWidths=[400])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("No specific facts were collected.", self.styles['CustomEmphasis']))
        
        # 4. Recommendation & Confidence
        elements.append(Paragraph("AI Recommendation", self.styles['SectionHeader']))
        elements.append(Paragraph(data.get("recommendation", "No recommendation generated."), self.styles['CustomBodyText']))
        
        confidence = data.get("confidence", 0)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Overall System Confidence:</b> {confidence}%", self.styles['CustomBodyText']))
        
        # 5. Parallel Universes / Debate (If available)
        universes = data.get("universes", {})
        if universes:
            elements.append(Paragraph("Simulated Scenarios (Universes)", self.styles['SectionHeader']))
            for uni_name, uni_desc in universes.items():
                elements.append(Paragraph(f"<b>{uni_name.upper()}</b>", self.styles['CustomBodyText']))
                elements.append(Paragraph(str(uni_desc), self.styles['CustomBodyText']))
                elements.append(Spacer(1, 5))
                
        # Build PDF
        doc.build(elements)
        return os.path.abspath(filepath)
