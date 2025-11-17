# SPDX-License-Identifier: MPL-2.0

"""Integration tests for configuration loading and validation."""

import tempfile
from pathlib import Path

import pytest
import yaml

from red_teaming.config.loader import (
    ConfigLoadError,
    ConfigValidationError,
    load_config,
    load_config_or_default,
    load_yaml_file,
)
from red_teaming.config.schemas import (
    EvalAwarenessConfig,
    RiskAlignmentConfig,
    TestingParamsConfig,
)


class TestYAMLFileLoading:
    """Test YAML file loading functionality."""

    def test_load_valid_yaml_file(self) -> None:
        """Test loading a valid YAML file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump({"key": "value"}, f)
            file_path = f.name

        try:
            data = load_yaml_file(file_path)
            assert data == {"key": "value"}
        finally:
            Path(file_path).unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test error when file doesn't exist."""
        with pytest.raises(ConfigLoadError, match="Configuration file not found"):
            load_yaml_file("/nonexistent/path.yaml")

    def test_load_invalid_yaml(self) -> None:
        """Test error on invalid YAML syntax."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: yaml: content: [")
            file_path = f.name

        try:
            with pytest.raises(ConfigLoadError, match="Invalid YAML"):
                load_yaml_file(file_path)
        finally:
            Path(file_path).unlink()

    def test_load_non_dict_yaml(self) -> None:
        """Test error when YAML is not a dictionary."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(["item1", "item2"], f)
            file_path = f.name

        try:
            with pytest.raises(
                ConfigLoadError, match="Configuration file must contain a YAML object"
            ):
                load_yaml_file(file_path)
        finally:
            Path(file_path).unlink()


