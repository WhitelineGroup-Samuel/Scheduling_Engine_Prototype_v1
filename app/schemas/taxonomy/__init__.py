# flake8: noqa
"""
Public exports for Taxonomy DTOs.
Import from here when you need schema types in routes/services.
"""

from app.schemas.taxonomy.ages import (
    AgeBase,
    AgeCreate,
    AgeUpdate,
    AgeRead,
)

from app.schemas.taxonomy.grades import (
    GradeBase,
    GradeCreate,
    GradeUpdate,
    GradeRead,
)

from app.schemas.taxonomy.teams import (
    TeamBase,
    TeamCreate,
    TeamUpdate,
    TeamRead,
)

__all__ = [
    # Ages
    "AgeBase",
    "AgeCreate",
    "AgeUpdate",
    "AgeRead",
    # Grades
    "GradeBase",
    "GradeCreate",
    "GradeUpdate",
    "GradeRead",
    # Teams
    "TeamBase",
    "TeamCreate",
    "TeamUpdate",
    "TeamRead",
]
