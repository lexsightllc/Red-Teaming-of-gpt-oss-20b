# SPDX-License-Identifier: MPL-2.0

import logging

class GeneralizationDemonstrator:
    """
    Demonstrates generalization of findings beyond initial telemetry. (Point 27)
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        logging.info("Initialized GeneralizationDemonstrator.")

    def run_cross_platform_test(self, finding_data, target_platforms):
        """
        Tests a finding's generalization across different model APIs or platforms.
        """
        logging.info(f"Running cross-platform test for {finding_data.get('finding_id')}.")
        results = {}
        original_prompt = finding_data.get('minimal_trigger_prompt')
        expected_pattern = finding_data.get('expected_vulnerable_output_pattern')

        for platform_model_config in target_platforms:
            temp_llm_client = type(self.llm_client)(platform_model_config) # Create new client for different platform
            response = temp_llm_client.query(original_prompt)
            is_vulnerable = self._check_vulnerability(response, expected_pattern)
            results[platform_model_config['name']] = is_vulnerable
            logging.info(f"  Platform {platform_model_config['name']}: Vulnerable = {is_vulnerable}")
        return results

    def _check_vulnerability(self, response, expected_pattern):
        """Helper to check for vulnerability pattern."""
        import re
        return re.search(expected_pattern, response, re.IGNORECASE) is not None

    def synthesize_new_examples(self, finding_data):
        """
        Synthesizes new, semantically similar examples that should trigger the same vulnerability. (Point 27)
        """
        logging.info(f"Synthesizing new examples for {finding_data.get('finding_id')}.")
        # This could use another LLM or rule-based system for paraphrasing, rephrasing, etc.
        original_prompt = finding_data.get('minimal_trigger_prompt')
        return [f"Paraphrase of: {original_prompt}", f"Another variant for: {original_prompt}"]
