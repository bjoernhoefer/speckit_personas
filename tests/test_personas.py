"""Content rules every persona in the catalog must satisfy."""
import re

import pytest

from conftest import PERSONA_FILES, ROOT, parse_persona

GROUPS = {"orchestration", "engineering", "infrastructure", "observability", "domain"}
# Personas that do not take part in the review gate and use their own output format.
NON_REVIEWERS = {"review-orchestrator", "infra-request-validator"}

SENSITIVE = {
    "private IPv4 address": r"\b(?:10|127|192\.168|172\.(?:1[6-9]|2\d|3[01]))(?:\.\d{1,3}){2,3}\b",
    "e-mail address": r"[\w.%+-]+@[\w-]+\.[\w.-]*[a-z]{2,}",
    "SSH private key path": r"\bid_(?:rsa|ed25519|ecdsa)\b",
    "home directory path": r"(?:/home/|/Users/|C:\\Users\\)\w+",
    "secret/token": r"\b(?:ghp_|github_pat_|glc_|glsa_|AKIA)[A-Za-z0-9_]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "unresolved placeholder": r"\b(?:TODO|TBD|FIXME|XXX)\b",
}

GERMAN = re.compile(r"[äöüÄÖÜß]|\b(?:und|nicht|oder|wird|sind|für|bitte|Spezialist)\b")

ids = [p.name.removesuffix(".agent.md") for p in PERSONA_FILES]


def test_catalog_is_not_empty():
    assert len(PERSONA_FILES) >= 10


def test_persona_names_are_unique():
    assert len(ids) == len(set(ids))


@pytest.fixture(params=PERSONA_FILES, ids=ids)
def persona(request):
    path = request.param
    meta, body = parse_persona(path)
    return {
        "path": path,
        "rel": path.relative_to(ROOT).as_posix(),
        "name": path.name.removesuffix(".agent.md"),
        "group": path.parent.name,
        "meta": meta,
        "body": body,
        "text": path.read_text(encoding="utf-8"),
    }


def test_front_matter_fields(persona):
    meta = persona["meta"]
    assert isinstance(meta, dict), "front matter must be a YAML mapping"
    assert set(meta) <= {"name", "description", "tools", "model"}, f"unexpected keys: {set(meta)}"
    assert meta.get("name") == persona["name"], "front matter name must equal the file name"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", persona["name"]), "name must be kebab-case"


def test_description_is_useful(persona):
    desc = persona["meta"].get("description")
    assert isinstance(desc, str) and "\n" not in desc.strip()
    assert 60 <= len(desc) <= 500, f"description length {len(desc)} outside 60..500"


def test_group_directory_is_known(persona):
    assert persona["group"] in GROUPS


def test_body_structure(persona):
    body = persona["body"].lstrip()
    assert body.startswith("# "), "body must start with an H1 title"
    assert len(re.findall(r"^## ", body, re.M)) >= 3, "persona needs at least three sections"
    assert len(body.splitlines()) >= 30, "persona body is too short to be a usable role"
    assert body.count("```") % 2 == 0, "unbalanced code fences"


def test_reads_project_facts_from_project(persona):
    assert "AGENTS.md" in persona["body"], "persona must point to AGENTS.md for project facts"


def test_review_answer_format(persona):
    if persona["name"] in NON_REVIEWERS:
        pytest.skip("not a review-gate participant")
    body = persona["body"]
    assert re.search(r"^Verdict: .*Approve.*Objection", body, re.M), "missing Verdict line"
    assert re.search(r"^Findings:\n- \[blocking\|minor\]", body, re.M), "missing Findings format"
    assert "Assumed:" in body, "missing Verified/Sources | Assumed line"


@pytest.mark.parametrize("kind", SENSITIVE)
def test_no_sensitive_or_project_specific_data(persona, kind):
    hits = [
        f"{persona['rel']}:{n}: {line.strip()}"
        for n, line in enumerate(persona["text"].splitlines(), 1)
        if re.search(SENSITIVE[kind], line)
    ]
    assert not hits, f"{kind} found:\n" + "\n".join(hits)


def test_written_in_english(persona):
    hits = [line for line in persona["text"].splitlines() if GERMAN.search(line)]
    assert not hits, "German text found:\n" + "\n".join(hits)


def test_listed_in_readme_catalog(persona):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    row = re.search(rf"^\| `{re.escape(persona['name'])}` \| (\w+) \|", readme, re.M)
    assert row, "persona missing from README catalog table"
    assert row.group(1) == persona["group"], "README group does not match directory"


def test_listed_in_provenance(persona):
    provenance = (ROOT / "docs" / "provenance.md").read_text(encoding="utf-8")
    assert re.search(rf"^\| `{re.escape(persona['name'])}` \|", provenance, re.M)


def test_readme_lists_no_unknown_personas(persona_names):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"^\| `([a-z0-9-]+)` \|", readme, re.M))
    assert listed == persona_names
