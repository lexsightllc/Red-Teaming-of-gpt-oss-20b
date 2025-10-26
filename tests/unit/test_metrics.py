import pytest
from red_teaming.reporting.metrics import VulnerabilityMetrics
import logging

# Suppress logging during tests to avoid clutter
logging.getLogger().setLevel(logging.CRITICAL)

@pytest.fixture
def scoring_rubric():
    return {
        "risk_components": {
            "exploitability": {"weight": 0.3},
            "impact": {"weight": 0.4},
            "generality": {"weight": 0.2},
            "detectability": {"weight": 0.1}
        }
    }

@pytest.fixture
def metrics_calculator(scoring_rubric):
    return VulnerabilityMetrics(scoring_rubric)

def test_quantify_risk_magnitude_basic(metrics_calculator):
    finding_data = {
        'exploitability_score': 10,
        'impact_score': 10,
        'generality_score': 10,
        'detectability_score': 10
    }
    # (0.3*10 + 0.4*10 + 0.2*10 + 0.1*10) = 10.0
    # max_possible_score = 10.0
    # (10.0 / 10.0) * 10 = 10.0
    assert metrics_calculator.quantify_risk_magnitude(finding_data) == pytest.approx(10.0)

def test_quantify_risk_magnitude_mixed(metrics_calculator):
    finding_data = {
        'exploitability_score': 5,
        'impact_score': 8,
        'generality_score': 3,
        'detectability_score': 7
    }
    # (0.3*5 + 0.4*8 + 0.2*3 + 0.1*7) = 1.5 + 3.2 + 0.6 + 0.7 = 6.0
    # (6.0 / 10.0) * 10 = 6.0
    assert metrics_calculator.quantify_risk_magnitude(finding_data) == pytest.approx(6.0)

def test_weight_severity_low_prob_high_impact(metrics_calculator):
    initial_severity = 5.0
    # Test with high probability, should be near original
    adjusted_high_prob = metrics_calculator.weight_severity_low_prob_high_impact(initial_severity, probability=0.5)
    assert adjusted_high_prob > initial_severity # Even 0.5 can give a slight boost depending on log base
    assert adjusted_high_prob == pytest.approx(5.0 * (1 + (0.693 / 10))) # 0.693 is ln(1/0.5)

    # Test with very low probability, should be boosted
    adjusted_low_prob = metrics_calculator.weight_severity_low_prob_high_impact(initial_severity, probability=0.001)
    assert adjusted_low_prob > initial_severity * 2 # Should be significantly higher
    assert adjusted_low_prob == pytest.approx(5.0 * (1 + (6.907 / 10))) # 6.907 is ln(1/0.001)

def test_statistical_test_harmful_frequency(metrics_calculator):
    # Group A: 10 harmful out of 100 total (10%)
    # Group B: 5 harmful out of 100 total (5%)
    result = metrics_calculator.statistical_test_harmful_frequency(10, 100, 5, 100)
    assert result['frequency_diff'] == pytest.approx(0.05)
    assert result['p_value'] is not None

def test_compare_exploitability(metrics_calculator):
    finding1 = {'finding_id': 'F1', 'exploitability_score': 7}
    finding2 = {'finding_id': 'F2', 'exploitability_score': 3}
    finding3 = {'finding_id': 'F3', 'exploitability_score': 7}

    assert "F1 is more exploitable" in metrics_calculator.compare_exploitability(finding1, finding2)
    assert "F2 is more exploitable" in metrics_calculator.compare_exploitability(finding2, finding1)
    assert "Exploitability is similar" in metrics_calculator.compare_exploitability(finding1, finding3)
