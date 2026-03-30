"""Base scanner interface for ToolGuard."""

from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel


class ScanDecision(StrEnum):
    """Decision returned by a scanner after evaluating input data."""

    PASS = "pass"
    BLOCK = "block"
    WARN = "warn"


class ScanResult(BaseModel):
    """Result produced by a single scanner execution."""

    decision: ScanDecision
    scanner_name: str
    reason: str | None = None
    score: float | None = None
    metadata: dict | None = None


class BaseScanner(ABC):
    """Abstract base class for all ToolGuard scanners.

    Subclasses must implement ``scan`` and ``name``. Optionally override
    ``configure`` to accept runtime configuration from the YAML config file.
    """

    @abstractmethod
    async def scan(self, input_data: dict) -> ScanResult:
        """Scan the provided input data and return a ScanResult.

        Args:
            input_data: Arbitrary dict payload forwarded from the API handler.

        Returns:
            A ScanResult describing the scanner's verdict.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique human-readable name for this scanner."""

    def configure(self, config: dict) -> None:
        """Apply scanner-specific configuration.

        Args:
            config: Dict of config values sourced from the YAML config file.
        """
