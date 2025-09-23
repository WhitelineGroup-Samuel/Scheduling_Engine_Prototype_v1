# Codex Workflow

This document describes the workflow, rules, and best practices for Codex (the AI code assistant) when interacting with this repository. It is intended to ensure consistency, completeness, and maintainability in all code and documentation contributions.

---

## Purpose

The purpose of this workflow is to define clear guidelines for Codex’s operation in this repository, ensuring:
- All code contributions are complete, maintainable, and well-documented.
- The repository remains in a production-ready state after every Codex action.
- All changes are reviewed for alignment with project requirements, standards, and best practices.

---

## Codex Rules of Engagement

Codex must adhere to the following rules when working in this repository:

1. **Strictly Code Assistant**: Codex acts only as a code assistant, making no architectural or business decisions unless explicitly instructed.
2. **Completeness**: All contributions must be complete—no partial implementations or missing tests unless specifically requested.
3. **Repository Familiarity**: Always read the README and scan the full repository before making any changes or suggestions.
4. **Proactive Refactoring**: Codex may proactively refactor code for clarity, maintainability, or to bring it in line with current standards, but should explain the rationale for significant refactors.
5. **Automatic TODOs & Placeholders**: Where implementation details are unclear or require human input, Codex should insert clear TODOs or placeholders, both inline and as docstring stubs, following the policy below.
6. **Documentation Awareness**: Cross-reference related documentation (see Integration section) when introducing new terms or processes.

---

## Repo Review Process

Before any code generation or modification, Codex must:

1. **File-by-File Review**: Examine all files relevant to the task, including README, configuration, and code files.
2. **Manuals & ERD Comparison**: Compare the current implementation with any available manuals, specifications, and the Entity-Relationship Diagram (ERD) to ensure alignment.
3. **Flag Gaps**: Identify and flag any functional or stylistic gaps, inconsistencies, or technical debt.
4. **Highlight Dependencies**: Note any dependencies or interactions that may be affected by the proposed changes.

---

## Code Generation Process

When generating or modifying code, Codex must:

1. **Output Full File Content**: Unless a patch diff is explicitly requested, provide the complete, updated file content.
2. **Test Generation**: Always generate or update corresponding tests for any new or modified code.
3. **Migrations**: When schema changes are made, generate database migration scripts and update related documentation.
4. **Docstring Updates**: Update or add docstrings to reflect the current functionality, using clear and concise language.
5. **Simple-Language Explanations**: Provide a brief, simple-language explanation of complex changes or new modules.
6. **Consistency**: Ensure code style and structure are consistent with [coding_standards.md](coding_standards.md).

---

## TODOs & Placeholders Policy

When Codex cannot fully implement a section due to missing information or human input requirements:

1. **Inline TODOs**: Insert `# TODO(Codex): ...` comments directly in the code at the relevant location.
2. **Docstring Placeholders**: Add a docstring stub at the function/class/module level indicating the missing implementation.
3. **Rationale**: Only include a rationale if the reason for the placeholder is not obvious.
4. **Consistent Prefix**: Always use the prefix `TODO(Codex):` for easy searching and tracking.
5. **Documentation**: Summarize outstanding TODOs in a dedicated section at the end of the file, if appropriate.

---

## Test & Documentation Requirements

Codex must enforce and update the following:

1. **README Updates**: Always update the README to reflect new features, changes, or setup instructions.
2. **ADRs for Design Changes**: Propose an Architecture Decision Record (ADR) for any significant design or architectural changes.
3. **Testing Standards**: Ensure all code changes are accompanied by tests that meet the criteria in [testing_standards.md](testing_standards.md).
4. **Docstring Updates**: Suggest or add docstring updates for all new or modified functions, classes, and modules.
5. **Documentation Cross-References**: Reference or update [documentation_standards.md](documentation_standards.md) as needed.

---

## Integration with Other Docs

When introducing new terms, patterns, or procedures, Codex must cross-reference:
- [coding_standards.md](coding_standards.md) for code style and patterns.
- [testing_standards.md](testing_standards.md) for test requirements.
- [documentation_standards.md](documentation_standards.md) for docstring and documentation structure.
- [glossary.md](glossary.md) when new or domain-specific terms are introduced.

---

## Example Workflow

**Step 1:** Codex receives a feature request or bug report.

**Step 2:** Codex reads the README and scans the repository for related files.

**Step 3:** Codex reviews relevant files, compares them to manuals/specs/ERD, and flags any gaps.

**Step 4:** Codex generates or modifies code, outputting the full file content (unless a patch is requested).

**Step 5:** Codex creates or updates tests, migrations, and docstrings as needed.

**Step 6:** Codex inserts TODOs/placeholders for ambiguous or human-required parts, using the prescribed format.

**Step 7:** Codex updates the README and references other documentation as required.

**Step 8:** Codex provides a simple-language summary of the changes.

---

## Good vs Bad Codex Behavior

### Good Example
> Codex scans the repo, updates a model, generates a migration, creates tests, updates the README, and adds a `TODO(Codex):` for a business rule that needs clarification.

### Bad Example
> Codex adds a new feature but omits tests, leaves undocumented changes, or adds ambiguous `# TODO` comments without the `Codex` prefix or explanation.

---
