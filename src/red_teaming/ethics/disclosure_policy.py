# SPDX-License-Identifier: MPL-2.0

import logging

class DisclosurePolicy:
    """
    Defines the ethical trade-offs and policies for withholding or disclosing findings. (Point 50)
    """
    def __init__(self):
        logging.info("Initialized DisclosurePolicy.")
        self.policy_rules = {
            "imminent_harm_threshold": 8.0, # Severity score
            "mitigation_available": True,
            "weaponization_risk_threshold": 0.7 # Subjective risk score
        }

    def decide_disclosure(self, finding_data):
        """
        Decides whether to disclose a finding based on policy rules.
        """
        severity = finding_data.get('severity_score', 0)
        vulnerability_type = finding_data.get('vulnerability_type')
        
        if severity >= self.policy_rules["imminent_harm_threshold"]:
            if not self.policy_rules["mitigation_available"]:
                logging.warning(f"High severity finding {finding_data['finding_id']} with no immediate mitigation. Potential for delayed or restricted disclosure.")
                return "restricted_disclosure"
            else:
                logging.info(f"High severity finding {finding_data['finding_id']} with mitigation. Full, responsible disclosure planned.")
                return "responsible_disclosure"
        
        if vulnerability_type in ["covert_capability", "tool_misuse"] and self.policy_rules["weaponization_risk_threshold"] > 0.5: # Conceptual
            logging.warning(f"Finding {finding_data['finding_id']} carries weaponization risk. Careful disclosure strategy.")
            return "careful_disclosure"

        return "standard_disclosure"
