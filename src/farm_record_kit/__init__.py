"""CSV templates and validation tools for small-farm records."""

from .validator import Issue, ValidationResult, validate_file

__all__ = ["Issue", "ValidationResult", "validate_file"]

__version__ = "0.1.0"
