# app/db/seed.py
"""
Deterministic, idempotent ORM seeding for the dev database.

- Uses portable get_or_create() keyed by natural uniques (slug/code/composites)
- Runs in a fixed order so FKs exist before dependents
- Safe to re-run: no duplicates
- Skips TimeSlot seeding until 'default_times' exists (per user instruction)
"""

from __future__ import annotations

import re as _re
from dataclasses import dataclass
from datetime import date, time
from typing import Any, Final, NotRequired, TypedDict

from sqlalchemy.orm import Session

from app.db.seed_helpers import (
    echo,
    ensure_seed_admin_user,
    get_one_by,
    get_or_create,
    slugify,
)
from app.models.system.competitions import Competition

# --- Models (adjust imports if your module paths differ) ---
from app.models.system.organisations import Organisation
from app.models.system.season_days import SeasonDay
from app.models.system.seasons import Season
from app.models.system.user_permissions import (
    UserPermission,
)
from app.models.system.users import UserAccount
from app.models.taxonomy.ages import Age
from app.models.taxonomy.grades import Grade
from app.models.taxonomy.teams import Team
from app.models.timeplan.round_settings import (
    RoundSetting,
)
from app.models.timeplan.rounds import Round
from app.models.venues.courts import Court
from app.models.venues.venues import Venue


class BaselineSeason(TypedDict):
    name: str
    start_date: date
    end_date: date


class BaselineSeasonDay(TypedDict, total=False):
    season_day_name: str
    week_day: int
    active: NotRequired[bool]
    display_label: NotRequired[str]
    window_start: NotRequired[time]
    window_end: NotRequired[time]


class BaselineCourt(TypedDict, total=False):
    court_code: str
    court_name: NotRequired[str]
    display_order: NotRequired[int]


class BaselineVenue(TypedDict, total=False):
    venue_name: str
    venue_address: str
    display_order: NotRequired[int]
    is_accessible: NotRequired[bool]
    accessible: NotRequired[bool]
    indoor: NotRequired[bool]
    courts: NotRequired[list[BaselineCourt]]


class BaselineTeam(TypedDict, total=False):
    team_code: str
    team_name: NotRequired[str]


class BaselineGrade(TypedDict, total=False):
    grade_code: str
    grade_name: str
    grade_rank: int
    teams: NotRequired[list[BaselineTeam]]


class BaselineAge(TypedDict, total=False):
    age_code: str
    age_name: str
    age_rank: int
    gender: NotRequired[str]
    grades: NotRequired[list[BaselineGrade]]


class BaselineRound(TypedDict, total=False):
    round_number: int
    round_type: NotRequired[str]
    round_label: str


class BaselineRoundSetting(TypedDict, total=False):
    round_settings_number: int


class BaselineRoot(TypedDict):
    organisation: dict[str, str]  # {"name": "..."}
    competition: dict[str, str]  # {"name": "..."}
    season: BaselineSeason
    season_days: list[BaselineSeasonDay]
    venues: list[BaselineVenue]
    ages: list[BaselineAge]
    rounds: list[BaselineRound]
    round_settings: list[BaselineRoundSetting]


# --- Fallback slug normalizer for tests/utils/test_slug_normalizer.py -------
_slug_re = _re.compile(r"[^a-z0-9]+")


def _fallback_normalize_slug(name: str) -> str:
    """
    Lowercase, replace any non [a-z0-9] run with '-', collapse dashes,
    trim leading/trailing dashes. If the result is empty, return 'org'.
    """
    if not name:
        return "org"
    s = name.strip().lower()
    s = _slug_re.sub("-", s)
    s = s.strip("-")
    return s or "org"


# ---------------------------------------------------------------------------

# ======================================================================================
# Small baseline data (expand later to mirror your full SQL seed)
# ======================================================================================

DEFAULT_ORG_NAME = "Kilsyth Basketball Association"
DEFAULT_COMP_NAME = "Junior Domestic"
DEFAULT_SEASON_NAME = "Winter 2024"

