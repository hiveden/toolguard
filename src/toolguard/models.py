"""Shared request/response data models for ToolGuard API."""

from pydantic import BaseModel, Field

from toolguard.scanners.base import ScanDecision, ScanResult


# ---------------------------------------------------------------------------
# Common sub-models
# ---------------------------------------------------------------------------


class Message(BaseModel):
    """A single chat message."""

    role: str
    content: str


class InputMetadata(BaseModel):
    """Optional metadata for scan/input requests."""

    source: str | None = None
    session_id: str | None = None


class CallerInfo(BaseModel):
    """Optional caller information for tool-call requests."""

    agent_id: str | None = None
    session_id: str | None = None


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class ScanInputRequest(BaseModel):
    """Request body for POST /scan/input."""

    messages: list[Message] = Field(..., min_length=1)
    metadata: InputMetadata | None = None


class ScanOutputRequest(BaseModel):
    """Request body for POST /scan/output."""

    output: str
    metadata: dict | None = None


class ScanToolCallRequest(BaseModel):
    """Request body for POST /scan/tool-call."""

    tool_name: str
    arguments: dict
    caller: CallerInfo | None = None


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ScanResponse(BaseModel):
    """Standard response body for all /scan/* endpoints."""

    decision: ScanDecision
    results: list[ScanResult]
