# WHITELINE DATABASE ERD - INSTRUCTIONS FOR CHATGPT

## SECTION 0: Document Overview

### SECTION 0.1: PURPOSE OF THIS DOCUMENT
This document provides a complete schema reference for the Whiteline SportsHub PostgreSQL database. Its goals are:
- To serve as the authoritative schema definition for development, debugging, and knowledge integration.
- To provide ChatGPT with structured, exhaustive context about the database’s entities, relationships, triggers, and seeded data.
- To enable consistent and accurate generation of SQL queries that span multiple tables and relationships.

### SECTION 0.2: DOCUMENT STRUCTURE
The documentation is broken into six major sections:
1. Server Configuration - Overview of the local PostgreSQL server setup.
2. Database Overview — Complete table-by-table breakdown of columns, keys, constraints, and notes.
3. Entity Relationship Summary — Detailed mapping of relationships, traversals, and delete behavior.
4. Triggers & Functions — Full inventory of procedural logic and triggers embedded in the schema.
5. Seed / Bootstrap SQL — A record of all preloaded reference data (dates, public holidays, default times).
6. Enumerations Dictionary - Centralized list of all schema-wide enumerated values and check constraints, including their possible values and intended meanings. Used as a canonical reference for data validation and query generation.

### SECTION 0.3: DATABASE CONVENTIONS & GLOBAL NOTES
- Primary Keys: Every table has a SERIAL surrogate key (*_id).
- Foreign Keys: Always declared explicitly with REFERENCES constraints. Most child relationships cascade deletes, except in certain organisational entities (e.g., venues).
- Timestamps: Almost every table has created_at TIMESTAMPTZ DEFAULT NOW(). Some also have updated_at, published_at, or locked_at.
- Audit Attribution: Key actions reference users(user_account_id) (created_by_user_id, updated_by_user_id, etc.).
- Enumerations: Implemented via CHECK constraints on text columns (e.g., round_type, restriction_type).
- Uniqueness: Business rules enforced with UNIQUE constraints (e.g., one court per venue_id, one season_day per weekday).

### SECTION 0.4: HOW CHATGPT SHOULD USE THIS DOCUMENT
- Use Section 1 when needing to know columns, constraints, or defaults.
- Use Section 2 when writing queries that join across tables. Follow traversal paths as outlined.
- Use Section 3 to understand automated behaviors (e.g., auto-generated labels, cascade syncs).
- Use Section 4 to know what data is already pre-populated and available without inserts.

### SECTION 0.5: INTERPRETATION GUIDANCE
- Always respect uniqueness and constraints when generating INSERT or UPDATE.
- Assume cascade delete effects when reasoning about data removal.
- Use pre-seeded data (from Section 4) when referencing baseline entities like dates, default_times, or public_holidays.
- Treat denormalized output tables (final_game_schedule, final_bye_schedule) as immutable snapshots, not sources of truth.

## SECTION 1: Server Configuration
### SECTION 1.1: SERVER INFORMATION

SERVER NAME: Whiteline
HOST/ADDRESS: localhost
PORT NUMBER: 5432
MAINTENANCE DATABASE: postgres
USERNAME: samuelellis
CONNECTION NOTES:
- Password authentication enabled
- SSL removed
- RBAC (Role-Based Access Control) removed
- Backups and logging disabled per dev setup

### SECTION 1.2: DATABASE OVERVIEW
DATABASE NAME: whiteline_db
DESCRIPTION: Primary project database for the Whiteline SportsHub system. Stores all scheduling-related data.
ENCODING: UTF-8 (default)
DEFAULT SCHEMA: public

### SECTION 1.3: CONNECTION SETUP (AUTOMATED)
CONNECTED APPLICATIONS: Visual Studio Code
METHOD: SQLAlchemy ORM + psycopg v3 driver
CONNECTION STRING: postgresql+psycopg://samuelellis:{password}@localhost:5432/whiteline_db
PASSWORD: `quote("5-e3CpU0z[t7416\>uS<9z{JA")`
ROLE PERMISSIONS: Single user `samuelellis` has full superuser access

### SECTION 1.4: BACKUP & RESTORE PROCESS
BACKUP METHOD: Not currently in use
BACKUP FREQUENCY: N/A
BACKUP STORAGE: N/A
RESTORE METHOD: N/A

(Note: This is a prototype environment; no data retention or fault tolerance measures have been configured.)

### SECTION 1.5: ENVIRONMENT CONFIGURATION NOTES
HOSTING LOCATION: Local development machine
ENVIRONMENT TYPE: Development / Testing
CUSTOM CONFIGURATION:
- SSL removed
- Role-Based Access Control removed
- No write-ahead logging (WAL) enabled
- No PostgreSQL extensions active (e.g., pg_stat_statements)




## SECTION 2: Database Overview
### SECTION 2.0: INTERPRETATION (for ChatGPT)
- Treat each table description as authorit- ative for columns, keys, defaults, and constraints.
- Read the PURPOSE line as a plain-language explanation of what the table represents. Use this to infer the table’s role in scheduling or orchestration.

⸻

Use the COLUMNS list to:
- Identify primary keys ([PK]), alternate keys ([AK]), and foreign keys ([FK]).
- Note inline constraints: [NOT NULL], [NULLABLE], [default: …], and any CHECK enumerations.
- Recognize uniqueness rules via [AK] or UNIQUE notes in the NOTES block.

⸻

Use the NOTES block to understand:
- How the table is referenced elsewhere.
- Any automatic behaviors (e.g., triggers, cascade deletes, synchronization).
- Which indexes exist for performance and query guidance.

⸻

When generating SQL:
- Always enforce uniqueness constraints when inserting new rows.
- Use the explicit FK references to join tables — rely on column names and references shown here rather than guessing.
- Apply enumerations exactly as written in the CHECK constraints or from the Enumerations Dictionary (Section 5).

⸻

When reasoning about schema traversal:
- Look for [FK] to identify join directions.
- Assume ON DELETE CASCADE if explicitly stated; otherwise, assume NO ACTION.
- Consider created_by_user_id, updated_by_user_id, published_by_user_id as attribution-only, not as hierarchy links.

### SECTION 2.1: THE CORE ELEMENTS
TABLE: dates
PURPOSE: Canonical calendar dimension for all date logic (weekends, ISO week, holiday flags).
COLUMNS:
- [PK] date_id SERIAL [NOT NULL]
- [AK] date_value DATE [NOT NULL]
- []   date_day TEXT [NOT NULL]  // CHECK: 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'
- []   calendar_year INTEGER [NOT NULL]
- []   iso_week_int INTEGER [NOT NULL]
- []   is_weekend BOOLEAN [NOT NULL]
- []   is_public_holiday BOOLEAN [NOT NULL]
NOTES:
- Holds one row per calendar date; date_value is unique.
- Used by round_dates and to tag holidays via public_holidays; is_public_holiday is also stored here for quick filters.
- Indexed: (date_value) via idx_dates_date_value.

⸻

TABLE: public_holidays
PURPOSE: Named public holidays per date and Australian region.
COLUMNS:
- [PK] public_holiday_id SERIAL [NOT NULL]
- [FK] date_id INTEGER [NOT NULL] [references: dates(date_id)]
- []   holiday_name TEXT [NOT NULL]
- []   holiday_region TEXT [NOT NULL]  // CHECK: 'CTH', 'TAS', 'VIC', 'NSW', 'ACT', 'QLD', 'SA', 'NT', 'WA'
NOTES:
- Joins to dates for holiday date; region-scoped names. Insert logic prevents duplicates.
- Typical filters: by date_id and holiday_region.
- Indexed: (none defined).

