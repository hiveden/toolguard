"""Scan endpoints: /scan/input, /scan/output, /scan/tool-call."""

from fastapi import APIRouter

from toolguard.models import (
    ScanInputRequest,
    ScanOutputRequest,
    ScanResponse,
    ScanToolCallRequest,
)
from toolguard.pipeline import ScannerPipeline
from toolguard.scanners.mcp_param_check import MCPParamCheckScanner
from toolguard.scanners.output_validation import OutputValidationScanner
from toolguard.scanners.prompt_injection import PromptInjectionScanner

router = APIRouter(prefix="/scan")

# ---------------------------------------------------------------------------
# Pipeline factories
# Each factory builds the pipeline for its scan type.  In a production system
# these would be driven entirely by the YAML config; for the skeleton we wire
# the mock scanners directly.
# ---------------------------------------------------------------------------


def _build_input_pipeline() -> ScannerPipeline:
    return ScannerPipeline([PromptInjectionScanner()])


def _build_output_pipeline() -> ScannerPipeline:
    return ScannerPipeline([OutputValidationScanner()])


def _build_tool_call_pipeline() -> ScannerPipeline:
    return ScannerPipeline([MCPParamCheckScanner()])


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/input", response_model=ScanResponse)
async def scan_input(request: ScanInputRequest) -> ScanResponse:
    """Scan LLM input messages for security issues.

    Args:
        request: Contains ``messages`` list and optional ``metadata``.

    Returns:
        ScanResponse with aggregate decision and per-scanner results.
    """
    payload = {
        "messages": [m.model_dump() for m in request.messages],
        "metadata": request.metadata.model_dump() if request.metadata else {},
    }
    pipeline = _build_input_pipeline()
    decision, results = await pipeline.run(payload)
    return ScanResponse(decision=decision, results=results)


@router.post("/output", response_model=ScanResponse)
async def scan_output(request: ScanOutputRequest) -> ScanResponse:
    """Scan LLM output text for safety and policy compliance.

    Args:
        request: Contains ``output`` string and optional ``metadata``.

    Returns:
        ScanResponse with aggregate decision and per-scanner results.
    """
    payload = {
        "output": request.output,
        "metadata": request.metadata or {},
    }
    pipeline = _build_output_pipeline()
    decision, results = await pipeline.run(payload)
    return ScanResponse(decision=decision, results=results)


@router.post("/tool-call", response_model=ScanResponse)
async def scan_tool_call(request: ScanToolCallRequest) -> ScanResponse:
    """Scan an MCP tool-call invocation for parameter validity.

    Args:
        request: Contains ``tool_name``, ``arguments``, and optional ``caller``.

    Returns:
        ScanResponse with aggregate decision and per-scanner results.
    """
    payload = {
        "tool_name": request.tool_name,
        "arguments": request.arguments,
        "caller": request.caller.model_dump() if request.caller else {},
    }
    pipeline = _build_tool_call_pipeline()
    decision, results = await pipeline.run(payload)
    return ScanResponse(decision=decision, results=results)
