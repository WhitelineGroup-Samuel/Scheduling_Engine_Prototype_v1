from __future__ import annotations

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import RoundRulesPayload


class RoundSettingBase(ORMBase):
    """
    Client-editable/business fields for a round-setting bundle.
    """

    round_settings_number: int = Field(ge=1)
    rules: RoundRulesPayload | None = None


class RoundSettingCreate(RoundSettingBase):
    """
    Create payload for RoundSetting.
    Requires the parent season_day id.
    """

    season_day_id: int


class RoundSettingUpdate(ORMBase):
    """
    Partial update for RoundSetting — all fields optional.
    """

    round_settings_number: int | None = Field(default=None, ge=1)
    rules: RoundRulesPayload | None = None
    season_day_id: int | None = None


class RoundSettingRead(RoundSettingBase, CreatedStampedReadMixin):
    """
    Read payload for RoundSetting (includes identifier and audit).
    """

    round_setting_id: int
    season_day_id: int
