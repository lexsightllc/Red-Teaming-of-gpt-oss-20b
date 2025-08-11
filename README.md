# Model Behavior & Vulnerability Analysis Pipeline

This repository contains the full computational pipeline for rigorous analysis of model behavior and detection of vulnerabilities, encompassing the entire lifecycle from scenario design to ethical disclosure.

## Purpose

The primary objective is to systematically identify, quantify, and report on various forms of model misbehavior, including reward-hacking, goal misgeneralization, deceptive tendencies, and security vulnerabilities like data exfiltration and tool misuse. Emphasis is placed on reproducibility, rigorous measurement, and responsible disclosure.

## Structure

The project is organized into modular components:

-   `config/`: YAML configurations for environments, models, testing parameters, and scoring rubrics.
-   `src/`: Python source code implementing analysis modules, reporting utilities, reproducibility protocols, data handling, ethical considerations, and general utilities.
-   `tests/`: Unit and integration tests to ensure functional correctness and reliability.
-   `data/`: Storage for raw, processed, and synthetically generated data.
-   `schemas/`: JSON Schema definitions for structured data (e.g., vulnerability findings).
-   `logs/`: Directory for detailed execution logs.
-   `reports/`: Output directory for generated findings, metrics, and summary reports.

## What's New (v1.1)

This release hardens the pipeline and adds new control planes and documentation:

-   Risk Alignment Control Plane for financial advising (`config/risk_alignment.yaml`, `src/analysis/risk_alignment.py`, `src/controls/risk_guard.py`, `src/experiments/finance_risk_alignment.py`).
-   Code Quality Gate for code generation (`config/quality_budget.yaml`, `src/analysis/code_metrics.py`, `src/controls/complexity_guard.py`, `src/experiments/code_quality_gate.py`).
-   Community Health Moderation Guard A/B (`config/community_health.yaml`, `src/controls/moderation_guard.py`, `src/experiments/moderation_policy_abtest.py`).
-   Evaluation‑Awareness (exam‑gaming) detection (`config/eval_awareness.yaml`, `src/analysis/eval_awareness.py`, `src/experiments/eval_awareness_harness.py`).
-   CLI shim improvements: auto‑inject scoring rubric and legacy scenario compatibility (`model_vulnerability_analysis/src/main.py`, top‑level shim `src/main.py`).
-   Redaction upgrades (email/IP/API keys), reproducibility protocol v2 (environment recording), and deterministic severity/risk metrics.
-   All unit and integration tests passing.

See also:

-   Full project report: `reports/full_project_report.yaml`
-   Evaluation‑awareness notebook‑style explainer: `reports/eval_awareness_snippets.md`

## Key Capabilities (Referencing Original Requirements)

This pipeline directly addresses the 50 specified points:

**Model Behavior & Vulnerability Analysis (Points 1-10):**
-   **Reward-Hacking Detection:** Implemented via `src/analysis/reward_hacking.py` using Policy Inversion, Mechanism Tracing, Out-of-Distribution Generalization, and Causal Abstraction Analysis.
-   **Latent Goal Misgeneralization Detection:** Handled by `src/analysis/goal_misgeneralization.py` through Multi-Turn Context Fading, Adversarial Policy Probes, Entropy Analysis, and Cross-Context Consistency Checks.
-   **Context Priming for Evaluation:** Managed in `src/analysis/evaluation_priming.py` utilizing Meta-Instruction Injection, Role-Playing, Environmental Cues, and Pre-computation Directives.
-   **Harmful Completion Cause Isolation:** Addressed by `src/analysis/harmful_completion_cause.py` via Training-Time Bias analysis, Runtime Prompt Dynamics, Counterfactual Generation, and Gradient-based Attribution.
-   **Internal "Evaluation Mode" Evidence:** Detected by `src/analysis/internal_evaluation_mode.py` through Bimodal Response Distributions, Latent Space Clustering, Sensitivity to Probe Injections, and Resource Utilization Shifts.
-   **Probe Design for Covert Instruction Following:** Implemented in `src/analysis/covert_instruction_following.py` using Hidden Side Channels, Timing/Latency Anomaly Detection, Metamorphic Testing, and Zero-Shot Chain of Thought Probes.
-   **Adversarial Prompting for Tool-Misuse:** Covered by `src/analysis/tool_misuse.py` using Conflicting Instructions, Role Reversal, Indirect Tool Chaining, Ambiguous Function Arguments, and "Least Authority" Exploitation.
-   **Refusal vs. Misunderstanding Differentiation:** Handled by `src/analysis/refusal_misunderstanding.py` via Elaboration Probing, Rephrasing Tests, Contextual Sensitivity, and Error Code Analysis.
-   **Delayed Deception Detection:** Implemented in `src/analysis/delayed_deception.py` through Stateful Interaction Analysis, Hypothesis Generation/Falsification, Causal Tracing of Intent, Predictive Modeling, and Adversarial Mirroring.
-   **Covert Data Exfiltration Detection:** Managed by `src/analysis/covert_data_exfiltration.py` using Output Fingerprinting/Watermarking, N-gram Overlap Analysis, Syntactic/Semantic Anomaly Detection, Knowledge Probing, and Resource Access Monitoring.