BASELINE: Final[BaselineRoot] = {
    "organisation": {
        "name": DEFAULT_ORG_NAME,
        # slug derived via slugify() at runtime to keep one source of truth
    },
    "competition": {
        "name": DEFAULT_COMP_NAME,
        # slug derived via slugify()
    },
    "season": {
        "name": DEFAULT_SEASON_NAME,
        # slug derived via slugify()
        # Dates: tweak if your model expects different columns/types
        "start_date": date(2024, 4, 13),
        "end_date": date(2024, 9, 14),
    },
    # Seed only Saturday for now; you can add ["Mon", ...] later.
    "season_days": [
        {
            "season_day_name": "Saturday",
            "week_day": 6,  # ISO: Mon=1..Sun=7 → Saturday=6
            "active": True,
            "display_label": "Saturday",
        }
    ],
    "venues": [
        {
            "venue_name": "Kilsyth Sports Centre",
            "venue_address": "115 Liverpool Rd, Kilsyth VIC",
            "display_order": 1,
            "is_accessible": True,
            "courts": [
                {"court_code": "K1", "court_name": "Court 1", "display_order": 1},
                {"court_code": "K2", "court_name": "Court 2", "display_order": 2},
            ],
        },
        {
            "venue_name": "Oxley Stadium",
            "venue_address": "15-49 Old Heidelberg Rd, Ringwood VIC",
            "display_order": 2,
            "is_accessible": True,
            "courts": [
                {"court_code": "O1", "court_name": "Court 1", "display_order": 1},
            ],
        },
    ],
    # Minimal age/grade/teams sample. Expand this to mirror your full matrix.
    "ages": [
        {
            "age_code": "U10",
            "age_name": "Under 10 Boys",
            "age_rank": 10,
            "gender": "M",
            "grades": [
                {
                    "grade_code": "A",
                    "grade_name": "U10 Boys A",
                    "grade_rank": 1,
                    "teams": [
                        {"team_code": "KIL-U10A-01", "team_name": "KBL U10A 1"},
                        {"team_code": "KIL-U10A-02", "team_name": "KBL U10A 2"},
                    ],
                },
                {
                    "grade_code": "B",
                    "grade_name": "U10 Boys B",
                    "grade_rank": 2,
                    "teams": [
                        {"team_code": "KIL-U10B-01", "team_name": "KBL U10B 1"},
                    ],
                },
            ],
        }
    ],
    # A few rounds and one round_settings record
    "rounds": [
        {"round_number": 1, "round_type": "REGULAR", "round_label": "Round 1"},
        {"round_number": 2, "round_type": "REGULAR", "round_label": "Round 2"},
        {"round_number": 3, "round_type": "REGULAR", "round_label": "Round 3"},
    ],
    "round_settings": [
        {"round_settings_number": 1},
    ],
}


# ======================================================================================
# Context and plan
# ======================================================================================


@dataclass
class SeedContext:
    session: Session
    settings: Any
    created_by_user_id: int
    dry_run: bool = False
    org_name_override: str | None = None


def run_seed_plan(ctx: SeedContext) -> list[tuple[str, tuple[int, int]]]:
    """
    Run all domain seeders in order.
    Returns a list of (domain_name, (created_count, existing_count)).
    """
    plan: list[tuple[str, Any]] = [
        ("users", seed_users),
        ("organisations", seed_organisations),
        ("user_permissions", seed_user_permissions),
        ("competitions", seed_competitions),
        ("seasons", seed_seasons),
        ("season_days", seed_season_days),
        ("venues", seed_venues),
        ("courts", seed_courts),
        ("ages", seed_ages),
        ("grades", seed_grades),
        ("teams", seed_teams),
        ("rounds", seed_rounds),
        ("round_settings", seed_round_settings),
        # ("time_slots", seed_time_slots),  # intentionally skipped for now
    ]

    results: list[tuple[str, tuple[int, int]]] = []
    for name, fn in plan:
        echo(f"→ Seeding {name} ...")
        created, existing = fn(ctx)
        echo(f"✓ {name}: created {created}, existing {existing}")
        results.append((name, (created, existing)))
    return results


# ======================================================================================
# Domain seeders
# ======================================================================================


def seed_users(ctx: SeedContext) -> tuple[int, int]:
    """
    Ensure the seed admin user exists. Uses unique 'email' for idempotency.
    """
    # Already ensured by CLI step usually, but harmless to repeat here.
    ensure_seed_admin_user(ctx.session)
    return (0, 1)  # We don't attempt to create arbitrary users here.


def seed_organisations(ctx: SeedContext) -> tuple[int, int]:
    """
    Insert the baseline Organisation (by slug) idempotently.
    """
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    slug = slugify(name)

    where = {"slug": slug}
    defaults: dict[str, Any] = {
        "organisation_name": name,
        # Some models also keep a display_name or similar; adjust if needed.
        # If you enforce created_by_user_id, set it if the column exists:
        # We'll set it defensively only if the model has that attribute.
    }

    # add created_by_user_id if column exists on Organisation
    if hasattr(Organisation, "created_by_user_id"):
        defaults["created_by_user_id"] = ctx.created_by_user_id

    org, created = get_or_create(ctx.session, Organisation, where, defaults)
    return (1 if created else 0, 0 if created else 1)


