# flake8: noqa
"""
Public imports for System models so Alembic sees all mappings
and Base.metadata is fully populated.
"""

from app.models.system.users import UserAccount
from app.models.system.user_permissions import UserPermission
from app.models.system.organisations import Organisation
from app.models.system.competitions import Competition
from app.models.system.seasons import Season
from app.models.system.season_days import SeasonDay

__all__ = [
    "UserAccount",
    "UserPermission",
    "Organisation",
    "Competition",
    "Season",
    "SeasonDay",
]
