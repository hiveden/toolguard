"""Configuration loading for ToolGuard.

Loads toolguard.yaml via PyYAML and validates the result with Pydantic Settings.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "toolguard.yaml"


class ScannerConfig(BaseModel):
    """Configuration for a single scanner."""

    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class ScannerGroupConfig(BaseModel):
    """Scanner configuration grouped by scan type."""

    input: list[str] = Field(default_factory=list)
    output: list[str] = Field(default_factory=list)
    tool_call: list[str] = Field(default_factory=list)


class ServerConfig(BaseModel):
    """HTTP server settings."""

    host: str = "0.0.0.0"
    port: int = 8400
    log_level: str = "info"


class ToolGuardConfig(BaseModel):
    """Root configuration model for ToolGuard."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    scanners: ScannerGroupConfig = Field(default_factory=ScannerGroupConfig)
    scanner_configs: dict[str, ScannerConfig] = Field(default_factory=dict)


class Settings(BaseSettings):
    """Application settings with optional YAML config file overlay."""

    model_config = SettingsConfigDict(env_prefix="TOOLGUARD_", env_nested_delimiter="__")

    config_path: str = str(_DEFAULT_CONFIG_PATH)

    def load(self) -> ToolGuardConfig:
        """Load and validate the YAML configuration file.

        Returns:
            Parsed and validated ToolGuardConfig instance.
        """
        path = Path(self.config_path)
        if not path.exists():
            logger.warning("Config file not found at %s, using defaults.", path)
            return ToolGuardConfig()

        with path.open("r", encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}

        logger.info("Loaded configuration from %s", path)
        return ToolGuardConfig.model_validate(raw)


# Module-level singleton loaded on import.
settings = Settings()
app_config: ToolGuardConfig = settings.load()
