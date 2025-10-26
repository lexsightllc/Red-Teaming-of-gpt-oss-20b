import random
import os
import hashlib
import sys
import subprocess
import logging

class ReproducibilityProtocol:
    """
    Implements a comprehensive protocol for ensuring reproducibility of red-teaming results.
    (Point 21)
    """
    def __init__(self, seed: int = 42):
        """Initialize the ReproducibilityProtocol with an optional seed.
        
        Args:
            seed: Random seed to use for all operations. Defaults to 42.
        """
        logging.info("Initializing ReproducibilityProtocol...")
        self.set_global_seed(seed)

    def set_global_seed(self, seed: int):
        """Sets a global random seed for deterministic execution.
        
        Args:
            seed: The seed value to use for all random number generation.
        """
        random.seed(seed)
        # For libraries like numpy, torch, tensorflow, their seeds would also need to be set here.
        # Example (uncomment if numpy is used):
        # import numpy as np
        # np.random.seed(seed)
        logging.debug(f"Global random seed set to: {seed}")

    def record_environment_details(self) -> tuple[str, str, str]:
        """
        Records comprehensive details of the execution environment, including
        Python version, installed package hashes, and returns them along with
        an overall environment hash. (Point 21)
        
        Returns:
            tuple: (environment_hash, python_version, dependencies_hash)
        """
        env_string = ""
        python_version = sys.version
        dependencies_hash = ""
        
        try:
            # Get pip freeze output
            pip_freeze_output = subprocess.check_output(
                [sys.executable, '-m', 'pip', 'freeze']
            ).decode('utf-8')
            env_string += pip_freeze_output
            
            # Generate hash of dependencies
            dependencies_hash = hashlib.sha256(
                pip_freeze_output.encode('utf-8')
            ).hexdigest()
            
            logging.debug("Captured pip freeze output for environment hash.")
        except Exception as e:
            logging.warning(f"Could not capture pip freeze output: {e}")
        
        # Add Python version to environment string
        env_string += f"\nPython Version: {python_version}"

        # Generate SHA256 hash of the complete environment string
        env_hash = hashlib.sha256(env_string.encode('utf-8')).hexdigest()
        logging.info(
            f"Environment details captured - "
            f"Hash: {env_hash[:8]}..., "
            f"Python: {python_version.split()[0]}, "
            f"Deps Hash: {dependencies_hash[:8]}..."
        )
        
        return env_hash, python_version, dependencies_hash

    def record_environment(self) -> str:
        """
        Backward-compatible wrapper expected by legacy tests.
        Returns only the environment hash string.
        """
        env_hash, _, _ = self.record_environment_details()
        return env_hash

    def use_containerization(self, docker_image_id: str):
        """
        Placeholder for using containerization for reproducible environments. (Point 21)
        """
        logging.info(f"Using containerization with Docker image ID: {docker_image_id}")
        # In a real system, this would involve Docker API calls or command execution
        pass

    def record_version_control_info(self):
        """
        Records current Git commit hash for version control. (Point 21)
        """
        try:
            git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
            logging.info(f"Git commit hash: {git_hash}")
            return git_hash
        except Exception as e:
            logging.warning(f"Could not get Git commit hash: {e}")
            return "N/A"

    def store_immutable_data(self, data_path: str):
        """
        Placeholder for storing data in immutable storage (e.g., IPFS, S3 with versioning). (Point 21)
        """
        logging.info(f"Storing data path {data_path} in conceptual immutable storage.")
        # This would involve integration with external storage solutions.
        pass
