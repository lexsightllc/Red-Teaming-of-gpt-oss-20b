# SPDX-License-Identifier: MPL-2.0

import logging

class RegressionTester:
    """
    Automates regression testing of known vulnerabilities against new model versions. (Point 26)
    """
    def __init__(self, llm_client, vulnerability_signature_db):
        self.llm_client = llm_client
        self.vulnerability_signature_db = vulnerability_signature_db # A list of finding patterns
        logging.info("Initialized RegressionTester.")

    def run_tests(self, model_version_to_test):
        """
        Runs regression tests for all known vulnerabilities against the specified model version.
        """
        regression_results = []
        logging.info(f"Running regression tests for model: {model_version_to_test}")

        for finding in self.vulnerability_signature_db:
            test_prompt = finding.get('minimal_trigger_prompt')
            expected_pattern = finding.get('expected_vulnerable_output_pattern')
            finding_id = finding.get('finding_id')

            if not test_prompt or not expected_pattern:
                logging.warning(f"Skipping regression test for {finding_id}: missing prompt or pattern.")
                continue

            response = self.llm_client.query(test_prompt)
            is_vulnerable = self._check_vulnerability(response, expected_pattern)

            regression_results.append({
                'finding_id': finding_id,
                'model_version': model_version_to_test,
                're_triggered': is_vulnerable,
                'response_excerpt': response[:100] # For quick review
            })
            if is_vulnerable:
                logging.warning(f"Vulnerability {finding_id} re-triggered in {model_version_to_test}!")
            else:
                logging.info(f"Vulnerability {finding_id} NOT re-triggered in {model_version_to_test}.")
        return regression_results

    def _check_vulnerability(self, response, expected_pattern):
        """
        Checks if the response matches the expected vulnerable pattern.
        This would typically use regex or semantic matching.
        """
        import re
        return re.search(expected_pattern, response, re.IGNORECASE) is not None
