# Glossary

## Purpose
_This glossary standardizes terminology used throughout the Scheduling Engine project. It serves as a common reference for developers and AI tools like ChatGPT to ensure clear, unambiguous communication and understanding. By defining key concepts consistently, it helps avoid confusion and supports accurate reasoning and implementation._

## Domain Terms
- **Organisation:** The top-level entity representing a tenant or client that manages competitions and venues.
- **Competition:** A structured program or event under an organisation, typically consisting of multiple seasons.
- **Season:** A defined time period within a competition during which games are played, with specific scheduling and rules.
- **Season Day:** A specific day of the week within a season that has its own scheduling configurations and time windows.
- **Round:** A logical grouping of games within a season, such as grading rounds, regular rounds, or finals.
- **Age Group:** A category representing the age range of participants, used to organize teams and competitions.
- **Grade:** A subdivision within an age group that further categorizes teams, often by skill or experience level.
- **Team:** A group of players competing together within a grade and age group.
- **Venue:** A physical location where games are played, consisting of one or more courts.
- **Court:** An individual playing area within a venue where games take place.
- **Bye:** A scheduled rest or non-playing round assigned to a team, often due to an odd number of teams or scheduling constraints.
- **Allocation:** The process of assigning teams or games to specific courts and time slots.
- **Constraint:** A rule or restriction that must be respected during scheduling, such as court availability or age group limitations.
- **Schedule:** The finalized plan detailing when and where games will be played.
- **Export:** A generated output file or report that presents scheduling information in a publishable format.

## Database Terms
- **Organisation:** Tenant boundary; parent of competitions and venues.
- **Competition:** Program under an organisation; parent of seasons.
- **Season:** Time-bounded competition; parent of season_days and rounds.
- **Season Day:** Per-season weekday configuration window (name/label/weekday, start–end time window); parent of round_settings, time_slots, ages, and part of court_times.
- **Round:** Logical round (GRADING/REGULAR/FINALS) within a season; mapped to calendar dates via round_dates; linked to a configuration via round_groups.
- **Round Setting:** Configuration bundle (per season_day) governing allocation (holds rules JSON; numbered by round_settings_number).
- **Round Group:** Join table binding a round to a round_setting (which implies the season_day).
- **Default Times:** Canonical list of times-of-day; referenced by time_slots.start_time_id/end_time_id.
- **Time Slot:** A definitional time window on a season_day (start/end; buffer/duration; auto label).
- **Court:** A playing area at a venue; ordered by display_order.
- **Court Ranking:** Preference rank for courts per (season_day, round_setting). New inserts auto-mark older rows overridden=TRUE.
- **Court Time:** The schedulable cell: (season_day, round_setting, court, time_slot) plus availability_status and lock_state.
- **Age:** Age group under a season_day with age_rank and optional age_required_games.
- **Grade:** Grade under an age with grade_rank, optional grade_required_games, and bye_requirement.
- **Team:** Team under a grade.
- **Age Round Constraint:** Whitelists ages allowed in a round_setting.
- **Grade Round Constraint:** Whitelists grades allowed in a round_setting (stores age_id for convenience).
- **Allocation Settings:** Restriction flags at (round_setting, age, grade) with restriction_type (NONE|AGE|GRADE|DUAL).
- **Age/Grade Court Restrictions:** Disallow (or scope) specific court_times for an age/grade in a round_setting.
- **Scheduling Run:** Orchestrated scheduling attempt state; holds lifecycle flags, round_ids (JSON), metrics/errors, and checkpoints.
- **Run Event:** Time-stamped log row for a run (stage/severity/message, optional context JSON).
- **Run Lock:** Ensures exclusive orchestration per season_day (season_day_id is UNIQUE).
- **Run Export:** Artefact record for a run (export_type, file_path).
- **Run Constraints Snapshot:** JSON snapshot of constraints (phase: P2, P3, COMPOSITE) for reproducibility.
- **P2 Allocation:** Phase 2 assignment of (age, grade) to a specific court_time within a run/round.
- **P3 Game Allocation:** Phase 3 pairing of two teams into a court_time (optionally tied back to a P2 row).
- **P3 Bye Allocation:** Team assigned a bye in a run/round with bye_reason.
- **Saved Games/Byes:** Checkpointed results (After P2 / After P3 / Finalised).
- **Final Game/Bye Schedule:** Denormalized, publish-ready snapshots (include names and times as copied at publish).
- **Availability Status:** State of a court_time: AVAILABLE, BLOCKED, MAINTENANCE, EVENT.
- **Lock State:** OPEN or LOCKED status on court_time to control edits/allocations.
- **Idempotency Key:** Unique token on scheduling_runs to prevent duplicate processing of the same command.
- **Seed Master:** String on scheduling_runs indicating seed source/version for reproducibility.
- **Config Hash:** Hash of configuration inputs captured on scheduling_runs for auditability.
- **Resume Checkpoint:** Where to resume a run: BEFORE_P2, AFTER_P2_BEFORE_P3, AFTER_P3_BEFORE_FINALISE, or FINALISED.
- **Display Order:** Integer used to order venues/courts visually or preferentially.
- **Overridden (Court Rankings):** Flag set TRUE on older ranking rows when a new one for the same (court_id, season_day_id, round_setting_id) is inserted.

## Algorithm Terms
- **Phase 1 (P1):** Initial data preparation and validation stage before allocations begin.
- **Phase 2 (P2):** Allocation of age and grade groups to specific court times, establishing foundational scheduling blocks.
- **Phase 3 (P3):** Pairing of teams into games within allocated court times, including assigning byes where necessary.
- **Phase 4 (P4):** Finalization and optimization phase that refines the schedule for fairness and efficiency.
- **Orchestrator:** The component responsible for managing the overall scheduling process, coordinating phases and handling workflow.
- **Allocator:** The subsystem that assigns teams, grades, and ages to court times based on constraints and preferences.
- **Optimizer:** The process or tool that improves the schedule by balancing fairness, minimizing conflicts, and maximizing resource utilization.
- **Constraint Solver:** The algorithmic engine that enforces all scheduling rules and restrictions during allocation.
- **Run:** A single execution instance of the scheduling process, producing a schedule output.
- **Checkpoint:** Saved intermediate state within a run that allows pausing and resuming scheduling without loss of progress.
- **Golden Test:** A comprehensive validation test comparing current scheduling outputs against a trusted baseline to ensure correctness.
- **Determinism:** The property that a scheduling run produces the same result given the same inputs and seed data.
- **Fairness:** The principle that scheduling decisions distribute opportunities and constraints evenly among teams and participants.
- **Audit Log:** A detailed record of all actions, decisions, and events occurring during a scheduling run for traceability.
- **Seed Data:** Fixed input values or configurations used to ensure reproducible scheduling outcomes.
- **Reproducibility:** The ability to rerun scheduling processes and obtain identical results, important for auditing and debugging.
