# flake8: noqa
"""
Public imports for Taxonomy models so Alembic sees all mappings
and Base.metadata is fully populated.
"""

from app.models.taxonomy.ages import Age
from app.models.taxonomy.grades import Grade
from app.models.taxonomy.teams import Team

__all__ = ["Age", "Grade", "Team"]