⸻

TABLE: default_times
PURPOSE: Normalized catalog of times-of-day (lookup).
COLUMNS:
- [PK] time_id SERIAL [NOT NULL]
- [AK] time_value TIME [NOT NULL]
NOTES:
- Referenced by time_slots.start_time_id / end_time_id.
- Seed includes every second of the day (00:00:00–23:59:59).
- Indexed: (time_value) via idx_default_times_time_value.

### SECTION 2.2: THE ORGANISATIONAL ENTITIES
TABLE: users
PURPOSE: Application user accounts (creators, publishers, run owners, etc.).
COLUMNS:
- [PK] user_account_id SERIAL [NOT NULL]
- []   display_name TEXT [NOT NULL]
- [AK] email TEXT [NOT NULL]
- []   is_active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
NOTES:
- Referenced throughout for attribution (created_by_user_id, updated_by_user_id, locked_by_user_id, published_by_user_id).
- Indexed: (none defined on this table).

⸻

TABLE: organisations
PURPOSE: Tenant boundary; top-level owner of competitions/venues.
COLUMNS:
- [PK] organisation_id SERIAL [NOT NULL]
- [AK] organisation_name TEXT [NOT NULL]
- []   time_zone TEXT [NULLABLE]
- []   country_code TEXT [NULLABLE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Parent of competitions and venues.
- Indexed: (created_by_user_id) via idx_organisations_created_by.

⸻

TABLE: competitions
PURPOSE: Competition/program within an organisation.
COLUMNS:
- [PK] competition_id SERIAL [NOT NULL]
- [FK] organisation_id INTEGER [NOT NULL] [references: organisations(organisation_id)]
- []   competition_name TEXT [NOT NULL]
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (organisation_id, competition_name).
- Parent of seasons.
- Indexed: (organisation_id) via idx_competitions_org; (created_by_user_id) via idx_competitions_created_by.

⸻

TABLE: seasons
PURPOSE: Season window within a competition, with visibility and activation flags.
COLUMNS:
- [PK] season_id SERIAL [NOT NULL]
- [FK] competition_id INTEGER [NOT NULL] [references: competitions(competition_id)]
- []   season_name TEXT [NOT NULL]
- []   starting_date DATE [NULLABLE]
- []   ending_date DATE [NULLABLE]
- []   visibility TEXT [NOT NULL]  // CHECK: 'PRIVATE', 'INTERNAL', 'PUBLIC'
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (competition_id, season_name).
- Parent of season_days and rounds.
- Indexed: (competition_id) via idx_seasons_comp; (visibility, active) via idx_seasons_visibility_active; (created_by_user_id) via idx_seasons_created_by.

⸻

TABLE: season_days
PURPOSE: Per-season weekday configuration, label, and time window.
COLUMNS:
- [PK] season_day_id SERIAL [NOT NULL]
- [FK] season_id INTEGER [NOT NULL] [references: seasons(season_id)]
- []   season_day_name TEXT [NOT NULL]  // CHECK: 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'
- []   season_day_label TEXT [NULLABLE]
- []   week_day INTEGER [NOT NULL]  // CHECK: 1, 2, 3, 4, 5, 6, 7
- []   window_start TIME [NOT NULL]
- []   window_end TIME [NOT NULL]
- []   active BOOLEAN [NULLABLE] [default: FALSE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (season_id, season_day_name) and UNIQUE (season_id, week_day).
- Parent of time_slots, ages, court_times (via FKs elsewhere), round_settings.
- Indexed: (season_id) via idx_season_days_season; (week_day) via idx_season_days_week_day; (active) via idx_season_days_active.

⸻

TABLE: venues
PURPOSE: Physical sites hosting courts; maintains a live count of courts.
COLUMNS:
- [PK] venue_id SERIAL [NOT NULL]
- [FK] organisation_id INTEGER [NOT NULL] [references: organisations(organisation_id)]
- []   venue_name TEXT [NOT NULL]
- []   venue_address TEXT [NOT NULL]
- []   display_order INTEGER [NOT NULL]
- []   latitude NUMERIC(9,6) [NULLABLE]
- []   longitude NUMERIC(9,6) [NULLABLE]
- []   indoor BOOLEAN [NULLABLE] [default: TRUE]
- []   accessible BOOLEAN [NULLABLE] [default: TRUE]
- []   total_courts INTEGER [NOT NULL]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (venue_name, venue_address).
- Parent of courts; total_courts is auto-synchronized by triggers when courts are inserted/updated/deleted.
- Indexed: (created_by_user_id) via idx_venues_created_by.

⸻

TABLE: courts
PURPOSE: Individual playing areas at a venue.
COLUMNS:
- [PK] court_id SERIAL [NOT NULL]
- [FK] venue_id INTEGER [NOT NULL] [references: venues(venue_id)]
- []   court_code VARCHAR(20) [NOT NULL]
- []   court_name TEXT [NOT NULL]
- []   display_order INTEGER [NOT NULL]
- []   surface TEXT [NULLABLE]
- []   indoor BOOLEAN [NULLABLE] [default: TRUE]
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (venue_id, court_code), UNIQUE (venue_id, court_name), UNIQUE (venue_id, display_order).
- Referenced by court_times and court_rankings.
- Indexed: (venue_id) via idx_courts_venue; (active) via idx_courts_active.

### SECTION 2.3: THE ROUND ENTITIES
TABLE: rounds
PURPOSE: Logical round markers for a season (grading, regular, finals).
COLUMNS:
- [PK] round_id SERIAL [NOT NULL]
- [FK] season_id INTEGER [NOT NULL] [references: seasons(season_id)]
- []   round_number INTEGER [NOT NULL]
- []   round_label TEXT [NOT NULL]
- []   round_type TEXT [NOT NULL]  // CHECK: 'GRADING', 'REGULAR', 'FINALS'
- []   round_status TEXT [NOT NULL] [default: ‘PLANNED’]  // CHECK: 'PLANNED', 'SCHEDULED', 'PUBLISHED', 'COMPLETED', 'CANCELLED'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
- []   published_at TIMESTAMPTZ [NULLABLE]
NOTES:
- Alternate keys: UNIQUE (season_id, round_number) and UNIQUE (season_id, round_label).
- Parent to round_dates and linked to round_settings via round_groups.
- Indexed: (season_id) via idx_rounds_season; (round_type, round_status) via idx_rounds_type_status; (created_by_user_id) via idx_rounds_created_by.

⸻

TABLE: round_dates
PURPOSE: Assign one or more calendar dates to a round.
COLUMNS:
- [PK] round_date_id SERIAL [NOT NULL]
- [FK] date_id INTEGER [NOT NULL] [references: dates(date_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_id, date_id).
- Indexed: (round_id) via idx_round_dates_round; (date_id) via idx_round_dates_date.

⸻

TABLE: round_settings
PURPOSE: Configuration bundle per season_day and setting number.
COLUMNS:
- [PK] round_setting_id SERIAL [NOT NULL]
- [FK] season_day_id INTEGER [NOT NULL] [references: season_days(season_day_id)]
- []   round_settings_number INTEGER [NOT NULL]
- []   rules JSONB [NULLABLE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (season_day_id, round_settings_number).
- Used by round_groups, court_times, and all constraints tables.
- Indexed: (season_day_id) via idx_round_settings_day.

⸻

TABLE: round_groups
PURPOSE: Binds a round to a specific round_setting.
COLUMNS:
- [PK] round_group_id SERIAL [NOT NULL]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_id, round_setting_id).
- This mapping declares which setting governs a particular round.
- Indexed: (round_id) via idx_round_groups_round; (round_setting_id) via idx_round_groups_setting.

### SECTION 2.4: THE SCHEDULING SETUP
TABLE: court_rankings
PURPOSE: Preferred court order per (season_day, round_setting) and court.
COLUMNS:
- [PK] court_rank_id SERIAL [NOT NULL]
- [FK] court_id INTEGER [NOT NULL] [references: courts(court_id)]
- [FK] season_day_id INTEGER [NOT NULL] [references: season_days(season_day_id)]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- []   court_rank INTEGER [NOT NULL]
- []   overridden BOOLEAN [NULLABLE] [default: FALSE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
- []   updated_at TIMESTAMPTZ [NULLABLE]
- [FK] updated_by_user_id INTEGER [NULLABLE] [references: users(user_account_id)]
NOTES:
- New inserts automatically mark older matching rows as overridden = TRUE (triggered behavior).
- Used by allocation logic to rank slots by court preference.
- Indexed: (season_day_id, round_setting_id) via idx_court_rankings_day_setting; (court_id) via idx_court_rankings_court.

⸻

TABLE: time_slots
PURPOSE: Time windows available for a season_day (with both normalized IDs and denormalized times).
COLUMNS:
- [PK] time_slot_id SERIAL [NOT NULL]
- [FK] season_day_id INTEGER [NOT NULL] [references: season_days(season_day_id)]
- [FK] start_time_id INTEGER [NOT NULL] [references: default_times(time_id)]
- [FK] end_time_id INTEGER [NOT NULL] [references: default_times(time_id)]
- []   start_time TIME [NOT NULL]
- []   end_time TIME [NOT NULL]
- []   time_slot_label TEXT [NOT NULL]
- []   buffer_minutes INTEGER [NOT NULL]
- []   duration_minutes INTEGER [NOT NULL]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (season_day_id, start_time, end_time) and UNIQUE (season_day_id, time_slot_label).
- Label is auto-generated from start_time if blank (trigger).
- Indexed: (season_day_id) via idx_time_slots_day; (start_time, end_time) via idx_time_slots_start_end.

⸻

TABLE: court_times
PURPOSE: Concrete schedulable cells (season_day × round_setting × court × time_slot), with availability/lock state.
COLUMNS:
- [PK] court_time_id SERIAL [NOT NULL]
- [FK] season_day_id INTEGER [NOT NULL] [references: season_days(season_day_id)]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- [FK] court_id INTEGER [NOT NULL] [references: courts(court_id)]
- [FK] time_slot_id INTEGER [NOT NULL] [references: time_slots(time_slot_id)]
- []   availability_status TEXT [NOT NULL] [default: ‘AVAILABLE’]  // CHECK: 'AVAILABLE', 'BLOCKED', 'MAINTENANCE', 'EVENT'
- []   lock_state TEXT [NOT NULL] [default: ‘OPEN’]                // CHECK: 'OPEN', 'LOCKED'
- []   block_reason TEXT [NULLABLE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
- []   updated_at TIMESTAMPTZ [NULLABLE]
- [FK] updated_by_user_id INTEGER [NULLABLE] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (season_day_id, round_setting_id, court_id, time_slot_id).
- Central supply for scheduling; referenced by restrictions and allocations.
- Indexed: (season_day_id, round_setting_id) via idx_court_times_day_setting; (court_id) via idx_court_times_court; (time_slot_id) via idx_court_times_time_slot.

⸻

TABLE: ages
PURPOSE: Age groups per season_day with ranking and required games.
COLUMNS:
- [PK] age_id SERIAL [NOT NULL]
- [FK] season_day_id INTEGER [NOT NULL] [references: season_days(season_day_id)]
- []   age_code VARCHAR(20) [NOT NULL]
- []   age_name TEXT [NOT NULL]
- []   gender TEXT [NULLABLE]
- []   age_rank INTEGER [NOT NULL]
- []   age_required_games INTEGER [NULLABLE]
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (season_day_id, age_code), UNIQUE (season_day_id, age_name), UNIQUE (season_day_id, age_rank).
- Parent of grades; used by constraints.
- Indexed: (season_day_id) via idx_ages_day; (active) via idx_ages_active.

⸻

TABLE: grades
PURPOSE: Grades within an age, with ranking and optional bye requirement.
COLUMNS:
- [PK] grade_id SERIAL [NOT NULL]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- []   grade_code VARCHAR(20) [NOT NULL]
- []   grade_name TEXT [NOT NULL]
- []   grade_rank INTEGER [NOT NULL]
- []   grade_required_games INTEGER [NULLABLE]
- []   bye_requirement BOOLEAN [NULLABLE] [default: FALSE]
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   display_colour TEXT [NULLABLE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (age_id, grade_code), UNIQUE (age_id, grade_name), UNIQUE (age_id, grade_rank).
- Parent of teams; referenced in constraints and allocations.
- Indexed: (age_id) via idx_grades_age; (active) via idx_grades_active.

⸻

TABLE: teams
PURPOSE: Teams participating in a grade.
COLUMNS:
- [PK] team_id SERIAL [NOT NULL]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- []   team_code VARCHAR(20) [NOT NULL]
- []   team_name TEXT [NULLABLE]
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (grade_id, team_code) and UNIQUE (grade_id, team_name).
- Referenced by P3 allocations and final/saved schedules.
- Indexed: (grade_id) via idx_teams_grade; (active) via idx_teams_active.

### SECTION 2.5: THE SCHEDULING CONSTRAINTS
TABLE: age_round_constraints
PURPOSE: Declares which ages are in-scope for a given round_setting.
COLUMNS:
- [PK] age_round_constraint_id SERIAL [NOT NULL]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_setting_id, age_id).
- Drives which ages can be scheduled under that setting.
- Indexed: (round_setting_id, age_id) via idx_age_round_constraints_keys.

⸻

TABLE: grade_round_constraints
PURPOSE: Declares which grades are in-scope for a given round_setting (age carried for convenience).
COLUMNS:
- [PK] grade_round_constraint_id SERIAL [NOT NULL]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- []   active BOOLEAN [NULLABLE] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_setting_id, grade_id).
- Narrowing from age to specific grades for the setting.
- Indexed: (round_setting_id, grade_id) via idx_grade_round_constraints_keys.

⸻

TABLE: allocation_settings
PURPOSE: Restriction flags at (round_setting, age, grade) granularity.
COLUMNS:
- [PK] allocation_setting_id SERIAL [NOT NULL]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- []   restricted BOOLEAN [NULLABLE] [default: FALSE]
- []   restriction_type TEXT [NOT NULL] [default: ‘NONE’]  // CHECK: 'NONE', 'AGE', 'GRADE', 'DUAL'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
- []   updated_at TIMESTAMPTZ [NULLABLE]
- [FK] updated_by_user_id INTEGER [NULLABLE] [references: users(user_account_id)]
NOTES:
- No alternate keys; multiple rows per tuple are allowed (caller ensures uniqueness if desired).
- Used by P2 to govern eligibility/priority.
- Indexed: (none defined).

⸻

TABLE: age_court_restrictions
PURPOSE: Forbid or explicitly scope Age to specific court_time under a round_setting.
COLUMNS:
- [PK] age_court_restriction_id SERIAL [NOT NULL]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] court_time_id INTEGER [NOT NULL] [references: court_times(court_time_id)]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_setting_id, age_id, court_time_id).
- Indexed: (round_setting_id, age_id, court_time_id) via idx_age_court_restrictions_keys.

⸻

TABLE: grade_court_restrictions
PURPOSE: Grade-level or dual restrictions for specific court_time under a round_setting.
COLUMNS:
- [PK] grade_court_restriction_id SERIAL [NOT NULL]
- [FK] round_setting_id INTEGER [NOT NULL] [references: round_settings(round_setting_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] court_time_id INTEGER [NOT NULL] [references: court_times(court_time_id)]
- []   restriction_type TEXT [NOT NULL]  // CHECK: 'GRADE', 'DUAL'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_setting_id, grade_id, court_time_id).
- Indexed: (round_setting_id, grade_id, court_time_id) via idx_grade_court_restrictions_keys.

### SECTION 2.6: THE ORCHESTRATION & AUDIT ENTITIES
TABLE: scheduling_runs
PURPOSE: Orchestrated scheduling attempt state, idempotency, metrics, and lifecycle.
COLUMNS:
- [PK] run_id SERIAL [NOT NULL]
- [FK] season_id INTEGER [NOT NULL] [references: seasons(season_id)]
- [FK] season_day_id INTEGER [NOT NULL] [references: season_days(season_day_id)]
- []   run_status TEXT [NOT NULL]  // CHECK: 'PENDING', 'RUNNING', 'FAILED', 'SUCCEEDED', 'ABANDONED'
- []   process_type TEXT [NOT NULL]  // CHECK: 'INITIAL', 'MID'
- []   run_type TEXT [NULLABLE]  // CHECK: 'I_RUN_1', 'I_RUN_2', 'M_RUN_1', 'M_RUN_2', 'M_RUN_3'
- []   s1_check_results TEXT [NOT NULL]  // CHECK: 'NEW_INITIAL', 'NEW_MID', 'RESTART_INITIAL', 'RESTART_MID', 'SAVE_INITIAL', 'SAVE_MID'
- []   round_ids JSONB [NOT NULL]
- []   seed_master TEXT [NOT NULL]
- []   resume_checkpoint TEXT [NOT NULL]  // CHECK: 'BEFORE_P2', 'AFTER_P2_BEFORE_P3', 'AFTER_P3_BEFORE_FINALISE', 'FINALISED'
- []   config_hash TEXT [NULLABLE]
- [AK] idempotency_key TEXT [NOT NULL]
- []   metrics JSONB [NULLABLE]
- []   error_code TEXT [NULLABLE]
- []   error_details JSONB [NULLABLE]
- []   started_at TIMESTAMPTZ [NULLABLE]
- []   finished_at TIMESTAMPTZ [NULLABLE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Single-run record controlling all staging and output entities.
- Indexed: (season_day_id) via idx_runs_season_day; (run_status) via idx_runs_status; (process_type) via idx_runs_process_type; (created_at DESC) via idx_runs_created_at; (created_by_user_id) via idx_runs_created_by.

⸻

TABLE: scheduling_run_events
PURPOSE: Timeline of run events (info/warn/error) by stage.
COLUMNS:
- [PK] event_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- []   event_time TIMESTAMPTZ [NULLABLE] [default: NOW()]
- []   stage TEXT [NOT NULL]  // CHECK: 'STEP1', 'STEP2', 'STEP3', 'STEP4', 'STEP5', 'FINALISE'
- []   severity TEXT [NOT NULL]  // CHECK: 'INFO', 'WARN', 'ERROR'
- []   event_message TEXT [NOT NULL]
- []   context JSONB [NULLABLE]
NOTES:
- Append-only log for auditing and debugging of a run.
- Indexed: (run_id) via idx_run_events_run; (stage) via idx_run_events_stage; (severity) via idx_run_events_severity; (event_time DESC) via idx_run_events_time.

⸻

TABLE: scheduling_locks
PURPOSE: Enforces exclusive orchestration per season_day.
COLUMNS:
- [PK] lock_id SERIAL [NOT NULL]
- [FK] season_day_id INTEGER [NOT NULL] [references: season_days(season_day_id)]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- []   locked_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] locked_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (season_day_id) ensures only one runner per day.
- Indexed: (none defined).

⸻

TABLE: run_exports
PURPOSE: Records of exported artifacts per run.
COLUMNS:
- [PK] export_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- []   export_type TEXT [NOT NULL]  // CHECK: 'CSV', 'PDF', 'ZIP', 'XLSX'
- [AK] file_path TEXT [NOT NULL]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
NOTES:
- Alternate keys: UNIQUE (run_id, export_type); file_path is unique as well.
- Indexed: (run_id) via idx_run_exports_run.

⸻

TABLE: run_constraints_snapshot
PURPOSE: JSON snapshot of constraints at key phases for a run.
COLUMNS:
- [PK] snapshot_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- []   phase TEXT [NOT NULL]  // CHECK: 'P2', 'P3', 'COMPOSITE'
- []   constraints_json JSONB [NOT NULL]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
NOTES:
- Stores point-in-time constraint bundles for reproducibility.
- Indexed: (run_id) via idx_run_constraints_snapshot_run.

### SECTION 2.7: THE STAGING AREAS
TABLE: p2_allocations
PURPOSE: Phase 2 allocations of ages/grades to court_time per run/round.
COLUMNS:
- [PK] p2_allocation_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] court_time_id INTEGER [NOT NULL] [references: court_times(court_time_id)]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (run_id, round_id, court_time_id) to prevent double booking a slot in P2.
- Indexed: (run_id, round_id) via idx_p2_allocations_run_round; (court_time_id) via idx_p2_allocations_ct.

⸻

TABLE: p3_game_allocations
PURPOSE: Phase 3 team pairings on allocated slots.
COLUMNS:
- [PK] p3_game_allocation_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- [FK] p2_allocation_id INTEGER [NULLABLE] [references: p2_allocations(p2_allocation_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] team_a_id INTEGER [NOT NULL] [references: teams(team_id)]
- [FK] team_b_id INTEGER [NOT NULL] [references: teams(team_id)]
- [FK] court_time_id INTEGER [NOT NULL] [references: court_times(court_time_id)]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (run_id, round_id, court_time_id) ensures one game per slot.
- Indexed: (run_id, round_id) via idx_p3_games_run_round; (court_time_id) via idx_p3_games_ct; (team_a_id, team_b_id) via idx_p3_games_teams.

⸻

TABLE: p3_bye_allocations
PURPOSE: Teams assigned a bye in P3, with classified reason.
COLUMNS:
- [PK] p3_bye_allocation_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] team_id INTEGER [NOT NULL] [references: teams(team_id)]
- []   bye_reason TEXT [NOT NULL]  // CHECK: 'ODD_TEAMS', 'ERROR_LOOP', 'CONSTRAINT', 'MANUAL_OVERRIDE'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (run_id, round_id, team_id).
- Indexed: (run_id, round_id) via idx_p3_byes_run_round; (team_id) via idx_p3_byes_team.

⸻

TABLE: staging_diffs
PURPOSE: Change log for staging entities (add/change/remove) with before/after JSON.
COLUMNS:
- [PK] diff_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- []   entity_type TEXT [NOT NULL]  // CHECK: 'P2_ALLOCATION', 'P3_ALLOCATION', 'COMPOSITE_ALLOCATION'
- []   entity_id TEXT [NOT NULL]
- []   change_type TEXT [NOT NULL]  // CHECK: 'ADD', 'CHANGE', 'REMOVE'
- []   before_json JSONB [NULLABLE]
- []   after_json JSONB [NULLABLE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Audits transformations to staging data across phases.
- Indexed: (run_id) via idx_staging_diffs_run; (entity_type, entity_id) via idx_staging_diffs_entity.

### SECTION 2.8: THE SCHEDULING OUPUTS
TABLE: saved_games
PURPOSE: Persisted game rows at checkpoints (after P2, after P3, finalised).
COLUMNS:
- [PK] saved_game_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] team_a_id INTEGER [NOT NULL] [references: teams(team_id)]
- [FK] team_b_id INTEGER [NOT NULL] [references: teams(team_id)]
- [FK] court_time_id INTEGER [NOT NULL] [references: court_times(court_time_id)]
- []   game_status TEXT [NOT NULL]  // CHECK: 'AFTER_P2_BEFORE_P3', 'AFTER_P3_BEFORE_FINALISE', 'FINALISED'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (run_id, round_id, court_time_id).
- Indexed: (run_id, round_id) via idx_saved_games_run_round; (court_time_id) via idx_saved_games_ct.

⸻

TABLE: saved_byes
PURPOSE: Persisted bye rows at checkpoints.
COLUMNS:
- [PK] saved_bye_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] team_id INTEGER [NOT NULL] [references: teams(team_id)]
- []   bye_reason TEXT [NULLABLE]  // CHECK: 'ODD_TEAMS', 'ERROR_LOOP', 'CONSTRAINT', 'MANUAL_OVERRIDE'
- []   game_status TEXT [NOT NULL]  // CHECK: 'AFTER_P2_BEFORE_P3', 'AFTER_P3_BEFORE_FINALISE', 'FINALISED'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (run_id, round_id, team_id).
- Indexed: (run_id, round_id) via idx_saved_byes_run_round; (team_id) via idx_saved_byes_team.

⸻

TABLE: final_game_schedule
PURPOSE: Denormalized, publish-ready fixture rows (immutable snapshot).
COLUMNS:
- [PK] final_game_schedule_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] team_a_id INTEGER [NOT NULL] [references: teams(team_id)]
- [FK] team_b_id INTEGER [NOT NULL] [references: teams(team_id)]
- [FK] court_time_id INTEGER [NOT NULL] [references: court_times(court_time_id)]
- []   game_date DATE [NOT NULL]
- []   game_name TEXT [NOT NULL]
- []   organisation_name TEXT [NOT NULL]
- []   competition_name TEXT [NOT NULL]
- []   season_name TEXT [NOT NULL]
- []   gender TEXT [NULLABLE]
- []   venue_name TEXT [NOT NULL]
- []   court_name TEXT [NOT NULL]
- []   start_time TIME [NOT NULL]
- []   age_name TEXT [NOT NULL]
- []   grade_name TEXT [NOT NULL]
- []   team_a_name TEXT [NOT NULL]
- []   team_b_name TEXT [NOT NULL]
- []   game_status TEXT [NULLABLE] [default: ‘FINALISED’]  // CHECK: 'FINALISED', 'CANCELLED', 'FORFEITED', 'COMPLETED'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
- []   published_at TIMESTAMPTZ [NULLABLE]
- [FK] published_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_id, court_time_id).
- All names/times are denormalized for export stability.
- Indexed: (round_id) via idx_final_games_round; (court_time_id) via idx_final_games_ct.

