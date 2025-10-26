import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import logging
import os

class TamperEvidence:
    """
    Provides cryptographic methods for tamper-evidence of generated reports and data. (Point 24)
    Uses digital signatures (ECDSA/RSA-PSS).
    """
    def __init__(self):
        self.private_key = None
        self.public_key = None
        logging.info("Initialized TamperEvidence.")

    def generate_key_pair(self):
        """Generates a new RSA private and public key pair."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        logging.info("Generated new RSA key pair for signing.")

    def sign_artifact(self, filepath: str) -> bytes:
        """
        Signs a file with the private key.
        Returns the signature.
        """
        if not self.private_key:
            raise ValueError("Private key not generated. Call generate_key_pair() first.")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(file_content)
        digest = hasher.finalize()

        signature = self.private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        logging.info(f"Signed artifact: {filepath}")
        return signature

    def verify_signature(self, filepath: str, signature: bytes, public_key) -> bool:
        """
        Verifies the signature of a file using the public key.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(file_content)
        digest = hasher.finalize()

        try:
            public_key.verify(
                signature,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            logging.info(f"Signature for {filepath} is valid.")
            return True
        except Exception as e:
            logging.error(f"Signature verification failed for {filepath}: {e}")
            return False