def seed_user_permissions(ctx: SeedContext) -> tuple[int, int]:
    """
    Grant the seed admin a permission for the baseline org.
    Unique key: (user_account_id, organisation_id).
    """
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org_slug = slugify(name)

    org = get_one_by(ctx.session, Organisation, {"slug": org_slug})
    user = get_one_by(ctx.session, UserAccount, {"email": "samuel@whitelinegroup.com.au"})

    where = {
        "user_account_id": user.user_account_id,
        "organisation_id": org.organisation_id,
    }
    defaults: dict[str, Any] = {}  # add default permission fields if your model requires any

    up, created = get_or_create(ctx.session, UserPermission, where, defaults)
    return (1 if created else 0, 0 if created else 1)


def seed_competitions(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org_slug = slugify(name)
    org = get_one_by(ctx.session, Organisation, {"slug": org_slug})

    comp_name = BASELINE["competition"]["name"]
    comp_slug = slugify(comp_name)

    where = {"organisation_id": org.organisation_id, "slug": comp_slug}
    defaults: dict[str, Any] = {"competition_name": comp_name}
    if hasattr(Competition, "created_by_user_id"):
        defaults["created_by_user_id"] = ctx.created_by_user_id

    comp, created = get_or_create(ctx.session, Competition, where, defaults)
    return (1 if created else 0, 0 if created else 1)


def seed_seasons(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})
    comp = get_one_by(
        ctx.session,
        Competition,
        {
            "organisation_id": org.organisation_id,
            "slug": slugify(BASELINE["competition"]["name"]),
        },
    )

    s = BASELINE["season"]
    season_name = s["name"]
    season_slug = slugify(season_name)

    where = {"competition_id": comp.competition_id, "slug": season_slug}
    defaults: dict[str, Any] = {
        "season_name": season_name,
        "starting_date": s["start_date"],
        "ending_date": s["end_date"],
        "visibility": "PUBLIC",
        "active": True,
    }
    if hasattr(Season, "created_by_user_id"):
        defaults["created_by_user_id"] = ctx.created_by_user_id

    season, created = get_or_create(ctx.session, Season, where, defaults)
    return (1 if created else 0, 0 if created else 1)


def seed_season_days(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})
    comp = get_one_by(
        ctx.session,
        Competition,
        {
            "organisation_id": org.organisation_id,
            "slug": slugify(BASELINE["competition"]["name"]),
        },
    )
    season = get_one_by(
        ctx.session,
        Season,
        {
            "competition_id": comp.competition_id,
            "slug": slugify(BASELINE["season"]["name"]),
        },
    )

    created = 0
    existing = 0

    def _default_day_window(week_day: int) -> tuple[time, time]:
        """
        Return a sensible default time window for a given weekday.
        You can tune this later or move to config/default_times when that table exists.
        """
        # Example: weekdays 16:00–22:00, weekends 08:00–22:00
        if week_day in (6, 7):  # Saturday=6, Sunday=7 (per your model)
            return time(8, 0), time(22, 0)
        return time(16, 0), time(22, 0)

    for sd in BASELINE["season_days"]:
        where = {"season_id": season.season_id, "week_day": sd["week_day"]}
        ws, we = _default_day_window(sd["week_day"])

        defaults: dict[str, Any] = {
            "season_day_name": sd["season_day_name"],
            "active": sd.get("active", False),
            "season_day_label": sd.get("display_label", sd["season_day_name"]),
            "week_day": sd["week_day"],  # ensure we pass through the weekday
            "window_start": sd.get("window_start", ws),
            "window_end": sd.get("window_end", we),
        }
        if hasattr(SeasonDay, "created_by_user_id"):
            defaults["created_by_user_id"] = ctx.created_by_user_id

        _, c = get_or_create(ctx.session, SeasonDay, where, defaults)
        if c:
            created += 1
        else:
            existing += 1

    return created, existing


def seed_venues(ctx: SeedContext) -> tuple[int, int]:
    created = 0
    existing = 0

    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})

    for v in BASELINE["venues"]:
        where = {"venue_name": v["venue_name"], "venue_address": v["venue_address"]}
        total_courts = len(v.get("courts", []))

        defaults: dict[str, Any] = {
            "display_order": v.get("display_order", 1),
            "accessible": v.get("accessible", True),
            "indoor": v.get("indoor", True),
            "total_courts": total_courts,
            "organisation_id": org.organisation_id,
        }
        if hasattr(Venue, "created_by_user_id"):
            defaults["created_by_user_id"] = ctx.created_by_user_id

        _, c = get_or_create(ctx.session, Venue, where, defaults)
        if c:
            created += 1
        else:
            existing += 1

    return created, existing


