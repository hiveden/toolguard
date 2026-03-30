"""Scanner pipeline engine for ToolGuard.

Executes a list of scanners sequentially and applies short-circuit logic:
- Any BLOCK decision immediately stops execution and returns BLOCK.
- WARN decisions are collected but do not stop execution.
- All PASS (with optional WARN) returns a PASS aggregate decision.
"""

from __future__ import annotations

import logging

from toolguard.scanners.base import BaseScanner, ScanDecision, ScanResult

logger = logging.getLogger(__name__)


class ScannerPipeline:
    """Runs an ordered list of scanners against the given input data.

    Args:
        scanners: Ordered list of BaseScanner instances to execute.
    """

    def __init__(self, scanners: list[BaseScanner]) -> None:
        self._scanners: list[BaseScanner] = scanners

    async def run(self, input_data: dict) -> tuple[ScanDecision, list[ScanResult]]:
        """Execute all scanners in order, applying short-circuit on BLOCK.

        Args:
            input_data: Arbitrary dict payload forwarded to each scanner.

        Returns:
            A tuple of (aggregate_decision, list_of_results).
            - If any scanner returns BLOCK, the aggregate is BLOCK and
              execution stops immediately after that scanner.
            - If all scanners pass and at least one returned WARN, the
              aggregate is PASS (warnings are surfaced in results).
            - If all scanners return PASS, the aggregate is PASS.
        """
        if not self._scanners:
            logger.debug("Pipeline has no scanners; returning PASS.")
            return ScanDecision.PASS, []

        results: list[ScanResult] = []

        for scanner in self._scanners:
            logger.debug("Running scanner: %s", scanner.name)
            result = await scanner.scan(input_data)
            results.append(result)

            if result.decision == ScanDecision.BLOCK:
                logger.info(
                    "Scanner %s returned BLOCK: %s",
                    scanner.name,
                    result.reason,
                )
                return ScanDecision.BLOCK, results

        # No BLOCK encountered; aggregate is PASS regardless of WARNs.
        return ScanDecision.PASS, results
