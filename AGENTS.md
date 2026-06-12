# Repository Guidelines

## Project Compass

Read these files before substantial planning or implementation work:

- `docs/NORTH_STAR.md`: static long-term vision and product/system destination.
- `docs/WAYPOINT.md`: living current state, decisions, constraints, and next direction.
- `docs/architecture.md`: codebase map, subsystem responsibilities, data flow, and extension points.
- `README.md`: setup, commands, local development, and operational usage.
- `docs/TODO.md`: deferred work that is not part of the active plan.

## Planning

- Split large plans into the smallest useful standalone working units.
- Keep historical plans in `docs/plans/`.
- Name plans sequentially, for example `docs/plans/1_short_name.md`.
- Plans should identify goal, public contract changes, implementation approach, verification, assumptions, and out-of-scope work.
- Do not treat historical plans as current truth; use `docs/WAYPOINT.md` for current direction.

## Documentation Maintenance

Keep direction, current reality, and deferred work separate:

- `docs/NORTH_STAR.md` is static and vision-oriented. Update it rarely, only when the long-term product or system destination materially changes.
- `docs/WAYPOINT.md` is dynamic. Update it after meaningful planning, implementation, or decision changes that alter current state, constraints, direction, or open questions.
- `docs/TODO.md` is dynamic. Use it for tasks, ideas, and future work that are not part of the active plan.
- `docs/architecture.md` should reflect the current system shape after changes to subsystem boundaries, data flow, storage, public interfaces, or extension points.
- `docs/DSL.md`. An up to date definition of the DSL and all it's features including the standard libarary. Update this file whenever the DSL language changes.

Prefer current, distilled documentation over changelog-style history. Remove resolved questions from `WAYPOINT.md`; record lasting decisions there when they still affect direction.

## Coding

- This is a Python 3.12+ project unless a project-specific file says otherwise.
- No backward compatibility is required unless explicitly stated.
- Prefer existing project patterns, helpers, and abstractions over new frameworks or broad rewrites.
- Keep changes scoped to the requested behavior and nearby ownership boundaries.
- Avoid unrelated refactors, formatting churn, and generated-file updates unless required.
- Preserve user changes in the working tree. Do not revert or overwrite unrelated work.
- Use structured parsers and APIs for structured data instead of ad hoc string manipulation when practical.

## Code Documentation

- Every Python source file should have a top-of-file reStructuredText module docstring.
- Substantial modules should document purpose, responsibilities, public API, inputs/outputs, side effects, boundaries, and extension notes.
- Small modules may use a compact purpose/public API docstring.
- Keep docstrings current with code ownership. Avoid changelog notes, TODO lists, or line-level narration.

## Verification

- Before finishing implementation work, run the smallest relevant test, type check, lint check, build, or smoke test.
- If verification cannot be run, report the reason and the residual risk.
- Add or update tests when behavior changes, public contracts change, defects are fixed, or the blast radius is larger than a local refactor.
- Prefer focused tests that lock the requested behavior over broad snapshot or integration churn.

## Clean Handoff

- Summarize what changed, where it changed, and what verification ran.
- Call out public API, CLI, config, schema, data migration, or file format changes.
- Mention any deferred follow-up by adding it to `docs/TODO.md` when appropriate.