⸻

TABLE: final_bye_schedule
PURPOSE: Denormalized, publish-ready bye rows (immutable snapshot).
COLUMNS:
- [PK] final_bye_schedule_id SERIAL [NOT NULL]
- [FK] run_id INTEGER [NOT NULL] [references: scheduling_runs(run_id)]
- [FK] round_id INTEGER [NOT NULL] [references: rounds(round_id)]
- [FK] age_id INTEGER [NOT NULL] [references: ages(age_id)]
- [FK] grade_id INTEGER [NOT NULL] [references: grades(grade_id)]
- [FK] team_id INTEGER [NOT NULL] [references: teams(team_id)]
- []   bye_date DATE [NOT NULL]
- []   bye_name TEXT [NOT NULL]
- []   organisation_name TEXT [NOT NULL]
- []   competition_name TEXT [NOT NULL]
- []   season_name TEXT [NOT NULL]
- []   gender TEXT [NULLABLE]
- []   age_name TEXT [NOT NULL]
- []   grade_name TEXT [NOT NULL]
- []   team_name TEXT [NOT NULL]
- []   bye_reason TEXT [NOT NULL]  // CHECK: 'ODD_TEAMS', 'ERROR_LOOP', 'CONSTRAINT', 'MANUAL_OVERRIDE'
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
- [FK] created_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
- []   published_at TIMESTAMPTZ [NULLABLE]
- [FK] published_by_user_id INTEGER [NOT NULL] [references: users(user_account_id)]
NOTES:
- Alternate keys: UNIQUE (round_id, team_id).
- Indexed: (round_id) via idx_final_byes_round; (team_id) via idx_final_byes_team.

