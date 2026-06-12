# Plans

This directory stores historical plans. It is not the source of current project state; use `docs/WAYPOINT.md` for current direction.

## Naming

Use sequential filenames:

```text
1_short_name.md
2_next_short_name.md
```

## Plan Template

```markdown
# Plan Title

## Summary

Briefly state the goal and intended outcome.

## Public Contracts

List API, CLI, config, schema, file format, or migration changes. Write `None` if there are no public contract changes.

## Implementation

- Describe the smallest standalone units of work.
- Keep behavior-level detail high enough that implementation decisions are clear.
- Avoid unrelated refactors.

## Verification

- List focused tests, checks, builds, or smoke tests.
- Include manual verification when relevant.

## Assumptions

- Record important defaults or decisions made during planning.
```
