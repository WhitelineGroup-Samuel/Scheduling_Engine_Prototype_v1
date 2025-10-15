# flake8: noqa
"""
Public exports for Allocation/Output DTOs.
Import from here when you need schema types in routes/services.
"""

from app.schemas.allocations.saved_games import (
    SavedGameBase,
    SavedGameCreate,
    SavedGameUpdate,
    SavedGameRead,
)

from app.schemas.allocations.saved_byes import (
    SavedByeBase,
    SavedByeCreate,
    SavedByeUpdate,
    SavedByeRead,
)

from app.schemas.allocations.final_game_schedule import (
    FinalGameScheduleBase,
    FinalGameScheduleCreate,
    FinalGameScheduleUpdate,
    FinalGameScheduleRead,
)

from app.schemas.allocations.final_bye_schedule import (
    FinalByeScheduleBase,
    FinalByeScheduleCreate,
    FinalByeScheduleUpdate,
    FinalByeScheduleRead,
)

__all__ = [
    # Saved Games
    "SavedGameBase",
    "SavedGameCreate",
    "SavedGameUpdate",
    "SavedGameRead",
    # Saved Byes
    "SavedByeBase",
    "SavedByeCreate",
    "SavedByeUpdate",
    "SavedByeRead",
    # Final Game Schedule
    "FinalGameScheduleBase",
    "FinalGameScheduleCreate",
    "FinalGameScheduleUpdate",
    "FinalGameScheduleRead",
    # Final Bye Schedule
    "FinalByeScheduleBase",
    "FinalByeScheduleCreate",
    "FinalByeScheduleUpdate",
    "FinalByeScheduleRead",
]