def seed_courts(ctx: SeedContext) -> tuple[int, int]:
    created = 0
    existing = 0

    for v in BASELINE["venues"]:
        venue = get_one_by(
            ctx.session,
            Venue,
            {"venue_name": v["venue_name"], "venue_address": v["venue_address"]},
        )
        for c_def in v.get("courts", []):
            where = {"venue_id": venue.venue_id, "court_code": c_def["court_code"]}
            defaults: dict[str, Any] = {
                "court_name": c_def.get("court_name", c_def["court_code"]),
                "display_order": c_def.get("display_order", 0),
            }
            if hasattr(Court, "created_by_user_id"):
                defaults["created_by_user_id"] = ctx.created_by_user_id

            _, c = get_or_create(ctx.session, Court, where, defaults)
            if c:
                created += 1
            else:
                existing += 1

    return created, existing


def seed_ages(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})
    comp = get_one_by(
        ctx.session,
        Competition,
        {
            "organisation_id": org.organisation_id,
            "slug": slugify(BASELINE["competition"]["name"]),
        },
    )
    season = get_one_by(
        ctx.session,
        Season,
        {
            "competition_id": comp.competition_id,
            "slug": slugify(BASELINE["season"]["name"]),
        },
    )
    # use Saturday only (index 0)
    sat = get_one_by(ctx.session, SeasonDay, {"season_id": season.season_id, "week_day": 6})

    created = 0
    existing = 0
    for a in BASELINE["ages"]:
        where = {"season_day_id": sat.season_day_id, "age_code": a["age_code"]}
        defaults: dict[str, Any] = {
            "age_name": a["age_name"],
            "age_rank": a["age_rank"],
            "gender": a.get("gender", "X"),
        }
        if hasattr(Age, "created_by_user_id"):
            defaults["created_by_user_id"] = ctx.created_by_user_id

        _, c = get_or_create(ctx.session, Age, where, defaults)
        if c:
            created += 1
        else:
            existing += 1

    return created, existing


def seed_grades(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})
    comp = get_one_by(
        ctx.session,
        Competition,
        {
            "organisation_id": org.organisation_id,
            "slug": slugify(BASELINE["competition"]["name"]),
        },
    )
    season = get_one_by(
        ctx.session,
        Season,
        {
            "competition_id": comp.competition_id,
            "slug": slugify(BASELINE["season"]["name"]),
        },
    )
    sat = get_one_by(ctx.session, SeasonDay, {"season_id": season.season_id, "week_day": 6})

    created = 0
    existing = 0
    for a in BASELINE["ages"]:
        age = get_one_by(
            ctx.session,
            Age,
            {"season_day_id": sat.season_day_id, "age_code": a["age_code"]},
        )
        for g in a.get("grades", []):
            where = {"age_id": age.age_id, "grade_code": g["grade_code"]}
            defaults: dict[str, Any] = {
                "grade_name": g["grade_name"],
                "grade_rank": g["grade_rank"],
            }
            if hasattr(Grade, "created_by_user_id"):
                defaults["created_by_user_id"] = ctx.created_by_user_id

            _, c = get_or_create(ctx.session, Grade, where, defaults)
            if c:
                created += 1
            else:
                existing += 1

    return created, existing


def seed_teams(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})
    comp = get_one_by(
        ctx.session,
        Competition,
        {
            "organisation_id": org.organisation_id,
            "slug": slugify(BASELINE["competition"]["name"]),
        },
    )
    season = get_one_by(
        ctx.session,
        Season,
        {
            "competition_id": comp.competition_id,
            "slug": slugify(BASELINE["season"]["name"]),
        },
    )
    sat = get_one_by(ctx.session, SeasonDay, {"season_id": season.season_id, "week_day": 6})

    created = 0
    existing = 0
    for a in BASELINE["ages"]:
        age = get_one_by(
            ctx.session,
            Age,
            {"season_day_id": sat.season_day_id, "age_code": a["age_code"]},
        )
        for g in a.get("grades", []):
            grade = get_one_by(
                ctx.session,
                Grade,
                {"age_id": age.age_id, "grade_code": g["grade_code"]},
            )
            for t in g.get("teams", []):
                where = {"grade_id": grade.grade_id, "team_code": t["team_code"]}
                defaults: dict[str, Any] = {"team_name": t.get("team_name", t["team_code"])}
                if hasattr(Team, "created_by_user_id"):
                    defaults["created_by_user_id"] = ctx.created_by_user_id

                _, c = get_or_create(ctx.session, Team, where, defaults)
                if c:
                    created += 1
                else:
                    existing += 1

    return created, existing


