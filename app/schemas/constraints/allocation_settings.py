from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase, UpdatedStampedReadMixin
from app.schemas.enums import AllocationRestrictionType


class AllocationSettingBase(ORMBase):
    """
    Client-editable/business fields for allocation_settings.
    """

    round_setting_id: int
    age_id: int
    grade_id: int
    restricted: bool | None = False
    restriction_type: AllocationRestrictionType = AllocationRestrictionType.NONE


class AllocationSettingCreate(AllocationSettingBase):
    """
    Create payload for AllocationSetting.
    'created_by_user_id'/'updated_by_user_id' set by the service layer.
    """

    pass


class AllocationSettingUpdate(ORMBase):
    """
    Partial update for AllocationSetting — all fields optional.
    """

    round_setting_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    restricted: bool | None = None
    restriction_type: AllocationRestrictionType | None = None


class AllocationSettingRead(AllocationSettingBase, CreatedStampedReadMixin, UpdatedStampedReadMixin):
    """
    Read payload for AllocationSetting (includes identifiers and audit fields).
    """

    allocation_setting_id: int
