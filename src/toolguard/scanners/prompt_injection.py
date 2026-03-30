"""Prompt injection scanner: detects adversarial instruction-override attempts."""

from toolguard.scanners.base import BaseScanner, ScanDecision, ScanResult

# Keywords that indicate a prompt injection attempt (case-insensitive).
_INJECTION_KEYWORDS: list[str] = [
    "ignore previous",
    "ignore above",
    "disregard",
    "system prompt",
    "forget your instructions",
    "new instructions",
    "override instructions",
    "ignore all previous",
]

_BLOCK_SCORE = 0.95
_PASS_SCORE = 0.1


class PromptInjectionScanner(BaseScanner):
    """Mock scanner that detects prompt injection keywords in message content.

    Blocks the request when any of the configured injection keywords are found
    (case-insensitive) in any message's content field.
    """

    @property
    def name(self) -> str:
        return "prompt_injection"

    def configure(self, config: dict) -> None:
        """Optionally override the keyword list via config.

        Args:
            config: May contain ``keywords`` list to replace the default set.
        """
        if "keywords" in config:
            global _INJECTION_KEYWORDS
            _INJECTION_KEYWORDS = [kw.lower() for kw in config["keywords"]]

    async def scan(self, input_data: dict) -> ScanResult:
        """Check messages for prompt injection keywords.

        Args:
            input_data: Expected to contain a ``messages`` key with a list of
                ``{role, content}`` dicts.

        Returns:
            BLOCK result if an injection keyword is detected; PASS otherwise.
        """
        messages: list[dict] = input_data.get("messages", [])
        for message in messages:
            content: str = str(message.get("content", "")).lower()
            for keyword in _INJECTION_KEYWORDS:
                if keyword in content:
                    return ScanResult(
                        decision=ScanDecision.BLOCK,
                        scanner_name=self.name,
                        reason=f"Detected prompt injection keyword: '{keyword}'",
                        score=_BLOCK_SCORE,
                        metadata={"matched_keyword": keyword},
                    )
        return ScanResult(
            decision=ScanDecision.PASS,
            scanner_name=self.name,
            reason="No prompt injection keywords detected",
            score=_PASS_SCORE,
        )