### SECTION 2.9: THE AUTHENTICATION & PERMISSIONS ENTITIES
TABLE: user_permissions
PURPOSE: Per-organisation capability flags for a user.
COLUMNS:
- [PK] permission_id SERIAL [NOT NULL]
- [FK] user_account_id INTEGER [NOT NULL] [references: users(user_account_id)]
- [FK] organisation_id INTEGER [NOT NULL] [references: organisations(organisation_id)]
- []   can_schedule BOOLEAN [NOT NULL] [default: TRUE]
- []   can_approve BOOLEAN [NOT NULL] [default: TRUE]
- []   can_export BOOLEAN [NOT NULL] [default: TRUE]
- []   created_at TIMESTAMPTZ [NULLABLE] [default: NOW()]
NOTES:
- Alternate keys: UNIQUE (user_account_id, organisation_id) ensures one row per user–org pair.
- Indexed: (user_account_id) via idx_user_permissions_user; (organisation_id) via idx_user_permissions_org.


## SECTION 3: Entity Relationship Summary
### SECTION 3.0: INTERPRETATION (for ChatGPT)
This section expresses relationships as traversal paths. Each bullet shows the parent-to-child link using the format: TABLE_A(pk) → TABLE_B(fk=…)
- pk denotes the parent’s primary key.
- fk=… denotes the child’s foreign key column.

