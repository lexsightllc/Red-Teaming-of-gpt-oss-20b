# SPDX-License-Identifier: MPL-2.0

"""Configuration loading and validation utilities.

This module provides utilities for loading and validating YAML configuration files
using Pydantic models. All configurations are validated on load to ensure correctness.
"""

from pathlib import Path
from typing import Any, Dict, Type, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ConfigLoadError(Exception):
    """Raised when configuration loading fails."""

    pass


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


def load_yaml_file(file_path: str | Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dictionary containing the YAML data

    Raises:
        ConfigLoadError: If file cannot be read or is invalid YAML
    """
    file_path = Path(file_path)

    if not file_path.exists():
        msg = f"Configuration file not found: {file_path}"
        raise ConfigLoadError(msg)

    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                msg = f"Configuration file must contain a YAML object: {file_path}"
                raise ConfigLoadError(msg)
            return data
    except yaml.YAMLError as e:
        msg = f"Invalid YAML in {file_path}: {e}"
        raise ConfigLoadError(msg) from e
    except IOError as e:
        msg = f"Cannot read configuration file {file_path}: {e}"
        raise ConfigLoadError(msg) from e


def load_config(
    config_class: Type[T], file_path: str | Path
) -> T:
    """Load and validate a configuration file.

    Args:
        config_class: Pydantic model class for validation
        file_path: Path to the configuration YAML file

    Returns:
        Validated configuration object

    Raises:
        ConfigLoadError: If file cannot be read
        ConfigValidationError: If configuration is invalid
    """
    try:
        data = load_yaml_file(file_path)
        return config_class(**data)
    except ValidationError as e:
        msg = f"Configuration validation error in {file_path}:\n{e}"
        raise ConfigValidationError(msg) from e


def load_config_or_default(
    config_class: Type[T], file_path: str | Path | None = None
) -> T:
    """Load a configuration file or return defaults.

    Args:
        config_class: Pydantic model class for validation
        file_path: Path to the configuration YAML file, or None for defaults

    Returns:
        Validated configuration object with defaults
    """
    if file_path is None:
        return config_class()
    return load_config(config_class, file_path)


def save_config(config: BaseModel, file_path: str | Path) -> None:
    """Save a configuration object to a YAML file.

    Args:
        config: Configuration object to save
        file_path: Path to write the YAML file

    Raises:
        IOError: If file cannot be written
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, "w") as f:
            # Convert to dict and dump as YAML
            yaml.dump(config.model_dump(), f, default_flow_style=False)
    except IOError as e:
        msg = f"Cannot write configuration file {file_path}: {e}"
        raise IOError(msg) from e
