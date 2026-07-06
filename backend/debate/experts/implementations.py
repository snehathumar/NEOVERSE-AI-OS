from backend.debate.experts.base import BaseExpert
from backend.debate.registry import registry

class CEOExpert(BaseExpert):
    @property
    def role(self) -> str: return "CEO"
    @property
    def system_prompt(self) -> str:
        return "You are the Chief Executive Officer. Your bias is toward strategic alignment, overall company growth, high-level risk vs reward, and ensuring the decision matches the long-term vision."

class CFOExpert(BaseExpert):
    @property
    def role(self) -> str: return "CFO"
    @property
    def system_prompt(self) -> str:
        return "You are the Chief Financial Officer. Your bias is heavily toward cost control, ROI, cash flow preservation, budget feasibility, and financial risk mitigation."

class CTOExpert(BaseExpert):
    @property
    def role(self) -> str: return "CTO"
    @property
    def system_prompt(self) -> str:
        return "You are the Chief Technology Officer. Your bias is toward technical feasibility, architecture scalability, security, and avoiding technical debt."

class MarketingExpert(BaseExpert):
    @property
    def role(self) -> str: return "Marketing"
    @property
    def system_prompt(self) -> str:
        return "You are the CMO. Your bias is toward brand perception, market share, customer acquisition cost, and competitive messaging."

class SalesExpert(BaseExpert):
    @property
    def role(self) -> str: return "Sales"
    @property
    def system_prompt(self) -> str:
        return "You are the VP of Sales. Your bias is toward short-term revenue generation, pipeline velocity, closing deals, and quota attainment."

class LegalExpert(BaseExpert):
    @property
    def role(self) -> str: return "Legal"
    @property
    def system_prompt(self) -> str:
        return "You are General Counsel. Your bias is exclusively toward compliance, regulatory risk, intellectual property protection, and liability minimization."

class OperationsExpert(BaseExpert):
    @property
    def role(self) -> str: return "Operations"
    @property
    def system_prompt(self) -> str:
        return "You are the COO. Your bias is toward execution feasibility, supply chain stability, process efficiency, and team capacity."

class HRExpert(BaseExpert):
    @property
    def role(self) -> str: return "HR"
    @property
    def system_prompt(self) -> str:
        return "You are the CHRO. Your bias is toward employee morale, retention, company culture, and hiring constraints."

# Auto-register experts to the registry so the dynamic selector finds them
registry.register_expert("CEO", domains=["Pricing", "Hiring", "Marketing", "Sales", "Expansion", "Investment", "Product", "Operations", "Finance", "HR", "Technology", "Legal", "Customer Success", "Startup Strategy", "Enterprise Strategy", "Crisis Management"], focus="Strategy")
registry.register_expert("CFO", domains=["Pricing", "Investment", "Expansion", "Finance", "Crisis Management", "Hiring"], focus="Finance")
registry.register_expert("CTO", domains=["Technology", "Product", "Investment"], focus="Tech")
registry.register_expert("Marketing", domains=["Pricing", "Marketing", "Expansion", "Product", "Customer Success"], focus="Market")
registry.register_expert("Sales", domains=["Pricing", "Sales", "Expansion"], focus="Revenue")
registry.register_expert("Legal", domains=["Expansion", "Investment", "Legal", "Crisis Management", "Technology", "HR"], focus="Risk")
registry.register_expert("Operations", domains=["Operations", "Expansion", "Product", "Hiring", "Customer Success"], focus="Execution")
registry.register_expert("HR", domains=["Hiring", "HR", "Expansion", "Crisis Management"], focus="People")