⸻

Cardinality is implied:
- *1—→ means “one-to-many” (a parent can have many children).
- 1—1→ means “one-to-one”.

⸻

- Delete behavior is explicitly noted in square brackets, e.g. [ON DELETE CASCADE]. If not noted, assume NO ACTION.
- Path examples illustrate how to traverse multiple joins to reach leaf tables. Use these as templates for multi-table SQL.

⸻

When generating queries:
- Always follow the traversal paths exactly as shown — this ensures correct join order and prevents orphan logic.
- Use reverse traversal (child → parent) by inverting the FK direction if you need context, e.g., from teams back to organisations.

⸻

- Where multiple traversal options exist (e.g., round ↔ setting ↔ group), rely on the documented path examples to avoid ambiguous joins.
- Treat “Path Examples” and “Recipes” as canonical query blueprints. They are the safest starting points when building SELECT statements across multiple entities.
- “Cardinality & Delete Behavior Cheat-Sheet” is a quick reference: it dictates lifecycle rules (what gets deleted automatically, what persists). Always respect these when reasoning about deletions or data cleanup.

### SECTION 3.1: TENANT & COMPETITION HIERARCHY
Organisation → Competition → Season:
- organisations(organisation_id) *1—→ competitions(organisation_id) [ON DELETE CASCADE]
- competitions(competition_id) *1—→ seasons(competition_id) [ON DELETE CASCADE]
Path examples:
- Org to all Seasons: organisations.organisation_id → competitions.organisation_id → seasons.competition_id
- Season to Organisation (reverse): seasons.competition_id → competitions.competition_id → organisations.organisation_id