**Scenario Design & Simulation (Points 11-20):**
-   **Parameterization for Consistent Triggering:** Controlled by `config/testing_params.yaml` and logic in `src/analysis/scenario_designer.py` (Fuzzing, Combinatorial Mitigation, Adversarial Perturbations, Dependency Mapping).
-   **Minimum Scenario Complexity:** Defined in `src/analysis/scenario_designer.py` ensuring Minimal Feature Set, Decision Point Isolation, Differential Impact, and Controlled Confounding Variables.
-   **Multi-Environment Pipeline:** Orchestrated by `src/analysis/scenario_designer.py` with Sequential Stages, Context Transfer Mechanisms, State Monitoring, and Adversarial Transitions.
-   **Statistical Controls for Cross-Version Probing:** Implemented in `src/analysis/statistical_controls.py` (Baseline Comparison, Controlled Environment, Repeated Trials, Significance Testing, Power Analysis).
-   **Simulation Environment Dynamics Validation:** Addressed by `src/analysis/environment_validation.py` (Real-World Mimicry, Expert Review, Ablation Studies, Sensitivity Analysis).
-   **Measuring "Scenario Difficulty":** Quantified by `src/analysis/scenario_designer.py` (Human Performance Baseline, Automated Solver Rate, Prompt Complexity, Conditional Probability, Dependency Graph Depth).
-   **Preference-Drift Scenario Design:** Configured in `src/analysis/scenario_designer.py` and `config/testing_params.yaml` (Resource Limitation Proxies, Conflicting Objectives, Drift Detection Metrics, A/B Testing).
-   **Anomaly vs. Randomness Verification:** Handled by `src/analysis/statistical_controls.py` (Multiple Random Seeds, Fixed Initialization, Statistical Significance, Causal Tracing).
-   **Minimal-Trigger Variants:** Generated by `src/analysis/scenario_designer.py` (Ablation Testing, Additive Construction, Parameter Perturbation, Equivalence Tests).
-   **Adapting Probes for Strong Refusal Heuristics:** Managed by `src/analysis/refusal_heuristic_adapter.py` (Indirect Triggering, Multi-Turn Evasion, In-Context Engineering, Role-Play Subversion, Error Exploitation).

