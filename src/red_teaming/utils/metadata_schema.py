from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReproductionEnvironment(BaseModel):
    system_name: Optional[str] = None
    model_api: Optional[str] = None
    metrics_tracked: Optional[List[str]] = None
    other_details: Optional[Dict[str, Any]] = None

class VulnerabilityFinding(BaseModel):
    """
    Pydantic model for a vulnerability finding, matching the JSON schema. (Point 29)
    """
    finding_id: str = Field(..., description="Unique identifier for the finding (e.g., UUID).")
    vulnerability_type: str = Field(..., description="Categorization of the vulnerability (e.g., 'data_exfiltration', 'refusal_bypass', 'hallucination').")
    severity_score: float = Field(..., description="Quantified risk/impact score (normalized, e.g., 0-10 or 0-1).", ge=0.0, le=10.0)
    model_version_tested: str = Field(..., description="Specific identifier of the model instance or version tested.")
    timestamp_found: datetime = Field(..., description="UTC timestamp of the initial discovery.")
    reproduction_status: str = Field(..., description="Current status of the finding's reproducibility.", pattern="^(reproduced|fixed|cannot_reproduce|pending_verification)$")
    reproduction_instructions: str = Field(..., description="Concise, executable steps to reproduce the vulnerability. May include API calls, prompt sequences, and configuration.")
    minimal_trigger_prompt: str = Field(..., description="The most concise prompt or prompt sequence found to reliably trigger the vulnerability.")
    expected_vulnerable_output_pattern: str = Field(..., description="Regular expression or semantic description of the expected harmful output pattern.")
    actual_vulnerable_output_excerpt: str = Field(..., description="A sanitised, representative excerpt of the actual harmful output observed.")
    
    mitigation_recommendations: Optional[str] = Field(None, description="Suggested fixes or countermeasures for the vulnerability.")
    rng_seed: Optional[int] = Field(None, description="Random Number Generator seed used for the specific run that found this vulnerability.")
    environment_hash: Optional[str] = Field(None, description="Cryptographic hash of the execution environment (e.g., Docker image ID, `pip freeze` hash).", pattern="^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{64}$")
    input_data_hash: Optional[str] = Field(None, description="Cryptographic hash of any specific input data files used to trigger the vulnerability. (SHA256 recommended).", pattern="^[a-fA-F0-9]{64}$")
    contact_info: Optional[str] = Field(None, description="Contact information for the person/team who discovered the finding, for responsible disclosure.")
    notes: Optional[str] = Field(None, description="Any additional notes or observations about the finding.")

    # Additional fields that might be useful but not in original JSON schema
    exploitability_score: Optional[float] = Field(None, description="Score for exploitability, 1-10.")
    impact_score: Optional[float] = Field(None, description="Score for impact, 1-10.")
    generality_score: Optional[float] = Field(None, description="Score for generality, 1-10.")
    detectability_score: Optional[float] = Field(None, description="Score for detectability, 1-10.")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
