# SpecKit Personas

Reusable review personas (custom agents) collected from
[@bjoernhoefer](https://github.com/bjoernhoefer)'s repositories, packaged as a
[Spec Kit](https://github.com/github/spec-kit) extension with a persona review
gate. The personas are project-agnostic: project facts (hosts, accounts, data
sources, limits, commands) live in each project's `AGENTS.md`, constitution and
history. See [docs/provenance.md](docs/provenance.md) for sources.

## Catalog

| Persona | Group | Use for |
| --- | --- | --- |
| `review-orchestrator` | orchestration | Routes questions to one owner, runs T0–T3 triage, cross-reviews and the review gate |
| `python-architecture` | engineering | Lean, modular Python services, APIs, adapters, persistence |
| `python-container-engineer` | engineering | Python services plus reproducible Docker/Compose runtime, arm64 edge hosts |
| `ui-ux-developer` | engineering | Accessible, responsive web UI without new frameworks |
| `quality-documentation` | engineering | Risk-based tests, regressions, accurate docs (mandatory for T2/T3) |
| `azure-specialist` | infrastructure | Azure resources, Terraform safety, identity, recurring cost |
| `docker-container-specialist` | infrastructure | Images, Compose, health checks, volumes, upgrades, secrets |
| `networking-connectivity-specialist` | infrastructure | VNets, NSGs/firewalls, DNS, TLS, SSH, VPNs, end-to-end paths |
| `infra-request-validator` | infrastructure | Read-only check of infra requests against constitution and module catalog |
| `grafana-engineer` | observability | PromQL/LogQL, dashboards, panels, dashboard pipeline |
| `telemetry-ingest-specialist` | observability | OTel Collector/Alloy, labels, cardinality, ingest volume |
| `pricing-analyst` | observability | Free-tier/quota limits, usage measurement, cost of changes |
| `home-assistant-data-specialist` | domain | Meaning, units and gaps of Home Assistant data |
| `home-assistant-enthusiast` | domain | Home Assistant integration usability (REST sensors, YAML, automations) |
| `adsb-enthusiast` | domain | ADS-B/Mode S fields, readsb/ultrafeeder, reception quality |
| `eumetsat-specialist` | domain | EUMETSAT/Meteosat/MTG satellite products and nowcasting |

## Install

New project:

```bash
specify init my-project --integration copilot \
  --extension https://github.com/bjoernhoefer/speckit_personas/archive/refs/heads/main.zip \
  --trust-extension-urls
```

Existing project:

```bash
specify extension add personas \
  --from https://github.com/bjoernhoefer/speckit_personas/archive/refs/heads/main.zip
```

Then, in your agent:

- `/speckit-personas-select` (Copilot) / `/speckit.personas.select` — proposes
  personas for the project, installs them to `.github/agents/` (Claude:
  `.claude/agents/`) and fills routing in
  `.specify/extensions/personas/personas-config.yml`. Also offered after
  `/speckit.constitution`.
- `/speckit-personas-review` / `/speckit.personas.review` — review gate. Runs
  optionally after `specify` and mandatorily after `plan`, `tasks` and
  `implement`; appends results to `FEATURE_DIR/reviews.md` and blocks the next
  phase on unresolved objections (max. 2 correction rounds, then the user
  decides).

Helper script (installed at `.specify/extensions/personas/scripts/bash/personas.sh`):

```bash
personas.sh list [--json]          # catalog
personas.sh installed              # personas present in the project
personas.sh install [--force] NAME...
personas.sh update                 # refresh installed personas from the catalog
```

To pick up catalog changes: `specify extension update personas` (or remove and
re-add), then `personas.sh update`. `update` overwrites local edits to
installed persona files — keep project specifics in `AGENTS.md` instead.

## Maintaining

- One persona per file: `personas/<group>/<name>.agent.md`, front matter
  `name` equal to the file name and a `description`.
- Keep personas project-agnostic — no hosts, IPs, accounts, UIDs or
  measurements. Tell the persona where to read project facts instead.
- Keep the shared review answer format (`Verdict` / `Findings` /
  `Verified | Assumed`) so the review gate can aggregate results.
- Add new personas to the catalog above and to `docs/provenance.md`, and bump
  `extension.version` in `extension.yml`.
- Every persona points to `AGENTS.md` for project facts. Reviewer personas
  also include the shared review answer format.

## Tests

CI (`.github/workflows/validate.yml`) runs on every PR and push to `main`:

| Job | What it checks |
| --- | --- |
| lint | ShellCheck for `scripts/` and `tests/` |
| persona & script tests | `pytest`: front matter, naming, structure, review format, `AGENTS.md` contract, no private IPs/e-mails/secrets/placeholders, English only, catalog and provenance listings, manifest/hooks/commands, cross-references, `personas.sh` behavior |
| install into Spec Kit | `tests/integration.sh` for Copilot and Claude: `specify init` + extension install from the working tree and from a GitHub-style archive URL, skills, hooks, persona install |

Run locally:

```bash
pip install -r tests/requirements.txt && pytest
bash tests/integration.sh copilot   # needs the `specify` CLI
```
