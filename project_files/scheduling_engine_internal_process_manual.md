# Scheduling Engine - Internal Process Manual

## Scheduling Overview

The Scheduling Engine is designed to automate the creation of fair and efficient sports competition schedules. Its primary goals are to balance fairness, maximize court utilization, and provide transparency throughout the scheduling process. The system supports customization at multiple levels—age groups, grades, and individual games—allowing administrators to tailor schedules to their competition's unique requirements. By automating complex scheduling tasks, the engine reduces manual workload and helps ensure equitable distribution of games, BYEs, and court assignments.

## Step-by-Step Process Flow

The scheduling process consists of 14 sequential steps, divided between user interface (UI) pages and algorithm execution phases:

1. **Season Dashboard (UI)**: Overview and management of the current season.
2. **Setup Age Allocations (UI)**: Define court time and resource allocations per age group.
3. **Age Scheduling (Algorithm)**: Generate initial schedules for each age group based on allocations.
4. **Confirm Age Schedule (UI)**: Review and confirm the age group schedules.
5. **Setup Grade Allocations (UI)**: Specify court time and parameters for each grade within age groups.
6. **Grade Scheduling (Algorithm)**: Create detailed schedules for each grade.
7. **Confirm Grade Schedule (UI)**: Review and confirm grade-level schedules.
8. **Setup Game Allocations (UI)**: Configure individual game parameters and constraints.
9. **Game Scheduling (Algorithm)**: Finalize game-level scheduling with all constraints applied.
10. **Confirm Game Schedule (UI)**: Review and approve the final game schedule.
11. **Finalize & Export (UI)**: Lock schedules and export data for use in competition management.

Each UI step allows administrators to input or adjust parameters, while the algorithm steps perform automated scheduling computations based on those inputs.

## Algorithm Phases

### Age Scheduling

This phase establishes the foundational schedule by allocating court times and assigning matches across age groups. It applies fairness rules such as round-robin matchups and equitable BYE rotations to ensure balanced play opportunities. The algorithm respects court rankings to optimize the use of higher-quality courts.

### Grade Scheduling

Building on age scheduling, this phase refines schedules within each grade, considering grade-specific constraints and preferences. It maintains fairness by continuing round-robin cycles and BYE rotations, and adjusts court assignments based on grade-level priorities and availability.

### Game Scheduling

The final algorithm phase schedules individual games, incorporating all constraints from previous phases plus game-specific rules such as timing and court preferences. It resolves conflicts and optimizes the schedule for minimal overlaps and maximum fairness.

Throughout all phases, error handling mechanisms detect logic errors (e.g., invalid inputs) and constraint violations (e.g., unavailable courts). The system attempts automatic corrections where possible and flags issues for manual review.

## Input / Output Mapping

User inputs from the dashboard—such as court allocations, age and grade parameters, and game constraints—are initially stored in temporary tables to allow iterative adjustments. Key input tables include `season_court_time_allocations` for court resources and allocation settings.

Once schedules are confirmed at each phase, outputs are written to permanent tables like `scheduled_games` and `scheduled_byes`. These tables capture finalized matchups, BYE assignments, court allocations, and timing details.

This two-stage storage approach enables flexibility during scheduling and ensures data integrity upon confirmation.

## Error Handling

Errors are categorized as:

- **Logic Errors**: Critical issues that must be corrected before proceeding (e.g., missing required inputs, invalid data formats).
- **Constraint Errors**: Violations of scheduling rules that can be overridden or ignored if necessary (e.g., court conflicts, scheduling overlaps).

When errors occur, the system provides automated suggestions for fixes. Administrators can manually adjust inputs or choose to ignore certain constraint errors to proceed. Manual overrides are supported to accommodate exceptional cases.

A future audit log feature is planned to track all manual changes and overrides, enhancing accountability and transparency.
