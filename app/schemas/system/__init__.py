# flake8: noqa
"""
Public exports for System DTOs.
Import from here when you need schema types in routes/services.
"""

from app.schemas.system.users import (
    UserAccountBase,
    UserAccountCreate,
    UserAccountUpdate,
    UserAccountRead,
)

from app.schemas.system.organisations import (
    OrganisationBase,
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationRead,
)

from app.schemas.system.competitions import (
    CompetitionBase,
    CompetitionCreate,
    CompetitionUpdate,
    CompetitionRead,
)

from app.schemas.system.seasons import (
    SeasonBase,
    SeasonCreate,
    SeasonUpdate,
    SeasonRead,
)

from app.schemas.system.season_days import (
    SeasonDayBase,
    SeasonDayCreate,
    SeasonDayUpdate,
    SeasonDayRead,
)

from app.schemas.system.user_permissions import (
    UserPermissionBase,
    UserPermissionCreate,
    UserPermissionUpdate,
    UserPermissionRead,
)

__all__ = [
    # Users
    "UserAccountBase",
    "UserAccountCreate",
    "UserAccountUpdate",
    "UserAccountRead",
    # Organisations
    "OrganisationBase",
    "OrganisationCreate",
    "OrganisationUpdate",
    "OrganisationRead",
    # Competitions
    "CompetitionBase",
    "CompetitionCreate",
    "CompetitionUpdate",
    "CompetitionRead",
    # Seasons
    "SeasonBase",
    "SeasonCreate",
    "SeasonUpdate",
    "SeasonRead",
    # Season Days
    "SeasonDayBase",
    "SeasonDayCreate",
    "SeasonDayUpdate",
    "SeasonDayRead",
    # User Permissions
    "UserPermissionBase",
    "UserPermissionCreate",
    "UserPermissionUpdate",
    "UserPermissionRead",
]
