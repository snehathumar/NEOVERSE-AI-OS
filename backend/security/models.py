from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Organization(BaseModel):
    org_id: str
    name: str
    settings: Dict[str, Any] = Field(default_factory=dict)
    policies: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True

class User(BaseModel):
    user_id: str
    email: str
    org_id: str
    roles: List[str]
    active: bool = True

class Permission(BaseModel):
    resource: str
    action: str
    conditions: Dict[str, Any] = Field(default_factory=dict)

class Role(BaseModel):
    role_id: str
    name: str
    permissions: List[Permission]

class Session(BaseModel):
    session_id: str
    user_id: str
    org_id: str
    expires_at: str
    is_revoked: bool = False
    device_info: str = "Unknown"

class SecurityContext(BaseModel):
    org_id: str
    user_id: str
    session_id: str
    roles: List[str]
    is_judge_mode: bool = False

class AuditLog(BaseModel):
    log_id: str
    timestamp: str
    org_id: str
    user_id: str
    session_id: str
    action: str
    resource: str
    status: str # SUCCESS, DENIED, FAILED
    details: Dict[str, Any]
