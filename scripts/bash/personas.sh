#!/usr/bin/env bash
# List and install personas from this extension into a Spec Kit project.
#
# Usage:
#   personas.sh list [--json]              list available personas
#   personas.sh installed                  list personas installed in the project
#   personas.sh install [--force] NAME...  install personas as custom agents
#   personas.sh update                     reinstall all installed personas (overwrites)
#
# Environment:
#   PROJECT_ROOT    project root (default: git top level or current directory)
#   PERSONAS_DEST   target directory (default: derived from the Spec Kit integration)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CATALOG_DIR="$EXT_ROOT/personas"

PROJECT_ROOT="${PROJECT_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

integration() {
  local opts="$PROJECT_ROOT/.specify/init-options.json"
  if [[ -f "$opts" ]]; then
    sed -n 's/.*"integration"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$opts" | head -n1
  fi
}

# Claude Code reads .claude/agents/<name>.md; everything else uses the
# GitHub Copilot layout .github/agents/<name>.agent.md.
dest_dir() {
  if [[ -n "${PERSONAS_DEST:-}" ]]; then
    echo "$PERSONAS_DEST"
  elif [[ "$(integration)" == "claude" ]]; then
    echo "$PROJECT_ROOT/.claude/agents"
  else
    echo "$PROJECT_ROOT/.github/agents"
  fi
}

dest_file() {
  local name="$1" dir
  dir="$(dest_dir)"
  if [[ "$dir" == */.claude/agents ]]; then
    echo "$dir/$name.md"
  else
    echo "$dir/$name.agent.md"
  fi
}

frontmatter_field() {
  local file="$1" field="$2"
  awk -v f="$field" '
    NR == 1 && $0 == "---" { inside = 1; next }
    inside && $0 == "---" { exit }
    inside && index($0, f ":") == 1 { sub("^" f ":[[:space:]]*", ""); print; exit }
  ' "$file"
}

catalog_files() {
  find "$CATALOG_DIR" -type f -name '*.agent.md' | sort
}

source_file() {
  local name="$1"
  catalog_files | while read -r f; do
    if [[ "$(basename "$f" .agent.md)" == "$name" ]]; then
      echo "$f"
      return
    fi
  done
}

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '%s' "$s"
}

cmd_list() {
  local json=false first=true
  [[ "${1:-}" == "--json" ]] && json=true
  $json && printf '['
  while read -r f; do
    local name category desc
    name="$(basename "$f" .agent.md)"
    category="$(basename "$(dirname "$f")")"
    desc="$(frontmatter_field "$f" description)"
    if $json; then
      $first || printf ','
      first=false
      printf '{"name":"%s","category":"%s","description":"%s"}' \
        "$(json_escape "$name")" "$(json_escape "$category")" "$(json_escape "$desc")"
    else
      printf '%-36s %-15s %s\n' "$name" "$category" "$desc"
    fi
  done < <(catalog_files)
  $json && printf ']\n'
  return 0
}

cmd_installed() {
  while read -r f; do
    local name
    name="$(basename "$f" .agent.md)"
    [[ -f "$(dest_file "$name")" ]] && echo "$name"
  done < <(catalog_files)
  return 0
}

cmd_install() {
  local force=false names=() failed=0
  for arg in "$@"; do
    case "$arg" in
      --force) force=true ;;
      *) names+=("$arg") ;;
    esac
  done
  if [[ ${#names[@]} -eq 0 ]]; then
    echo "error: no persona names given (see: $0 list)" >&2
    return 2
  fi
  mkdir -p "$(dest_dir)"
  for name in "${names[@]}"; do
    local src dst
    src="$(source_file "$name")"
    dst="$(dest_file "$name")"
    if [[ -z "$src" ]]; then
      echo "error: unknown persona '$name'" >&2
      failed=1
      continue
    fi
    if [[ -f "$dst" ]] && ! $force; then
      echo "skipped   $name (exists: ${dst#"$PROJECT_ROOT"/}; use --force to overwrite)"
      continue
    fi
    cp "$src" "$dst"
    echo "installed $name -> ${dst#"$PROJECT_ROOT"/}"
  done
  return "$failed"
}

cmd_update() {
  local installed=()
  mapfile -t installed < <(cmd_installed)
  if [[ ${#installed[@]} -eq 0 ]]; then
    echo "no personas installed"
    return 0
  fi
  cmd_install --force "${installed[@]}"
}

case "${1:-}" in
  list) shift; cmd_list "$@" ;;
  installed) shift; cmd_installed ;;
  install) shift; cmd_install "$@" ;;
  update) shift; cmd_update ;;
  *)
    sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
