import time
from backend.repositories.event_repo import EventRepository

repo = EventRepository()

mock_events = [
    {"event_type": "SYSTEM_START", "message": "NEOVERSE OS Initialized Successfully"},
    {"event_type": "API_CONNECTION", "message": "Google Gemini API connected and verified."},
    {"event_type": "PLUGIN_LOAD", "message": "Loaded 4 core MCP plugins."},
    {"event_type": "MEMORY_SYNC", "message": "Synchronized 5 memories with Knowledge Base."},
    {"event_type": "AGENT_READY", "message": "Debate Agent spawned and awaiting instructions."},
]

print("Populating Event Database...")
for e in mock_events:
    repo.log_event(event_type=e["event_type"], message=e["message"])
    time.sleep(0.1)

print("Successfully injected events!")
