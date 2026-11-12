---
description: "Select the personas that fit this project and install them as custom agents"
---

# Select Personas

Choose the review personas that match this project's domains and install them
as custom agents. Personas are AI review perspectives, not a substitute for
human domain experts.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). It may
name personas explicitly (e.g. `grafana-engineer pricing-analyst`), ask to
`update` installed personas, or describe the project.

## Steps

1. **List the catalog and what is installed.**

   ```bash
   bash .specify/extensions/personas/scripts/bash/personas.sh list
   bash .specify/extensions/personas/scripts/bash/personas.sh installed
   ```

   If the user asked to `update`, run
   `bash .specify/extensions/personas/scripts/bash/personas.sh update`, report
   the result and stop.

2. **Understand the project.** Read `.specify/memory/constitution.md`,
   `README.md`, `AGENTS.md` (if present) and skim the repository layout and
   dependency manifests. Identify the surfaces that change in this project
   (e.g. Python service, web UI, Home Assistant integration, dashboards,
   telemetry collector, Azure/Terraform, containers, networking, satellite
   data).

3. **Propose a selection.** Map each surface to exactly one owning persona.
   Include `review-orchestrator` when two or more personas are selected, and
   `quality-documentation` for any project with user-facing behavior. Include
   `pricing-analyst` when the project ingests into quota-limited or billable
   services. Do not select personas for surfaces the project does not have.
   Present the proposal as a table (persona — owned surface — reason) plus the
   personas you deliberately left out and why. If the user named personas
   explicitly, use those and only flag obvious gaps.

4. **Install** after the user confirms (or directly if the user named them):

   ```bash
   bash .specify/extensions/personas/scripts/bash/personas.sh install <name> [<name> ...]
   ```

   Existing files are skipped; use `--force` only with the user's consent,
   because it overwrites local edits.

5. **Configure routing.** Create `.specify/extensions/personas/personas-config.yml`
   from `personas-config.template.yml` if missing and fill `routing:` with the
   project paths, data sources or topics each selected persona owns.

6. **Record project facts where personas expect them.** The personas are
   project-agnostic and read project-specific facts (hosts, sites, accounts,
   data source UIDs, limits, commands, exclusions) from `AGENTS.md`, the
   constitution and the history/decision log. If those facts are missing,
   list the gaps and offer to add a "Personas" section to `AGENTS.md`. Never
   write secrets.

7. **Constitution hint.** If the constitution does not mention persona
   reviews yet, suggest (do not apply silently) a short workflow rule: plans
   name affected surfaces and selected personas — including why others are not
   needed — and persona review gates run after plan, tasks and implement.

## Output

The installed personas with their target files, the routing configuration and
any open gaps in project facts.
