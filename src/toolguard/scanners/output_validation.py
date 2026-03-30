"""Output validation scanner: checks LLM output for basic sanity constraints."""

from toolguard.scanners.base import BaseScanner, ScanDecision, ScanResult

_MAX_OUTPUT_LENGTH = 50_000  # characters


class OutputValidationScanner(BaseScanner):
    """Mock scanner that validates LLM output length and non-emptiness.

    - Empty string → BLOCK
    - Length >= ``max_output_length`` → WARN
    - Otherwise → PASS
    """

    def __init__(self) -> None:
        self._max_output_length: int = _MAX_OUTPUT_LENGTH

    @property
    def name(self) -> str:
        return "output_validation"

    def configure(self, config: dict) -> None:
        """Apply configuration overrides.

        Args:
            config: May contain ``max_output_length`` (int).
        """
        if "max_output_length" in config:
            self._max_output_length = int(config["max_output_length"])

    async def scan(self, input_data: dict) -> ScanResult:
        """Validate the output field in input_data.

        Args:
            input_data: Expected to contain an ``output`` key (str).

        Returns:
            BLOCK if empty, WARN if over length limit, PASS otherwise.
        """
        output: str = input_data.get("output", "")

        if not output or not output.strip():
            return ScanResult(
                decision=ScanDecision.BLOCK,
                scanner_name=self.name,
                reason="Output is empty",
                score=1.0,
            )

        if len(output) >= self._max_output_length:
            return ScanResult(
                decision=ScanDecision.WARN,
                scanner_name=self.name,
                reason=(
                    f"Output length {len(output)} exceeds limit {self._max_output_length}"
                ),
                score=0.6,
                metadata={"output_length": len(output), "limit": self._max_output_length},
            )

        return ScanResult(
            decision=ScanDecision.PASS,
            scanner_name=self.name,
            reason="Output passes length validation",
            score=0.0,
            metadata={"output_length": len(output)},
        )