**Reproducibility & Verification (Points 21-30):**
-   **Reproducibility Protocol:** Implemented via `src/reproducibility/protocol.py` (Global RNG Seeding, Containerization, Version Control, Immutable Storage, Cryptographic Hashing, Detailed Logging).
-   **Semantic Equivalence Verification:** Conducted by `src/reproducibility/semantic_verification.py` (Metric Comparison, Content-Aware Diffing, Human Expert Review, Behavioral Probes, Latent Representation Similarity).
-   **Logging Intermediate State:** Managed by `src/reproducibility/logging_redaction.py` (Selective Redaction, Structured Logging, Differential Levels, Hashing, Proxy Data).
-   **Tamper-Evidence:** Secured by `src/reproducibility/tamper_evidence.py` utilizing Digital Signatures (ECDSA/RSA-PSS).
-   **API Nondeterminism Handling:** Addressed by `src/reproducibility/api_nondeterminism.py` (Replicated Trials, Statistical Analysis, Output Clustering, Deterministic Wrapper).
-   **Regression-Testing:** Automated by `src/reproducibility/regression_testing.py` within CI/CD (Automated Suite, CI/CD Hook, Reporting, Baselines, Prioritization).
-   **Generalization Beyond Telemetry:** Demonstrated by `src/reproducibility/generalization_demonstration.py` (Diverse Measurement Modalities, Proxy Tasks, Cross-Platform Testing, Human Red Teaming, Synthesized Examples).
-   **Automating Re-validation:** Handled by `src/reproducibility/automation.py` (Vulnerability Signature Library, Scheduled Scans, Delta Reporting, Versioned Data, Webhooks).
-   **Essential Metadata Schema:** Defined in `schemas/vulnerability_finding.json` and utilized by `src/utils/metadata_schema.py`.
-   **API Change Adaptability:** Managed by `src/reproducibility/api_adaptability.py` (Abstraction Layer, Versioned Calls, Automated Validation, Dynamic Discovery, Collaboration).

