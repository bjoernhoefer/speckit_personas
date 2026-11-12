#!/usr/bin/env bash
# End-to-end test: install this extension into fresh Spec Kit projects, both
# from the working tree (--dev) and from a GitHub-style archive (--from URL).
#
# Usage: tests/integration.sh [copilot|claude]   (requires `specify` on PATH)
set -euo pipefail

INTEGRATION="${1:-copilot}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
SERVER_PID=""
cleanup() {
  [[ -n "$SERVER_PID" ]] && kill "$SERVER_PID" 2>/dev/null
  rm -rf "$WORK"
}
trap cleanup EXIT

case "$INTEGRATION" in
  copilot) SKILLS=.github/skills; AGENT_FILE=.github/agents/grafana-engineer.agent.md ;;
  claude) SKILLS=.claude/skills; AGENT_FILE=.claude/agents/grafana-engineer.md ;;
  *) echo "unsupported integration: $INTEGRATION" >&2; exit 2 ;;
esac

fail() { echo "FAIL: $*" >&2; exit 1; }

new_project() {
  local dir="$WORK/$1"
  mkdir -p "$dir" && git -C "$dir" init -q
  (cd "$dir" && specify init --here --integration "$INTEGRATION" --script sh --force --ignore-agent-tools >/dev/null)
  echo "$dir"
}

verify_project() {
  local dir="$1" ext="$1/.specify/extensions/personas"
  [[ -f "$ext/extension.yml" ]] || fail "extension not installed in $dir"
  [[ -f "$ext/personas-config.yml" ]] || fail "config not scaffolded"
  [[ ! -e "$ext/tests" ]] || fail ".extensionignore not honored (tests/ copied)"
  for skill in speckit-personas-select speckit-personas-review; do
    [[ -d "$dir/$SKILLS/$skill" ]] || fail "skill $skill not registered in $SKILLS"
  done
  python3 - "$dir/.specify/extensions.yml" <<'EOF' || fail "hooks not registered"
import sys, yaml
hooks = yaml.safe_load(open(sys.argv[1]))["hooks"]
for event in ("after_plan", "after_tasks", "after_implement"):
    entry = next(h for h in hooks[event] if h["extension"] == "personas")
    assert entry["command"] == "speckit.personas.review" and entry["optional"] is False, event
assert any(h["extension"] == "personas" for h in hooks["after_constitution"])
EOF
  (cd "$dir" && bash .specify/extensions/personas/scripts/bash/personas.sh install review-orchestrator grafana-engineer >/dev/null)
  [[ -f "$dir/$AGENT_FILE" ]] || fail "persona not installed to $AGENT_FILE"
  [[ "$(cd "$dir" && bash .specify/extensions/personas/scripts/bash/personas.sh installed | wc -l)" -eq 2 ]] \
    || fail "installed count mismatch"
}

echo "== $INTEGRATION: install from working tree (--dev)"
dev="$(new_project dev)"
(cd "$dev" && specify extension add --dev "$ROOT" >/dev/null)
verify_project "$dev"

echo "== $INTEGRATION: install from archive URL (nested root like GitHub)"
mkdir -p "$WORK/www"
git -C "$ROOT" archive --format=zip --prefix=speckit_personas-main/ -o "$WORK/www/main.zip" HEAD
PORT="$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$WORK/www" >/dev/null 2>&1 &
SERVER_PID=$!
for _ in $(seq 20); do curl -fs "http://127.0.0.1:$PORT/main.zip" -o /dev/null && break; sleep 0.25; done
arc="$(new_project archive)"
(cd "$arc" && printf 'y\n' | specify extension add --from "http://127.0.0.1:$PORT/main.zip" >/dev/null)
verify_project "$arc"

echo "PASS: $INTEGRATION"
