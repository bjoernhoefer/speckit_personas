# Provenance

The personas were collected on 2026-11-12 from the repositories of
[@bjoernhoefer](https://github.com/bjoernhoefer) and generalized into
project-agnostic versions: repository-specific hosts, IP addresses, account
names, file paths, UIDs and measurements were removed. Those facts belong in
each project's `AGENTS.md`, constitution and history, where the personas are
instructed to read them.

Repositories scanned (non-fork): `e2proxy`, `e2recorder`, `az_universal_vm`,
`ha_satimage`, `raspberrypi_management`, `grafana_dashboards`, `grafana_adsb`,
`grafana_homeassistant`, `ha_weather`, `infra-ai`, `tip-hass`, `ideas`,
`homeassistant_blueprints`, `loganalyticspush`, `overcrypt`, `iGrill_bbqmqtt`,
`test01`, `nodin`, `nodefhem_mqtt`, `techgarden`. Personas were found only in
the repositories listed below.

| Persona | Source(s) | Notes |
| --- | --- | --- |
| `review-orchestrator` | `grafana_dashboards/.github/agents/dashboard-orchestrator.md`, `grafana_adsb/.github/agents/collector-orchestrator.md`, `grafana_homeassistant/.github/agents/ha-orchestrator.md`; risk tiers from `ha_weather/.github/copilot-instructions.md` | Three domain-specific orchestrators merged into one generic moderator with T0–T3 triage. |
| `python-architecture` | `ha_weather/.github/agents/python-architecture.agent.md` | Translated, project name removed. |
| `python-container-engineer` | `grafana_adsb/.github/agents/python-docker-engineer.md` | Renamed; site keys, users and image fingerprints removed. |
| `ui-ux-developer` | `ha_weather/.github/agents/ui-ux-developer.agent.md` | Translated; static-frontend assumption made overridable. |
| `quality-documentation` | `ha_weather/.github/agents/quality-documentation.agent.md` | Translated; bilingual rule generalized to "all maintained languages". |
| `azure-specialist` | `az_universal_vm/.specify/memory/constitution.md` (principles II and VI) | Extracted from the inline constitution persona. |
| `docker-container-specialist` | `az_universal_vm/.specify/memory/constitution.md` (principle III) | Extracted from the inline constitution persona. |
| `networking-connectivity-specialist` | `az_universal_vm/.specify/memory/constitution.md` (principles IV and VI) | Extracted from the inline constitution persona. |
| `infra-request-validator` | `infra-ai/.github/agents/request-validator.agent.md` + `infra-ai/skills/validate-request/SKILL.md` | Skill procedure folded into the persona. |
| `grafana-engineer` | `grafana_dashboards/.github/agents/grafana-engineer.md` (newest), `grafana_homeassistant/.github/agents/grafana-engineer.md` (older duplicate) | Host, folders, UIDs, accounts and user names removed. |
| `telemetry-ingest-specialist` | `grafana_adsb/.github/agents/grafana-specialist.md` | Renamed (it covers ingest, not dashboards); versions and volumes removed. |
| `pricing-analyst` | `grafana_dashboards/.github/agents/pricing-analyst.md` | Account logins, measurements and dated limits removed; limits must be verified per project. |
| `home-assistant-data-specialist` | `grafana_dashboards/.github/agents/homeassistant-spezialist.md` (newest), `grafana_homeassistant/.github/agents/homeassistant-spezialist.md` (older duplicate) | Renamed to English; site names and exclusion specifics generalized. |
| `home-assistant-enthusiast` | `ha_weather/.github/agents/home-assistant-enthusiast.agent.md` | Translated, project endpoints generalized. |
| `adsb-enthusiast` | `grafana_adsb/.github/agents/adsb-enthusiast.md` (canonical domain core), `grafana_dashboards/.github/agents/adsb-enthusiast.md` (consumer variant) | Merged; station names and distances generalized. |
| `eumetsat-specialist` | `ha_weather/.github/agents/eumetsat-specialist.agent.md` | Translated. |

Review gate: `commands/speckit.personas.review.md` and the hooks in
`extension.yml` generalize `grafana_dashboards` and `grafana_adsb`
(`.github/skills/speckit-persona-review/SKILL.md`, `.specify/extensions.yml`).
