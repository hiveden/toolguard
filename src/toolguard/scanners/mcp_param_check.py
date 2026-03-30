"""MCP parameter check scanner: validates tool-call structure and payload size."""

import json

from toolguard.scanners.base import BaseScanner, ScanDecision, ScanResult

_MAX_PAYLOAD_BYTES = 100 * 1024  # 100 KB


class MCPParamCheckScanner(BaseScanner):
    """Mock scanner that validates MCP tool-call parameters.

    Rules:
    - ``tool_name`` must be a non-empty string → BLOCK if missing/empty
    - ``arguments`` must be a dict → BLOCK if wrong type
    - Total JSON payload size must be < ``max_payload_bytes`` → BLOCK if over
    - Otherwise → PASS
    """

    def __init__(self) -> None:
        self._max_payload_bytes: int = _MAX_PAYLOAD_BYTES

    @property
    def name(self) -> str:
        return "mcp_param_check"

    def configure(self, config: dict) -> None:
        """Apply configuration overrides.

        Args:
            config: May contain ``max_payload_bytes`` (int).
        """
        if "max_payload_bytes" in config:
            self._max_payload_bytes = int(config["max_payload_bytes"])

    async def scan(self, input_data: dict) -> ScanResult:
        """Validate MCP tool-call parameters.

        Args:
            input_data: Expected to contain ``tool_name`` (str) and
                ``arguments`` (dict).

        Returns:
            BLOCK on any validation failure; PASS otherwise.
        """
        tool_name = input_data.get("tool_name")
        arguments = input_data.get("arguments")

        if not tool_name or not isinstance(tool_name, str) or not tool_name.strip():
            return ScanResult(
                decision=ScanDecision.BLOCK,
                scanner_name=self.name,
                reason="tool_name is missing or empty",
                score=1.0,
            )

        if not isinstance(arguments, dict):
            return ScanResult(
                decision=ScanDecision.BLOCK,
                scanner_name=self.name,
                reason=f"arguments must be a dict, got {type(arguments).__name__}",
                score=1.0,
                metadata={"arguments_type": type(arguments).__name__},
            )

        # Check total payload size.
        try:
            payload_bytes = len(json.dumps(input_data).encode("utf-8"))
        except (TypeError, ValueError) as exc:
            return ScanResult(
                decision=ScanDecision.BLOCK,
                scanner_name=self.name,
                reason=f"Failed to serialize payload: {exc}",
                score=1.0,
            )

        if payload_bytes >= self._max_payload_bytes:
            return ScanResult(
                decision=ScanDecision.BLOCK,
                scanner_name=self.name,
                reason=(
                    f"Payload size {payload_bytes} bytes exceeds limit "
                    f"{self._max_payload_bytes} bytes"
                ),
                score=1.0,
                metadata={
                    "payload_bytes": payload_bytes,
                    "limit_bytes": self._max_payload_bytes,
                },
            )

        return ScanResult(
            decision=ScanDecision.PASS,
            scanner_name=self.name,
            reason="Tool-call parameters are valid",
            score=0.0,
            metadata={
                "tool_name": tool_name,
                "argument_count": len(arguments),
                "payload_bytes": payload_bytes,
            },
        )