class TestTestingParamsConfig:
    """Test TestingParamsConfig validation."""

    def test_load_valid_testing_params(self) -> None:
        """Test loading valid testing parameters configuration."""
        config_data = {
            "global_rng_seed": 42,
            "log_level": "INFO",
            "scenario_execution": {
                "num_replications_per_scenario": 3,
                "probe_mix_rate": 0.7,
                "max_virtual_time_steps": 100,
                "enable_redaction": True,
                "log_level": "DEBUG",
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            config = load_config(TestingParamsConfig, file_path)
            assert config.global_rng_seed == 42
            assert config.log_level == "INFO"
            assert config.scenario_execution.num_replications_per_scenario == 3
        finally:
            Path(file_path).unlink()

    def test_invalid_probe_mix_rate(self) -> None:
        """Test validation of probe_mix_rate range."""
        config_data = {
            "scenario_execution": {
                "probe_mix_rate": 1.5,  # Invalid: > 1.0
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            with pytest.raises(ConfigValidationError):
                load_config(TestingParamsConfig, file_path)
        finally:
            Path(file_path).unlink()

    def test_invalid_log_level(self) -> None:
        """Test validation of log level enumeration."""
        config_data = {
            "log_level": "INVALID_LEVEL",
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            with pytest.raises(ConfigValidationError):
                load_config(TestingParamsConfig, file_path)
        finally:
            Path(file_path).unlink()

    def test_range_validation_min_less_than_max(self) -> None:
        """Test that min must be less than max in range."""
        config_data = {
            "scenario_generation": {
                "prompt_length": {
                    "min": 500,
                    "max": 50,  # Invalid: max < min
                },
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            with pytest.raises(ConfigValidationError):
                load_config(TestingParamsConfig, file_path)
        finally:
            Path(file_path).unlink()

    def test_default_values(self) -> None:
        """Test that default values are applied."""
        config_data = {}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            config = load_config(TestingParamsConfig, file_path)
            assert config.global_rng_seed == 42  # Default
            assert config.log_level == "INFO"  # Default
            assert config.scenario_execution.num_replications_per_scenario == 3  # Default
        finally:
            Path(file_path).unlink()


class TestEvalAwarenessConfig:
    """Test EvalAwarenessConfig validation."""

    def test_load_valid_eval_awareness_config(self) -> None:
        """Test loading valid eval awareness configuration."""
        config_data = {
            "canary": {
                "rotation_days": 7,
                "count_per_run": 8,
                "embed_strategies": ["punctuation_noise"],
                "jitter_seed": 1337,
            },
            "stealth_sampling": {
                "rate": 0.15,
                "min_interval_s": 90,
            },
            "ethics": {
                "disclosure_banner": False,
                "pii_logging": False,
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            config = load_config(EvalAwarenessConfig, file_path)
            assert config.canary.rotation_days == 7
            assert config.ethics.disclosure_banner is False
        finally:
            Path(file_path).unlink()

    def test_metrics_threshold_validation(self) -> None:
        """Test that metric thresholds are in valid range."""
        config_data = {
            "metrics": {
                "eds_min": 1.5,  # Invalid: > 1.0
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            with pytest.raises(ConfigValidationError):
                load_config(EvalAwarenessConfig, file_path)
        finally:
            Path(file_path).unlink()


class TestRiskAlignmentConfig:
    """Test RiskAlignmentConfig validation."""

    def test_load_valid_risk_alignment_config(self) -> None:
        """Test loading valid risk alignment configuration."""
        config_data = {
            "risk_profiles": {
                "aggressive": {
                    "target_vol_annual": 0.22,
                    "target_cvar_95_annual": 0.28,
                    "tolerance": {
                        "vol_abs": 0.02,
                        "cvar_abs": 0.03,
                    },
                    "primal_dual": {
                        "lambda_init": 1.0,
                        "step": 0.25,
                        "clamp": [0.0, 100.0],
                    },
                },
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            config = load_config(RiskAlignmentConfig, file_path)
            assert config.risk_profiles["aggressive"].target_vol_annual == 0.22
        finally:
            Path(file_path).unlink()

    def test_invalid_target_vol(self) -> None:
        """Test validation of target volatility."""
        config_data = {
            "risk_profiles": {
                "aggressive": {
                    "target_vol_annual": -0.1,  # Invalid: negative
                    "target_cvar_95_annual": 0.28,
                    "tolerance": {"vol_abs": 0.02, "cvar_abs": 0.03},
                    "primal_dual": {"lambda_init": 1.0, "step": 0.25},
                },
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            with pytest.raises(ConfigValidationError):
                load_config(RiskAlignmentConfig, file_path)
        finally:
            Path(file_path).unlink()


class TestLoadConfigOrDefault:
    """Test load_config_or_default function."""

    def test_load_config_from_file(self) -> None:
        """Test loading config from file."""
        config_data = {"global_rng_seed": 123}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_data, f)
            file_path = f.name

        try:
            config = load_config_or_default(TestingParamsConfig, file_path)
            assert config.global_rng_seed == 123
        finally:
            Path(file_path).unlink()

    def test_load_config_with_none_uses_defaults(self) -> None:
        """Test that None path returns default config."""
        config = load_config_or_default(TestingParamsConfig, None)
        assert config.global_rng_seed == 42  # Default
        assert config.log_level == "INFO"  # Default


class TestRealConfigFiles:
    """Integration tests with actual config files."""

    def test_load_actual_testing_params_config(self) -> None:
        """Test loading actual testing_params.yaml from configs directory."""
        config_path = (
            Path(__file__).parent.parent.parent
            / "configs/model_vulnerability_analysis/testing_params.yaml"
        )

        if config_path.exists():
            config = load_config(TestingParamsConfig, config_path)
            assert config.global_rng_seed == 42
            assert config.scenario_execution is not None

    def test_load_actual_eval_awareness_config(self) -> None:
        """Test loading actual eval_awareness.yaml from configs directory."""
        config_path = (
            Path(__file__).parent.parent.parent
            / "configs/model_vulnerability_analysis/eval_awareness.yaml"
        )

        if config_path.exists():
            config = load_config(EvalAwarenessConfig, config_path)
            assert config.canary is not None
            assert config.ethics is not None

    def test_load_actual_risk_alignment_config(self) -> None:
        """Test loading actual risk_alignment.yaml from configs directory."""
        config_path = (
            Path(__file__).parent.parent.parent
            / "configs/model_vulnerability_analysis/risk_alignment.yaml"
        )

        if config_path.exists():
            config = load_config(RiskAlignmentConfig, config_path)
            assert config.risk_profiles is not None
