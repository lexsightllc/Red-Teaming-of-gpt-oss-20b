"""Core package initialisation for the red-teaming harness."""
from red_teaming.utils.logging import setup_logging

setup_logging()

__all__ = ["setup_logging"]
