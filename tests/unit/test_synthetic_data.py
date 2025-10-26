import pytest
from red_teaming.data.synthetic_data_generator import SyntheticDataGenerator
import re
import logging

# Suppress logging during tests to avoid clutter
logging.getLogger().setLevel(logging.CRITICAL)

@pytest.fixture
def generator():
    return SyntheticDataGenerator()

def test_generate_synthetic_text_preserve_patterns(generator):
    original_text = "This is a test sentence with some longer words like 'information' and 'development'."
    synthetic_text = generator.generate_synthetic_text(original_text, preserve_patterns=True)
    
    assert "[SYNTHETIC]" in synthetic_text
    assert len(synthetic_text.split()) == len(original_text.split()) # Check word count preservation
    # Check if some longer words are replaced (stochastic test, might fail rarely)
    original_long_words = [w for w in original_text.split() if len(w) > 5]
    synthetic_long_words = [w for w in synthetic_text.split() if len(w) > 5]
    
    # A more robust check would involve comparing character sets or specific patterns
    # For now, ensure it's not identical to original but has similar structure
    assert synthetic_text != original_text
    assert len(synthetic_text) == pytest.approx(len(original_text), rel=0.2) # Length should be similar

def test_generate_synthetic_text_no_preserve_patterns(generator):
    original_text = "Short text."
    synthetic_text = generator.generate_synthetic_text(original_text, preserve_patterns=False)
    assert "[SYNTHETIC_RANDOM]" in synthetic_text
    assert len(synthetic_text) == pytest.approx(len(original_text) + len(" [SYNTHETIC_RANDOM]")) # Should be close to original length + tag
    # Should primarily contain random characters
    assert re.fullmatch(r"[a-z0-9 ]+ \[SYNTHETIC_RANDOM\]", synthetic_text) is not None

def test_generate_synthetic_pii_email(generator):
    synthetic_email = generator.generate_synthetic_pii("email")
    assert "@example.com" in synthetic_email
    assert re.fullmatch(r"synthetic\.[0-9]{3}@example\.com", synthetic_email) is not None

def test_generate_synthetic_pii_name(generator):
    synthetic_name = generator.generate_synthetic_pii("name")
    assert "Synthetic User" in synthetic_name
    assert re.fullmatch(r"Synthetic User [0-9]{1,3}", synthetic_name) is not None

def test_generate_synthetic_pii_unknown_type(generator):
    synthetic_unknown = generator.generate_synthetic_pii("unknown_type")
    assert synthetic_unknown == "SYNTHETIC_PII"