⸻

Season → SeasonDay
- seasons(season_id) *1—→ season_days(season_id) [ON DELETE CASCADE]
- Uniques enforce one weekday/label per season: (season_id, season_day_name) and (season_id, week_day)

### SECTION 3.2: VENUES & COURTS
Organisation → Venue:
- organisations(organisation_id) *1—→ venues(organisation_id) (no cascade)

⸻

Venue → Court:
- venues(venue_id) *1—→ courts(venue_id) [ON DELETE CASCADE]
- Trigger keeps venues.total_courts in sync with child courts

### SECTION 3.3: ROUNDS, DATES & SETTINGS
Season → Rounds:
- seasons(season_id) *1—→ rounds(season_id) [ON DELETE CASCADE]

⸻

Rounds ↔ Dates (calendar mapping):
- rounds(round_id) *1—→ round_dates(round_id) [ON DELETE CASCADE]
- dates(date_id) *1—→ round_dates(date_id) [ON DELETE CASCADE]
- Path (round → all dates): rounds.round_id → round_dates.round_id → dates.date_id
- Path (date → rounds on that date): dates.date_id → round_dates.date_id → rounds.round_id

⸻

SeasonDay → RoundSettings:
- season_days(season_day_id) *1—→ round_settings(season_day_id) [ON DELETE CASCADE]

⸻

Round ↔ RoundSetting (governing config):
- rounds(round_id) *1—→ round_groups(round_id) [ON DELETE CASCADE]
- round_settings(round_setting_id) *1—→ round_groups(round_setting_id) [ON DELETE CASCADE]
- Path (round → its setting): rounds.round_id → round_groups.round_id → round_settings.round_setting_id
- Path (setting → all rounds using it): round_settings.round_setting_id → round_groups.round_setting_id → rounds.round_id

### SECTION 3.4: TIME WINDOWS & SCHEDULABLE CELLS
SeasonDay → TimeSlots:
- season_days(season_day_id) *1—→ time_slots(season_day_id) [ON DELETE CASCADE]
- default_times(time_id) *1—→ time_slots.start_time_id / end_time_id [ON DELETE CASCADE]

⸻

Schedulable Cells (CourtTimes):
- season_days(season_day_id) *1—→ court_times(season_day_id) [ON DELETE CASCADE]
- round_settings(round_setting_id) *1—→ court_times(round_setting_id) [ON DELETE CASCADE]
- courts(court_id) *1—→ court_times(court_id) [ON DELETE CASCADE]
- time_slots(time_slot_id) *1—→ court_times(time_slot_id) [ON DELETE CASCADE]
- Unique schedulable cell: (season_day_id, round_setting_id, court_id, time_slot_id)
Path (round → cells):
- rounds.round_id → round_groups.round_id → round_settings.round_setting_id → court_times.round_setting_id
- Add venue/court/time: court_times.court_id → courts.court_id → venues.venue_id and court_times.time_slot_id → time_slots

⸻

Court rankings (preference order):
- courts(court_id) *1—→ court_rankings(court_id) [ON DELETE CASCADE]
- season_days(season_day_id) *1—→ court_rankings(season_day_id) [ON DELETE CASCADE]
- round_settings(round_setting_id) *1—→ court_rankings(round_setting_id) [ON DELETE CASCADE]
Path (retrieve ranking list for a Round):
- rounds → round_groups → round_settings.round_setting_id
- Then round_settings.round_setting_id and its season_day_id (from round_settings) → court_rankings rows for that tuple

### SECTION 3.5: PARTICIPANT HIERARCHY (AGES, GRADES, TEAMS)
SeasonDay → Ages:
- season_days(season_day_id) *1—→ ages(season_day_id) [ON DELETE CASCADE]

⸻

Age → Grades:
- ages(age_id) *1—→ grades(age_id) [ON DELETE CASCADE]

⸻

Grade → Teams:
- grades(grade_id) *1—→ teams(grade_id) [ON DELETE CASCADE]

⸻

Path Examples:
- SeasonDay → all Teams: season_days.season_day_id → ages → grades → teams
- Team → Season/SeasonDay: reverse through grades.age_id → ages.season_day_id → season_days.season_id → seasons.competition_id → competitions.organisation_id

### SECTION 3.6: CONSTRAINTS (SCOPE & ELIGIBILITY)
Age allowed in RoundSetting:
- round_settings(round_setting_id) *1—→ age_round_constraints(round_setting_id) [ON DELETE CASCADE]
- ages(age_id) *1—→ age_round_constraints(age_id) [ON DELETE CASCADE]
Path (Round → eligible Ages):
- rounds → round_groups → round_settings.round_setting_id → age_round_constraints.round_setting_id → ages.age_id

⸻

Grade allowed in RoundSetting:
- round_settings(round_setting_id) *1—→ grade_round_constraints(round_setting_id) [ON DELETE CASCADE]
- grades(grade_id) *1—→ grade_round_constraints(grade_id) [ON DELETE CASCADE]
- (Table also stores age_id redundantly for convenience.)
Path (Round → eligible Grades):
- rounds → round_groups → round_settings.round_setting_id → grade_round_constraints.round_setting_id → grades.grade_id

⸻

Allocation flags at (RoundSetting, Age, Grade):
- round_settings(round_setting_id) *1—→ allocation_settings(round_setting_id) [ON DELETE CASCADE]
- ages(age_id) *1—→ allocation_settings(age_id) [ON DELETE CASCADE]
- grades(grade_id) *1—→ allocation_settings(grade_id) [ON DELETE CASCADE]
- Use: read restricted + restriction_type to drive algorithm behavior

⸻

Court-time restrictions:
- Age-level: round_settings → age_court_restrictions(round_setting_id) and ages → age_court_restrictions(age_id) and court_times → age_court_restrictions(court_time_id) (all CASCADE)
- Grade/dual-level: round_settings → grade_court_restrictions(round_setting_id) and grades → grade_court_restrictions(grade_id) and court_times → grade_court_restrictions(court_time_id) (all CASCADE)
Path (Round → forbidden CourtTimes for a Grade):
- rounds → round_groups → round_settings.round_setting_id → grade_court_restrictions.round_setting_id
- Filter by grade_id; collected court_time_id map to concrete cells

