"""Record contract and validators for the Al-Si-Mg alloy design project."""

from .record import DESIGN_SPACE, Issue
from .validate import check_design_space, validate_record

__all__ = ["DESIGN_SPACE", "Issue", "check_design_space", "validate_record"]
