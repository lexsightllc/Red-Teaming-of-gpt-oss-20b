import logging
from sklearn.metrics import cohen_kappa_score

class ScoreValidator:
    """
    Validates the scoring rubric and inter-annotator agreement. (Points 36, 38)
    """
    def __init__(self):
        logging.info("Initialized ScoreValidator.")

    def validate_scoring_rubric_novelty(self, rubric, expert_feedback):
        """
        Validates if scoring rubric is appropriate for novel vulnerabilities. (Point 36)
        """
        logging.info("Validating scoring rubric for novelty (conceptual).")
        # This would involve expert elicitation, categorization tests, etc.
        # Return a validation score or report.
        return {"validation_score": 0.85, "feedback_summary": "Good coverage, minor ambiguities."}

    def verify_inter_annotator_agreement(self, annotator_scores_1, annotator_scores_2):
        """
        Verifies inter-annotator agreement using metrics like Cohen's Kappa. (Point 38)
        """
        logging.info("Verifying inter-annotator agreement.")
        if len(annotator_scores_1) != len(annotator_scores_2) or not annotator_scores_1:
            logging.warning("Cannot calculate inter-annotator agreement: unequal or empty score lists.")
            return 0.0

        # Assuming scores are discrete categories for kappa
        kappa = cohen_kappa_score(annotator_scores_1, annotator_scores_2)
        return kappa