### SECTION 3.7: ORCHESTRATION & AUDIT
Run Master:
- seasons(season_id) *1—→ scheduling_runs(season_id) [ON DELETE CASCADE]
- season_days(season_day_id) *1—→ scheduling_runs(season_day_id) [ON DELETE CASCADE]

⸻

Run Events:
- scheduling_runs(run_id) *1—→ scheduling_run_events(run_id) [ON DELETE CASCADE]

⸻

Run Locks (exclusive per SeasonDay):
- season_days(season_day_id) 1—1→ scheduling_locks(season_day_id) [ON DELETE CASCADE]
- scheduling_runs(run_id) *1—→ scheduling_locks(run_id) [ON DELETE CASCADE]

⸻

Run Exports:
- scheduling_runs(run_id) *1—→ run_exports(run_id) [ON DELETE CASCADE]

⸻

Run Constraint Snapshots:
- scheduling_runs(run_id) *1—→ run_constraints_snapshot(run_id) [ON DELETE CASCADE]

### SECTION 3.8: STAGING (P2 / P3)
P2 allocations (age/grade → court_time):
- scheduling_runs(run_id) *1—→ p2_allocations(run_id) [ON DELETE CASCADE]
- rounds(round_id) *1—→ p2_allocations(round_id) [ON DELETE CASCADE]
- ages(age_id) *1—→ p2_allocations(age_id) [ON DELETE CASCADE]
- grades(grade_id) *1—→ p2_allocations(grade_id) [ON DELETE CASCADE]
- court_times(court_time_id) *1—→ p2_allocations(court_time_id) [ON DELETE CASCADE]
- Uniq: (run_id, round_id, court_time_id) ensures one allocation per slot per round within a run

⸻

P3 game allocations (team pairings):
- Parents like P2 plus Teams: teams(team_id) *1—→ p3_game_allocations.team_a_id / team_b_id [ON DELETE CASCADE]
- Optional link back to P2: p2_allocations(p2_allocation_id) *1—→ p3_game_allocations(p2_allocation_id)
- Uniq: (run_id, round_id, court_time_id) one game per slot per round within a run

⸻

P3 byes:
- scheduling_runs(run_id) *1—→ p3_bye_allocations(run_id) [ON DELETE CASCADE]
- rounds(round_id) *1—→ p3_bye_allocations(round_id) [ON DELETE CASCADE]
- ages(age_id) *1—→ p3_bye_allocations(age_id) [ON DELETE CASCADE]
- grades(grade_id) *1—→ p3_bye_allocations(grade_id) [ON DELETE CASCADE]
- teams(team_id) *1—→ p3_bye_allocations(team_id) [ON DELETE CASCADE]
- Uniq: (run_id, round_id, team_id) one bye per team per round in a run

⸻

Staging diffs (audit):
- scheduling_runs(run_id) *1—→ staging_diffs(run_id) [ON DELETE CASCADE]

### SECTION 3.9: SAVED / FINALISED OUTPUTS
Saved games (checkpointed):
- scheduling_runs(run_id) *1—→ saved_games(run_id) [ON DELETE CASCADE]
- rounds(round_id) *1—→ saved_games(round_id) [ON DELETE CASCADE]
- ages(age_id) *1—→ saved_games(age_id) [ON DELETE CASCADE]
- grades(grade_id) *1—→ saved_games(grade_id) [ON DELETE CASCADE]
- teams(team_id) *1—→ saved_games.team_a_id / team_b_id [ON DELETE CASCADE]
- court_times(court_time_id) *1—→ saved_games(court_time_id) [ON DELETE CASCADE]
- Uniq: (run_id, round_id, court_time_id)

⸻

Saved byes (checkpointed):
- Similar to p3_bye_allocations; Uniq (run_id, round_id, team_id)

⸻

Final game schedule (publish-ready snapshot):
- References the same master entities (run_id, round_id, age_id, grade_id, team_a_id, team_b_id, court_time_id) — all [ON DELETE CASCADE]
- Denormalized names/time fields stored in-table for export stability
- Uniq: (round_id, court_time_id)

⸻

Final bye schedule (publish-ready snapshot):
- References (run_id, round_id, age_id, grade_id, team_id) — all [ON DELETE CASCADE]
- Denormalized identity fields stored in-table
- Uniq: (round_id, team_id)

### SECTION 3.10: SUPPORTING LOOKUPS
Dates ↔ Public Holidays:
- dates(date_id) *1—→ public_holidays(date_id)
- dates.is_public_holiday is also toggled during seed insert

⸻

Default Times ↔ Time Slots:
- default_times(time_id) *1—→ time_slots.start_time_id / end_time_id [ON DELETE CASCADE]

### SECTION 3.11: PERMISSIONS
User ↔ Organisation (capabilities):
- users(user_account_id) *1—→ user_permissions(user_account_id) [ON DELETE CASCADE]
- organisations(organisation_id) *1—→ user_permissions(organisation_id) [ON DELETE CASCADE]
- Uniq: (user_account_id, organisation_id) — single permission row per user–org pair

### SECTION 3.12: END-TO-END "HOW DO I GET X FROM Y" RECIPES
From a Round to all schedulable CourtTimes (with venue/court/time):
- rounds.round_id → round_groups.round_id → round_settings.round_setting_id → court_times.round_setting_id
Enrich:
- court_times.court_id → courts → venues
- court_times.time_slot_id → time_slots (→ start/end_time, label)

⸻

From a Round to eligible Ages and Grades:
- Ages: rounds → round_groups → round_settings.round_setting_id → age_round_constraints.round_setting_id → ages.age_id
- Grades: rounds → round_groups → round_settings.round_setting_id → grade_round_constraints.round_setting_id → grades.grade_id
- (Optionally join back ages via grades.age_id to cross-check)

⸻

From a RoundSetting to forbidden CourtTimes for an Age/Grade:
- Age-level: round_settings.round_setting_id → age_court_restrictions.round_setting_id (filter age_id) → court_times
- Grade-level: round_settings.round_setting_id → grade_court_restrictions.round_setting_id (filter grade_id) → court_times

⸻

From a Run to its produced (checkpointed) games and byes:
- Games: scheduling_runs.run_id → saved_games.run_id → join rounds/ages/grades/teams/court_times
- Byes: scheduling_runs.run_id → saved_byes.run_id → join rounds/ages/grades/teams

⸻

From a Run to final published fixtures:
- scheduling_runs.run_id → final_game_schedule.run_id (denormalized names ready for export)
- For byes: scheduling_runs.run_id → final_bye_schedule.run_id

⸻

From a Team to its Round allocations (within a Run):
- teams.team_id → p3_game_allocations.team_a_id OR team_b_id (filter by run_id, round_id)
- Include cell and venue/time: p3_game_allocations.court_time_id → court_times → courts/venues/time_slots
- Or via checkpoint/final tables similarly

### SECTION 3.13: CARDINALITY & DELETE BEHAVIOR CHEAT-SHEET
CASCADE from parents:
- competitions → seasons
- seasons → season_days, rounds
- rounds → round_dates, round_groups
- round_settings (child of season_days) → cascades to: round_groups, court_times, constraints (age_*, grade_*, allocation_settings), court_rankings
- courts → court_times, court_rankings
- season_days → time_slots, ages, court_times, round_settings
- Run family: scheduling_runs → scheduling_run_events, scheduling_locks, run_exports, run_constraints_snapshot, p2_allocations, p3_*, staging_diffs, saved_*, final_*
- Participant chain: ages → grades → teams (each with CASCADE to children)

