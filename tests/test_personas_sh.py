"""Behavior of scripts/bash/personas.sh against throwaway projects."""
import json
import os
import subprocess

import pytest

from conftest import PERSONA_FILES, ROOT

SCRIPT = ROOT / "scripts" / "bash" / "personas.sh"


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".specify").mkdir()
    return tmp_path


def run(project, *args, integration=None, env=None, check=True):
    if integration:
        (project / ".specify" / "init-options.json").write_text(json.dumps({"integration": integration}))
    full_env = {k: v for k, v in os.environ.items() if k != "PERSONAS_DEST"}
    full_env.update({"PROJECT_ROOT": str(project), **(env or {})})
    result = subprocess.run(["bash", str(SCRIPT), *args], cwd=project, env=full_env,
                            capture_output=True, text=True)
    if check:
        assert result.returncode == 0, result.stderr
    return result


def test_list_shows_every_persona(project, persona_names):
    out = run(project, "list").stdout
    listed = {line.split()[0] for line in out.splitlines() if line.strip()}
    assert listed == persona_names


def test_list_json_is_valid(project, persona_names):
    data = json.loads(run(project, "list", "--json").stdout)
    assert {d["name"] for d in data} == persona_names
    for entry in data:
        assert entry["category"] and entry["description"]


def test_install_copilot_layout_copies_verbatim(project):
    run(project, "install", "grafana-engineer", "review-orchestrator")
    dst = project / ".github/agents/grafana-engineer.agent.md"
    src = ROOT / "personas/observability/grafana-engineer.agent.md"
    assert dst.read_bytes() == src.read_bytes()
    assert (project / ".github/agents/review-orchestrator.agent.md").is_file()


def test_install_claude_layout(project):
    run(project, "install", "adsb-enthusiast", integration="claude")
    assert (project / ".claude/agents/adsb-enthusiast.md").is_file()
    assert not (project / ".github/agents").exists()


def test_personas_dest_override(project):
    run(project, "install", "pricing-analyst", env={"PERSONAS_DEST": str(project / "custom")})
    assert (project / "custom/pricing-analyst.agent.md").is_file()


def test_install_skips_existing_without_force(project):
    run(project, "install", "pricing-analyst")
    dst = project / ".github/agents/pricing-analyst.agent.md"
    dst.write_text("local edit")
    out = run(project, "install", "pricing-analyst").stdout
    assert "skipped" in out
    assert dst.read_text() == "local edit"
    run(project, "install", "--force", "pricing-analyst")
    assert dst.read_text() != "local edit"


def test_unknown_persona_fails_but_installs_the_rest(project):
    result = run(project, "install", "does-not-exist", "ui-ux-developer", check=False)
    assert result.returncode != 0
    assert "unknown persona 'does-not-exist'" in result.stderr
    assert (project / ".github/agents/ui-ux-developer.agent.md").is_file()


def test_install_without_names_fails(project):
    assert run(project, "install", check=False).returncode == 2


def test_installed_and_update(project):
    assert run(project, "installed").stdout == ""
    assert "no personas installed" in run(project, "update").stdout
    run(project, "install", "azure-specialist", "eumetsat-specialist")
    assert set(run(project, "installed").stdout.split()) == {"azure-specialist", "eumetsat-specialist"}
    dst = project / ".github/agents/azure-specialist.agent.md"
    dst.write_text("stale")
    run(project, "update")
    assert dst.read_bytes() == (ROOT / "personas/infrastructure/azure-specialist.agent.md").read_bytes()


def test_install_all_personas(project):
    names = [p.name.removesuffix(".agent.md") for p in PERSONA_FILES]
    run(project, "install", *names)
    assert sorted(p.name for p in (project / ".github/agents").iterdir()) == sorted(p.name for p in PERSONA_FILES)


def test_usage_on_unknown_command(project):
    result = run(project, "bogus", check=False)
    assert result.returncode == 2
    assert "Usage" in result.stdout
