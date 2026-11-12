import pathlib
import re

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PERSONA_FILES = sorted((ROOT / "personas").glob("*/*.agent.md"))
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def parse_persona(path):
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        raise AssertionError(f"{path.relative_to(ROOT)}: missing or unclosed front matter")
    return yaml.safe_load(match.group(1)), match.group(2)


@pytest.fixture(scope="session")
def root():
    return ROOT


@pytest.fixture(scope="session")
def persona_names():
    return {p.name.removesuffix(".agent.md") for p in PERSONA_FILES}


@pytest.fixture(scope="session")
def manifest():
    return yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8"))
