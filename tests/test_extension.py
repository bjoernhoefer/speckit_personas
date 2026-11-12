"""Spec Kit extension manifest, commands and cross-references."""
import re

import pytest
import yaml

from conftest import PERSONA_FILES, ROOT, parse_persona

HOOK_EVENTS = {
    f"{when}_{phase}"
    for when in ("before", "after")
    for phase in ("constitution", "specify", "clarify", "plan", "tasks", "implement", "analyze", "checklist")
}


def test_manifest_required_fields(manifest):
    assert manifest["schema_version"] == "1.0"
    ext = manifest["extension"]
    assert ext["id"] == "personas"
    assert re.fullmatch(r"\d+\.\d+\.\d+", ext["version"]), "version must be semver"
    for key in ("name", "description", "author", "repository"):
        assert ext.get(key), f"extension.{key} missing"
    assert manifest["requires"]["speckit_version"]


def test_commands_are_namespaced_and_exist(manifest):
    commands = manifest["provides"]["commands"]
    assert commands
    for cmd in commands:
        assert re.fullmatch(r"speckit\.personas\.[a-z][a-z0-9-]*", cmd["name"])
        path = ROOT / cmd["file"]
        assert path.is_file(), f"{cmd['file']} missing"
        text = path.read_text(encoding="utf-8")
        meta = yaml.safe_load(re.match(r"\A---\n(.*?)\n---\n", text, re.S).group(1))
        assert meta.get("description"), f"{cmd['file']} needs a description"
        assert "$ARGUMENTS" in text, f"{cmd['file']} ignores user input"


def test_hooks_reference_provided_commands(manifest):
    provided = {c["name"] for c in manifest["provides"]["commands"]}
    for event, hook in manifest["hooks"].items():
        assert event in HOOK_EVENTS, f"unknown hook event {event}"
        assert hook["command"] in provided
        assert isinstance(hook.get("optional"), bool)


def test_review_gate_is_mandatory_after_plan_tasks_implement(manifest):
    for event in ("after_plan", "after_tasks", "after_implement"):
        hook = manifest["hooks"][event]
        assert hook["command"] == "speckit.personas.review"
        assert hook["optional"] is False


def test_config_template_is_valid(manifest):
    for cfg in manifest["provides"]["config"]:
        data = yaml.safe_load((ROOT / cfg["template"]).read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert isinstance(data["routing"], dict)
        assert data["review"]["max_rounds"] >= 1


@pytest.mark.parametrize(
    "path",
    [*sorted((ROOT / "commands").glob("*.md")), ROOT / "personas-config.template.yml", *PERSONA_FILES],
    ids=lambda p: p.relative_to(ROOT).as_posix(),
)
def test_referenced_personas_exist(path, persona_names):
    text = path.read_text(encoding="utf-8")
    # Backticked kebab-case names that look like persona references.
    refs = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", text))
    persona_like = {r for r in refs if re.search(r"-(specialist|engineer|enthusiast|analyst|orchestrator|developer|documentation|architecture|validator)$", r)}
    assert persona_like <= persona_names, f"unknown personas referenced: {persona_like - persona_names}"


def test_extension_paths_referenced_in_commands_exist():
    for cmd in (ROOT / "commands").glob("*.md"):
        for rel in re.findall(r"\.specify/extensions/personas/([\w./-]+\.(?:sh|yml|md))", cmd.read_text(encoding="utf-8")):
            if rel == "personas-config.yml":  # scaffolded from the template at install time
                continue
            assert (ROOT / rel).is_file(), f"{cmd.name} references missing {rel}"


def test_extensionignore_keeps_runtime_files():
    ignored = [line.strip().rstrip("/") for line in (ROOT / ".extensionignore").read_text().splitlines()
               if line.strip() and not line.startswith("#")]
    for needed in ("personas", "commands", "scripts", "extension.yml", "personas-config.template.yml"):
        assert needed not in ignored


def test_orchestrator_knows_mandatory_reviewers():
    _, body = parse_persona(ROOT / "personas/orchestration/review-orchestrator.agent.md")
    for name in ("quality-documentation", "pricing-analyst"):
        assert f"`{name}`" in body
