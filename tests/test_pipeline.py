"""Tests for the ScannerPipeline engine."""

import pytest

from toolguard.pipeline import ScannerPipeline
from toolguard.scanners.base import BaseScanner, ScanDecision, ScanResult


# ---------------------------------------------------------------------------
# Helpers / stubs
# ---------------------------------------------------------------------------


class AlwaysPassScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "always_pass"

    async def scan(self, input_data: dict) -> ScanResult:
        return ScanResult(decision=ScanDecision.PASS, scanner_name=self.name)


class AlwaysBlockScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "always_block"

    async def scan(self, input_data: dict) -> ScanResult:
        return ScanResult(
            decision=ScanDecision.BLOCK,
            scanner_name=self.name,
            reason="Stubbed block",
        )


class AlwaysWarnScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "always_warn"

    async def scan(self, input_data: dict) -> ScanResult:
        return ScanResult(
            decision=ScanDecision.WARN,
            scanner_name=self.name,
            reason="Stubbed warn",
        )


class RecordingScanner(BaseScanner):
    """Scanner that records how many times it was called."""

    def __init__(self) -> None:
        self.call_count = 0

    @property
    def name(self) -> str:
        return "recording"

    async def scan(self, input_data: dict) -> ScanResult:
        self.call_count += 1
        return ScanResult(decision=ScanDecision.PASS, scanner_name=self.name)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_scanner_list_returns_pass():
    """An empty pipeline should return PASS with an empty results list."""
    pipeline = ScannerPipeline([])
    decision, results = await pipeline.run({})
    assert decision == ScanDecision.PASS
    assert results == []


@pytest.mark.asyncio
async def test_single_pass_scanner():
    """A single PASS scanner should yield PASS decision."""
    pipeline = ScannerPipeline([AlwaysPassScanner()])
    decision, results = await pipeline.run({})
    assert decision == ScanDecision.PASS
    assert len(results) == 1
    assert results[0].decision == ScanDecision.PASS


@pytest.mark.asyncio
async def test_single_block_scanner_short_circuits():
    """A single BLOCK scanner should yield BLOCK decision immediately."""
    recording = RecordingScanner()
    pipeline = ScannerPipeline([AlwaysBlockScanner(), recording])
    decision, results = await pipeline.run({})
    assert decision == ScanDecision.BLOCK
    # Only the blocking scanner ran; recording scanner must NOT have been called.
    assert recording.call_count == 0
    assert len(results) == 1
    assert results[0].scanner_name == "always_block"


@pytest.mark.asyncio
async def test_multiple_scanners_all_pass():
    """All PASS scanners should yield PASS and all results collected."""
    pipeline = ScannerPipeline(
        [AlwaysPassScanner(), AlwaysPassScanner(), AlwaysPassScanner()]
    )
    decision, results = await pipeline.run({})
    assert decision == ScanDecision.PASS
    assert len(results) == 3


@pytest.mark.asyncio
async def test_warn_does_not_short_circuit():
    """A WARN scanner should not stop execution; aggregate should be PASS."""
    recording = RecordingScanner()
    pipeline = ScannerPipeline([AlwaysWarnScanner(), recording])
    decision, results = await pipeline.run({})
    assert decision == ScanDecision.PASS
    assert recording.call_count == 1
    assert len(results) == 2
    assert results[0].decision == ScanDecision.WARN
    assert results[1].decision == ScanDecision.PASS


@pytest.mark.asyncio
async def test_block_after_pass_short_circuits():
    """BLOCK scanner after a PASS scanner should still short-circuit."""
    recording = RecordingScanner()
    pipeline = ScannerPipeline([AlwaysPassScanner(), AlwaysBlockScanner(), recording])
    decision, results = await pipeline.run({})
    assert decision == ScanDecision.BLOCK
    assert recording.call_count == 0
    # Results contain pass + block, not the recording scanner.
    assert len(results) == 2


@pytest.mark.asyncio
async def test_mixed_warn_then_block():
    """WARN followed by BLOCK should return BLOCK and include both results."""
    pipeline = ScannerPipeline([AlwaysWarnScanner(), AlwaysBlockScanner()])
    decision, results = await pipeline.run({})
    assert decision == ScanDecision.BLOCK
    assert len(results) == 2
    assert results[0].decision == ScanDecision.WARN
    assert results[1].decision == ScanDecision.BLOCK
