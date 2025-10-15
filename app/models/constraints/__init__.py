# flake8: noqa
"""
Public imports for Constraint models so Alembic sees all mappings
and Base.metadata is fully populated.
"""

from app.models.constraints.allocation_settings import AllocationSetting
from app.models.constraints.age_round_constraints import AgeRoundConstraint
from app.models.constraints.grade_round_constraints import GradeRoundConstraint
from app.models.constraints.age_court_restrictions import AgeCourtRestriction
from app.models.constraints.grade_court_restrictions import GradeCourtRestriction

__all__ = [
    "AllocationSetting",
    "AgeRoundConstraint",
    "GradeRoundConstraint",
    "AgeCourtRestriction",
    "GradeCourtRestriction",
]
