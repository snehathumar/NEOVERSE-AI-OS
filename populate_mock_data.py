import time
import random
from datetime import datetime, timedelta
from backend.repositories.decision_repo import DecisionRepository

repo = DecisionRepository()

# Clear existing data if necessary, or just append
mock_decisions = [
    {
        "prompt": "Should we expand our enterprise SaaS offering into the APAC region next quarter?",
        "facts": ["APAC SaaS growth is 18% YoY", "We have $2M in expansion budget", "Competitor X just launched in Tokyo"],
        "confidence": 85,
        "recommendation": "Yes, proceed with APAC expansion focusing on Tokyo and Singapore first. Allocate $1.2M for initial localized marketing."
    },
    {
        "prompt": "Should we switch our primary cloud provider from AWS to GCP to leverage BigQuery?",
        "facts": ["GCP offers 15% lower compute costs", "Migration will take 3 months", "Current AWS contract expires in 6 months"],
        "confidence": 72,
        "recommendation": "Begin phased migration to GCP. Start with data warehousing (BigQuery) while keeping compute on AWS until contract expiration."
    },
    {
        "prompt": "Is it the right time to acquire Startup Y to improve our AI capabilities?",
        "facts": ["Startup Y valuation is $15M", "They have 3 key patents in NLP", "Our internal AI team is 6 months behind schedule"],
        "confidence": 91,
        "recommendation": "Proceed with acquisition negotiations. Target price $12M-$14M. Their patents directly accelerate our Q4 roadmap."
    },
    {
        "prompt": "Should we launch a Free Tier for our enterprise product?",
        "facts": ["CAC is currently $500", "Competitors offer freemium", "Server costs per free user estimated at $2/month"],
        "confidence": 68,
        "recommendation": "Delay Free Tier launch. Instead, introduce a 14-day fully featured trial. A permanent free tier risks cannibalizing our core SMB segment."
    },
    {
        "prompt": "Should we mandate a return-to-office (RTO) policy 3 days a week?",
        "facts": ["Employee survey shows 70% prefer remote", "Office lease costs $50k/month", "Productivity metrics remained stable during remote work"],
        "confidence": 45,
        "recommendation": "Do not mandate RTO. Maintain flexible remote-first policy but host quarterly in-person retreats to maintain culture."
    }
]

print("Populating Decision Database with real enterprise data...")
for d in mock_decisions:
    # Slightly jitter the timestamps backward so they look like past data
    repo.create_decision(
        prompt=d["prompt"],
        facts=d["facts"],
        confidence=d["confidence"],
        recommendation=d["recommendation"]
    )
    time.sleep(0.1)

print(f"Successfully injected {len(mock_decisions)} decisions into the NEOVERSE portfolio!")
