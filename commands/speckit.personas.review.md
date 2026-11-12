---
description: "Persona review gate for a Spec Kit artifact (spec, plan, tasks or implementation)"
---

# Persona Review Gate

You act as the **review-orchestrator** in review-gate mode. You do not review
yourself and you do not edit the artifact — you moderate the installed
personas, collect their verdicts and record the result.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). It may
name the phase (`specify`, `plan`, `tasks`, `implement`) or restrict the
reviewers.

## 1. Context

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   (PowerShell: `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly`)
   and read `FEATURE_DIR`.
2. Determine the phase from the calling hook or the arguments; otherwise use
   the most recent artifact:

   | Phase | Input |
   | --- | --- |
   | specify | `spec.md` |
   | plan | `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `spec.md` |
   | tasks | `tasks.md`, `plan.md` (constitution check) |
   | implement | `tasks.md`, diff against the actual PR base, CI and local check results |

3. Always include `.specify/memory/constitution.md`, `AGENTS.md` and the
   project history/decision log if they exist.
4. Never pass credentials, full environment files or sensitive live output to
   reviewers.

## 2. Select reviewers

1. List installed personas:
   `bash .specify/extensions/personas/scripts/bash/personas.sh installed`.
   If none are installed, report `Persona review <phase>: skipped (no personas
   installed — run /speckit-personas-select)` and stop.
2. Read `.specify/extensions/personas/personas-config.yml` (`routing`) and each
   installed persona file.
3. Pick only the personas whose surface the artifact touches. Every question
   belongs to exactly one owner. Apply the risk tiers from the
   `review-orchestrator` persona: T0 needs no reviewer; T1 uses one persona's
   checklist inline; T2/T3 use every directly relevant owner, and
   `quality-documentation` (if installed) is mandatory.
4. Add `pricing-analyst` (if installed) whenever the artifact adds or changes
   ingest, scrape intervals, recording rules, log streams/fields, data
   sources, accounts or other billable usage.
5. If a needed owner is not installed, record it as a gap — do not improvise a
   persona.

## 3. Run the reviews

Start the selected reviewers **in parallel** as sub-agents when the agent
supports it. Each prompt contains verbatim: the persona file, the artifacts,
the constitution, the routing scope and this instruction: *review only your
domain and answer in the mandatory format*. Phase-specific questions:

| Phase | Domain persona | Engineering persona | Budget persona |
| --- | --- | --- | --- |
| specify | Are sources, semantics, exclusions and a measurable acceptance criterion per site defined? | — | Is ingest impact named? |
| plan | Does the plan cover all domain requirements; are sources verified? | Is the approach viable; constitution check correct; gates, rollback and secrets handled? | Is the added usage per account quantified and < 100 %? Relief planned at 80–100 %? |
| tasks | Is there a task that measures the acceptance criterion? | Order, dependencies, testability; validation gates as tasks? | Is there a task that measures usage after the change; relief before ingest? |
| implement | Is the measured value in the expected range; exclusions present? | Measurements present, gates green, diff minimal? | Measured usage matches the projection? |

Without sub-agent support, review the roles one after another yourself and
label the result **role review** instead of independent approval.

Mandatory answer format for every reviewer:

```text
Verdict: Approve | Approve with conditions | Objection
Findings:
- [blocking|minor] <location> — <problem> — <concrete fix>
Verified: <commands/measurements> | Assumed: <...>
```

## 4. Consensus

- All reviewers approve and nothing is blocking → gate passed.
- An objection goes **verbatim** to the author for correction, then re-review.
  At most `review.max_rounds` (default **2**) correction rounds.
- A trade-off or no consensus after the last round → put both positions side
  by side with numbers and options and let the user decide. In unattended
  runs the gate stays blocked. Never prioritize domain, cost or safety
  silently.

## 5. Record

Append to `FEATURE_DIR/reviews.md` (or `review.log_file`); create it if
missing, never overwrite:

```markdown
## <phase> — <YYYY-MM-DD>, round <n>

| Persona | Verdict | Blocking | Minor |
| --- | --- | --- | --- |
| <persona> | … | … | … |

### Findings
…(verbatim)…

### Verification
Verified: … | Assumed: … | Not executed: …

### Decision
Gate passed | User decision: … | open
```

Durable insights additionally go to the project history/decision log with
date and how they were verified. If another repository is affected, prepare a
cross-repository issue that links the PR.

## 6. Result

Return one line to the calling command:
`Persona review <phase>: passed | blocked (<n> blocking) | skipped (<reason>)`.
When **blocked**, the next Spec Kit phase must not start.