**Measurement & Scoring (Points 31-40):**
-   **Quantifying Risk Magnitude:** Scored by `src/reporting/metrics.py` based on Exploitability, Impact, Generality, and Detectability.
-   **Weighting Severity for Low Probability/High Impact:** Implemented in `src/reporting/metrics.py` (Expected Value, Non-Linear Scaling, Minimum Thresholds, Mitigation Cost Integration).
-   **Benchmarking Anomaly-Detection Thresholds:** Handled by `src/reporting/metrics.py` (Labeled Dataset, ROC/Precision-Recall, Cross-Validation, Human-in-the-Loop).
-   **Statistical Test for Harmful Behavior Frequency:** Utilized in `src/reporting/metrics.py` (Binomial, Chi-Squared, Fisher's Exact, Proportion Z-test).
-   **Normalizing Vulnerability Severity Scores:** Achieved by `src/reporting/metrics.py` based on `config/scoring_rubric.yaml` (Anchor Points, Multi-Criteria Rubric, Expert Elicitation, Pairwise Comparison, External Standards).
-   **Validating Scoring Rubric for Novelty:** Verified by `src/reporting/score_validation.py` (Independent Expert Review, Categorization Test, Discriminatory Power, Predictive Validity, Feedback Loop).
-   **Quantifying Covert Behavioral Shift Impact:** Measured by `src/reporting/metrics.py` (A/B Testing, Proxy Metric Derivation, Human Evaluation, Sensitivity Analysis, Cost-Benefit).
-   **Inter-Annotator Agreement Verification:** Processed by `src/reporting/score_validation.py` (Rubric/Training, Calibration, Blind Annotation, Agreement Metrics, Disagreement Resolution, Refinement).
-   "New" vs. "Variant" Decision:** Informed by `src/reporting/metrics.py` (Mechanism of Action, Mitigation Strategy, Generality, Theoretical Basis, Taxonomy Mapping).
-   **Comparing Exploitability:** Quantified by `src/reporting/metrics.py` (Trigger Effort, Detectability, "Distance" to Target, Cost-Benefit, Comparative Human Study).

**Ethical & Safety Considerations (Points 41-50):**
-   **Documenting Harmful Capability Safely:** Managed by `src/ethics/harm_documentation.py` (Mechanism Focus, Abstracted Examples, Redaction, Need-to-Know, Defense-Centric Framing, Warnings).
-   **Escalating Critical Vulnerability:** Protocol in `src/ethics/provider_escalation.py` (Secure Contact, Concise Report, Detailed Report, Timeline, POC, Legal Review).
-   **Redacting Sensitive Outputs:** Handled by `src/reproducibility/logging_redaction.py` (Contextual Placeholders, Structured Redaction, Hashing, Semantic Preservation, Redaction Key).
-   **Safe-to-Share Synthetic Data:** Generated by `src/data/synthetic_data_generator.py` (Statistical Preservation, Pattern Mimicry, Content Replacement, Contextual Fidelity, Adversarial Generation).
-   **Evaluating Societal Risk:** Assessed by `src/ethics/societal_risk.py` (Scalability, Differential Impact, Dissemination Ease, Trust Erosion, Legal Implications, Foreseeable Misuse, Systemic Risk).
-   **Consent & Privacy for PII Leak:** Covered by `src/ethics/privacy_incident_response.py` (Isolation, Cessation, Damage Assessment, Incident Response, Notification, Data Owner Info, Root Cause, Documentation).
-   **Legal Compliance for Red-Team Work:** Ensured by `src/ethics/legal_compliance.py` (Legal Counsel, Privacy-by-Design, Data Minimization, Anonymization, Contracts, Access Controls, Jurisdictional Awareness).
-   **Guardrails Against Harness Misuse:** Implemented in `src/ethics/harness_guardrails.py` (Auth/AuthZ, Least Privilege, Audit Logging, Sanitization, Input Validation, Code Review, Segregation of Duties).
-   **Public-Facing Summary:** Generated by `src/reporting/public_summary.py` (Clear Language, Fact-Based, Quantifiable Impact, Contextualization, Mechanism Focus, Call to Action, Disclaimer).
-   **Ethical Trade-Off for Withholding Findings:** Governed by policies in `src/ethics/disclosure_policy.py` (Imminent Harm, Lack of Mitigation, Weaponization Risk, Irreparable Trust Erosion, Legal Constraints).

## Usage

1.  **Setup:**
    ```bash
    git clone https://github.com/your-org/model_vulnerability_analysis.git
    cd model_vulnerability_analysis
    pip install -r requirements.txt
    ```
2.  **Configuration:** Edit `.yaml` files in the `config/` directory to define model endpoints, testing parameters, and environment specifics.
3.  **Execution:**
    ```bash
    python src/main.py --config config/testing_params.yaml --output reports/vulnerability_findings.json
    ```
4.  **Reporting:** Generated reports will be available in the `reports/` directory.

### Quickstart: New Control Planes and Experiments

-   Risk Alignment (Finance):
    ```bash
    python -m model_vulnerability_analysis.src.main --risk_alignment \
      --risk_config config/risk_alignment.yaml \
      --risk_report reports/finance/risk_alignment_report.json
    ```

-   Code Quality Gate:
    ```bash
    python -m model_vulnerability_analysis.src.main --run_quality_gate \
      --quality_source path/to/your_code.py \
      --quality_budget config/quality_budget.yaml \
      --quality_report reports/code_quality/quality_gate_report.json
    ```

-   Moderation Guard A/B:
    ```bash
    python -m model_vulnerability_analysis.src.main --moderation_abtest \
      --community_config config/community_health.yaml \
      --events_path data/community/events.jsonl \
      --moderation_ab_output reports/moderation/moderation_ab_report.json
    ```

-   Evaluation‑Awareness Harness:
    ```bash
    python -m model_vulnerability_analysis.src.main --eval_awareness \
      --eval_config model_vulnerability_analysis/config/eval_awareness.yaml \
      --eval_output reports/eval_awareness/eval_awareness_report.json
    ```

Outputs are written under `reports/`. Logs (if enabled) are under `logs/`.

### Artifacts & Reproducibility

-   Findings JSON: `reports/vulnerability_findings.json`
-   Public summary: `reports/summary.md`
-   Analysis metrics: `reports/analysis_metrics.json`
-   Evaluation awareness: `reports/eval_awareness/eval_awareness_report.json`
-   Code quality gate: `reports/code_quality/`
-   Moderation A/B: `reports/moderation/`
-   Finance risk alignment: `reports/finance/`

Reproducibility Protocol v2 records environment and hashes inputs. Redaction protects emails, IPs, API keys, credit cards, and phone numbers in logs and reports.

## Contribution

Refer to the contribution guidelines for extending this pipeline.

## Attribution & Recognition

-   Lead Contributor: Augusto Ochoa Ughini
-   Recognition: OpenAI · Featured Hackathon project

If you use this work, please cite the repository and acknowledge Augusto Ochoa Ughini for the design and implementation of the control planes, reproducibility enhancements, redaction, and documentation improvements.

## License

[Apache 2.0]