def seed_rounds(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})
    comp = get_one_by(
        ctx.session,
        Competition,
        {
            "organisation_id": org.organisation_id,
            "slug": slugify(BASELINE["competition"]["name"]),
        },
    )
    season = get_one_by(
        ctx.session,
        Season,
        {
            "competition_id": comp.competition_id,
            "slug": slugify(BASELINE["season"]["name"]),
        },
    )

    created = 0
    existing = 0
    for r in BASELINE["rounds"]:
        where = {"season_id": season.season_id, "round_number": r["round_number"]}
        defaults: dict[str, Any] = {
            "round_type": r.get("round_type", "REGULAR"),
            "round_label": r["round_label"],
        }
        if hasattr(Round, "created_by_user_id"):
            defaults["created_by_user_id"] = ctx.created_by_user_id

        _, c = get_or_create(ctx.session, Round, where, defaults)
        if c:
            created += 1
        else:
            existing += 1

    return created, existing


def seed_round_settings(ctx: SeedContext) -> tuple[int, int]:
    name = ctx.org_name_override or BASELINE["organisation"]["name"]
    org = get_one_by(ctx.session, Organisation, {"slug": slugify(name)})
    comp = get_one_by(
        ctx.session,
        Competition,
        {
            "organisation_id": org.organisation_id,
            "slug": slugify(BASELINE["competition"]["name"]),
        },
    )
    season = get_one_by(
        ctx.session,
        Season,
        {
            "competition_id": comp.competition_id,
            "slug": slugify(BASELINE["season"]["name"]),
        },
    )
    sat = get_one_by(ctx.session, SeasonDay, {"season_id": season.season_id, "week_day": 6})

    created = 0
    existing = 0
    for rs in BASELINE["round_settings"]:
        where = {
            "season_day_id": sat.season_day_id,
            "round_settings_number": rs["round_settings_number"],
        }
        defaults: dict[str, Any] = {}
        if hasattr(RoundSetting, "created_by_user_id"):
            defaults["created_by_user_id"] = ctx.created_by_user_id

        _, c = get_or_create(ctx.session, RoundSetting, where, defaults)
        if c:
            created += 1
        else:
            existing += 1

    return created, existing


# -----------------------------------------------------------------------------
# Test shims (used by tests/integration/test_seed_data.py, test_seed_flow.py)
# These are intentionally minimal and only seed Organisations for now.
# -----------------------------------------------------------------------------
@dataclass
class OrganisationSeed:
    name: str


@dataclass
class SeedPlan:
    organisations: list[OrganisationSeed]


class SeedItem(TypedDict, total=False):
    id: int | None
    name: str | None
    slug: str | None
    action: str  # "inserted" | "exists" (keep simple; test only reads name/slug)


class SeedResult(TypedDict):
    inserted: int
    updated: int
    skipped: int
    items: list[SeedItem]


def seed_from_plan(session: Session, plan: SeedPlan) -> SeedResult:
    """
    Minimal seeding used by tests:
      - creates/gets Organisation rows by slug.
      - returns a uniform summary dict.
    """
    items: list[SeedItem] = []

    seed_user = ensure_seed_admin_user(session)
    created_by_user_id = getattr(seed_user, "user_account_id", None)

    inserted = 0
    skipped = 0

    for org_seed in plan.organisations:
        org_name = org_seed.name.strip()
        org_slug = slugify(org_name)

        where = {"slug": org_slug}
        defaults: dict[str, Any] = {
            "organisation_name": org_name,
            "created_by_user_id": created_by_user_id,
        }

        org, created = get_or_create(session, Organisation, where, defaults)
        if created:
            inserted += 1
            action = "inserted"
        else:
            skipped += 1
            action = "exists"

        items.append(
            {
                "id": getattr(org, "organisation_id", None),
                "name": getattr(org, "organisation_name", org_name),
                "slug": getattr(org, "slug", org_slug),
                "action": action,
            }
        )

    result: SeedResult = {
        "inserted": inserted,
        "updated": 0,
        "skipped": skipped,
        "items": items,
    }
    return result


def seed_minimal(session: Session, org_name: str) -> SeedResult:
    """
    Convenience wrapper the tests import.
    """
    plan = SeedPlan(organisations=[OrganisationSeed(name=org_name)])
    return seed_from_plan(session, plan)
