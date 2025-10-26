# SPDX-License-Identifier: MPL-2.0

import pytest
import os
import hashlib
import random
from red_teaming.reproducibility.protocol import ReproducibilityProtocol
from red_teaming.reproducibility.tamper_evidence import TamperEvidence
import logging

# Suppress logging during tests to avoid clutter
logging.getLogger().setLevel(logging.CRITICAL)

@pytest.fixture
def repro_protocol():
    return ReproducibilityProtocol()

@pytest.fixture
def tamper_evidence_tool():
    tool = TamperEvidence()
    tool.generate_key_pair()
    return tool

def test_set_global_seed_effect(repro_protocol):
    # Test that random sequences are reproducible
    seed = 123
    repro_protocol.set_global_seed(seed)
    rand_sequence1 = [random.random() for _ in range(5)]
    
    repro_protocol.set_global_seed(seed) # Reset with same seed
    rand_sequence2 = [random.random() for _ in range(5)]
    assert rand_sequence1 == rand_sequence2
    
    repro_protocol.set_global_seed(seed + 1) # Different seed
    rand_sequence3 = [random.random() for _ in range(5)]
    assert rand_sequence1 != rand_sequence3

def test_record_environment_produces_hash(repro_protocol):
    env_hash = repro_protocol.record_environment()
    assert isinstance(env_hash, str)
    assert len(env_hash) == 64 # SHA256 hash length

def test_tamper_evidence_sign_and_verify(tmp_path, tamper_evidence_tool):
    # Create a dummy file
    file_content = b"This is some test data."
    test_file = tmp_path / "test_report.txt"
    with open(test_file, 'wb') as f:
        f.write(file_content)
    
    # Sign the file
    signature = tamper_evidence_tool.sign_artifact(str(test_file))
    assert isinstance(signature, bytes)
    
    # Verify the signature with the public key
    is_valid = tamper_evidence_tool.verify_signature(str(test_file), signature, tamper_evidence_tool.public_key)
    assert is_valid == True

    # Tamper with the file
    with open(test_file, 'wb') as f:
        f.write(b"This is tampered data.")
    
    # Verify again, should fail
    is_tampered = tamper_evidence_tool.verify_signature(str(test_file), signature, tamper_evidence_tool.public_key)
    assert is_tampered == False

def test_tamper_evidence_file_not_found(tmp_path, tamper_evidence_tool):
    non_existent_file = tmp_path / "non_existent.txt"
    with pytest.raises(FileNotFoundError):
        tamper_evidence_tool.sign_artifact(str(non_existent_file))
    with pytest.raises(FileNotFoundError):
        tamper_evidence_tool.verify_signature(str(non_existent_file), b"dummy_sig", tamper_evidence_tool.public_key)

def test_record_version_control_info(repro_protocol):
    # This test will actually try to run 'git rev-parse HEAD'
    # If not in a git repo, it should return "N/A"
    git_info = repro_protocol.record_version_control_info()
    # Assert it's either a SHA1 hash or "N/A"
    assert len(git_info) == 40 or git_info == "N/A"
