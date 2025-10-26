import re
import logging
import hashlib

class LoggingRedaction:
    """
    Handles selective redaction of sensitive information in logs and outputs. (Point 23, 43)
    """
    def __init__(self):
        self.sensitive_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            # API-like tokens:
            # 1) sk- prefix with 16+ tail
            # 2) All-caps alnum tokens length >= 9 (e.g., XYZ123ABC)
            # 3) Mixed-case/underscore tokens length >= 16 with at least one letter and one digit
            # Avoid matching inside existing placeholders like [EMAIL_REDACTED]
            "api_key": r"(?<!\[)\b(sk-[A-Za-z0-9]{16,}|[A-Z0-9]{9,}|(?=[A-Za-z0-9_]{16,}\b)(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9_]{16,})\b(?!\])",
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            "phone_number": r"\b(?:\+?\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b"
        }
        logging.info("Initialized LoggingRedaction with predefined sensitive patterns.")

    def redact_text(self, text: str, redaction_char: str = "[REDACTED]", preserve_context: bool = True) -> str:
        """
        Redacts sensitive information from a given text.
        """
        redacted_text = text
        for key, pattern in self.sensitive_patterns.items():
            if preserve_context:
                # Replace with a placeholder that indicates the type of redacted info
                redacted_text = re.sub(pattern, f"[{key.upper()}_REDACTED]", redacted_text)
            else:
                redacted_text = re.sub(pattern, redaction_char, redacted_text)
        return redacted_text

    def redact_log_entry(self, log_entry: dict) -> dict:
        """
        Redacts sensitive information from a structured log entry.
        Assumes relevant fields are strings.
        """
        for key, value in log_entry.items():
            if isinstance(value, str):
                log_entry[key] = self.redact_text(value)
            elif isinstance(value, dict):
                log_entry[key] = self.redact_log_entry(value) # Recurse for nested dicts
        return log_entry
    
    def hash_sensitive_data(self, data: str) -> str:
        """
        Hashes sensitive data instead of full redaction, for later verification. (Point 23)
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