⸻

No explicit CASCADE (defaults to NO ACTION):
- organisations → competitions does cascade via competitions→seasons, but organisations → venues does not cascade (venues remain unless explicitly handled)
- organisations → user_permissions does cascade (declared on user_permissions)


## SECTION 4: Triggers & Functions
### SECTION 4.1: TIME SLOT LABEL AUTO-GENERATION
FUNCTION: fn_time_slots_label_default()
TRIGGER: trg_time_slots_label_default (BEFORE INSERT OR UPDATE ON time_slots)
PURPOSE: Ensures that if time_slot_label is NULL or blank, it is auto-generated from start_time in format HH:MI AM.
NOTES: Raises an exception if start_time is NULL during auto-generation.

### SECTION 4.2: VENUE COURT COUNT SYNC
FUNCTIONS:
- fn_venues_refresh_total_courts(p_venue_id integer) → Updates venues.total_courts to reflect count of rows in courts for given venue_id.
- fn_courts_sync_total_courts() → Wrapper for triggers; calls refresh appropriately for INSERT, UPDATE, or DELETE on courts.
TRIGGERS:
- trg_courts_ai_sync_total_courts (AFTER INSERT ON courts)
- trg_courts_au_sync_total_courts (AFTER UPDATE ON courts)
- trg_courts_ad_sync_total_courts (AFTER DELETE ON courts)
PURPOSE: Automatically maintains accurate venues.total_courts without requiring manual updates.
NOTES: On update, handles venue reassignments (refreshing both old and new venue totals).

### SECTION 4.3: COURT RANKINGS AUTO-OVERRIDE
FUNCTION: fn_court_rankings_auto_override()
TRIGGER: trg_court_rankings_auto_override (BEFORE INSERT ON court_rankings)
PURPOSE: Automatically marks older rows for the same (court_id, season_day_id, round_setting_id) as overridden = TRUE when a new record is inserted.
NOTES: Ensures that only the latest ranking for a court under a setting is active. Updates updated_at and updated_by_user_id.


## SECTION 5: Seed / Bootstrap SQL
### SECTION 5.1: DATES TABLE PREPOPULATION
LOGIC: Inserts one row per day from (current_date - 10 years) to (current_date + 100 years).
COLUMNS POPULATED:
- date_value (actual date)
- date_day (weekday name in uppercase)
- calendar_year (numeric year)
- iso_week_int (ISO week number)
- is_weekend (TRUE if Saturday/Sunday)
- is_public_holiday (FALSE initially)
CONFLICT HANDLING: ON CONFLICT (date_value) DO NOTHING — ensures idempotence.
PURPOSE: Provides a ready-to-use calendar dimension for all scheduling.

### SECTION 5.2: PUBLIC HOLIDAYS PREPOPULATION
LOGIC: Inserts Commonwealth + state/territory holidays for 2025.
REGIONS: CTH, ACT, NSW, NT, QLD, SA, TAS, VIC, WA.
EXAMPLES OF SEEDED HOLIDAYS:
- National: New Year’s Day, Australia Day (observed), Good Friday, Easter, Anzac Day, Christmas Day, Boxing Day.
- ACT: Canberra Day, Reconciliation Day, Labour Day.
- VIC: Melbourne Cup Day, Labour Day, King’s Birthday.
- WA: Western Australia Day, Labour Day.
MECHANISM:
- Updates dates.is_public_holiday = TRUE for matching date_value.
- Inserts into public_holidays with holiday_name + holiday_region if not already present.
PURPOSE: Ensures baseline awareness of Australian public holidays at system startup.

### SECTION 5.3: DEFAULT TIMES PREPOPULATION
LOGIC: Inserts every second of the day (0–86,399) into default_times as a TIME value.
CONFLICT HANDLING: ON CONFLICT (time_value) DO NOTHING — prevents duplicates.
PURPOSE: Provides a canonical lookup of all possible times-of-day for referencing in time_slots.
NOTES: This table is critical for normalizing time_slots.start_time_id and end_time_id.


## SECTION 6: Enumerations Dictionary
_All enums arise from CHECK constraints or constrained text fields. Use these exact literals (case-sensitive)._

### SECTION 6.1: CALENDAR & GEOGRAPHY
- dates.date_day: MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
- public_holidays.holiday_region: CTH, TAS, VIC, NSW, ACT, QLD, SA, NT, WA

### SECTION 6.2: VISIBILITY & ROUNDS
- seasons.visibility: PRIVATE, INTERNAL, PUBLIC
- PRIVATE: visible to season owners/admins only
- INTERNAL: internal stakeholders; not public
- PUBLIC: intended for public consumption
- rounds.round_type: GRADING, REGULAR, FINALS
- rounds.round_status: PLANNED, SCHEDULED, PUBLISHED, COMPLETED, CANCELLED

### SECTION 6.3: SEASON DAY & WEEKDAY
- season_days.season_day_name: MONDAY … SUNDAY
- season_days.week_day: integers 1..7 (weekday mapping per schema; 1=Monday if ISO)

### SECTION 6.4: SCHEDULING CELLS & AVAILABILITY
- court_times.availability_status: AVAILABLE, BLOCKED, MAINTENANCE, EVENT
- court_times.lock_state: OPEN, LOCKED

### SECTION 6.5: CONSTRAINTS & RESTRICTIONS
- allocation_settings.restriction_type: NONE, AGE, GRADE, DUAL
- grade_court_restrictions.restriction_type: GRADE, DUAL

### SECTION 6.6: ORCHESTRATION (RUNS)
- scheduling_runs.run_status: PENDING, RUNNING, FAILED, SUCCEEDED, ABANDONED
- scheduling_runs.process_type: INITIAL, MID
- scheduling_runs.run_type: I_RUN_1, I_RUN_2, M_RUN_1, M_RUN_2, M_RUN_3
- scheduling_runs.s1_check_results: NEW_INITIAL, NEW_MID, RESTART_INITIAL, RESTART_MID, SAVE_INITIAL, SAVE_MID
- scheduling_runs.resume_checkpoint: BEFORE_P2, AFTER_P2_BEFORE_P3, AFTER_P3_BEFORE_FINALISE, FINALISED

### SECTION 6.7: RUN EVENTS & EXPORTS
- scheduling_run_events.stage: STEP1, STEP2, STEP3, STEP4, STEP5, FINALISE
- scheduling_run_events.severity: INFO, WARN, ERROR
- run_exports.export_type: CSV, PDF, ZIP, XLSX

### SECTION 6.8: SNAPSHOTS & OUTPUT STATUS
- run_constraints_snapshot.phase: P2, P3, COMPOSITE
- saved_games.game_status: AFTER_P2_BEFORE_P3, AFTER_P3_BEFORE_FINALISE, FINALISED
- saved_byes.game_status: AFTER_P2_BEFORE_P3, AFTER_P3_BEFORE_FINALISE, FINALISED
- saved_byes.bye_reason: ODD_TEAMS, ERROR_LOOP, CONSTRAINT, MANUAL_OVERRIDE
- final_game_schedule.game_status: FINALISED, CANCELLED, FORFEITED, COMPLETED
- final_bye_schedule.bye_reason: ODD_TEAMS, ERROR_LOOP, CONSTRAINT, MANUAL_OVERRIDE