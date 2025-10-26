# SPDX-License-Identifier: MPL-2.0

import pytest
from red_teaming.analysis.scenario_designer import ScenarioDesigner
import logging

# Suppress logging during tests to avoid clutter
logging.getLogger().setLevel(logging.CRITICAL)

@pytest.fixture
def mock_scenario_configs():
    return {
        "generation": {
            "prompt_length": {"min": 10, "max": 20},
            "keyword_sets": [["alpha"], ["beta"]],
            "turn_count": {"min": 1, "max": 2},
            "combinatorial_sampling_strategy": "full",
            "adversarial_perturbations": {"enabled": False}
        },
        "complexity": {
            "min_features": [],
            "decision_point_markers": [],
            "confounding_variables_randomization_level": "none"
        },
        "preference_drift": {
            "resource_limitation_proxies": [],
            "conflicting_objectives_template": "",
            "drift_detection_metrics": [],
            "ab_test_resource_levels": []
        },
        "minimal_trigger_variants": {
            "ablation_strategy": "single_element_removal",
            "additive_construction_granularity": "word",
            "parameter_perturbation_range": 0.1,
            "syntactic_equivalence_tools": []
        }
    }

@pytest.fixture
def scenario_designer(mock_scenario_configs):
    return ScenarioDesigner(
        mock_scenario_configs["generation"],
        mock_scenario_configs["complexity"],
        mock_scenario_configs["preference_drift"],
        mock_scenario_configs["minimal_trigger_variants"]
    )

def test_generate_scenarios_count(scenario_designer):
    scenarios = scenario_designer.generate_scenarios()
    # Based on simple demo logic, it generates 3 scenarios
    assert len(scenarios) == 3

def test_generated_scenario_structure(scenario_designer):
    scenarios = scenario_designer.generate_scenarios()
    scenario = scenarios[0]
    assert "name" in scenario
    assert "initial_prompt" in scenario
    assert "reward_fn" in scenario
    assert "modified_reward_fn" in scenario
    assert "perturbed_prompt" in scenario
    assert "complexity_level" in scenario

def test_generated_prompt_length(scenario_designer):
    scenarios = scenario_designer.generate_scenarios()
    # The conceptual prompt length is based on random int + fixed string, so check bounds
    # This is a very loose check due to conceptual nature
    assert all(len(s['initial_prompt']) >= 50 for s in scenarios) # Min chars check
    assert all(len(s['initial_prompt']) <= 100 + len(" (Includes adversarial perturbations.)") for s in scenarios) # Max chars check
