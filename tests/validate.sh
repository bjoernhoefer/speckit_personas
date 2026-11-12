#!/usr/bin/env bash
# Validates the persona catalog and the extension manifest.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
errors=0
fail() { echo "FAIL: $*" >&2; errors=$((errors + 1)); }

names=()
while IFS= read -r f; do
  rel="${f#"$ROOT"/}"
  base="$(basename "$f" .agent.md)"
  [[ "$(head -n1 "$f")" == "---" ]] || fail "$rel: missing front matter"
  name="$(awk 'NR>1 && /^---$/{exit} /^name:/{sub(/^name:[[:space:]]*/,""); print}' "$f")"
  desc="$(awk 'NR>1 && /^---$/{exit} /^description:/{sub(/^description:[[:space:]]*/,""); print}' "$f")"
  [[ "$name" == "$base" ]] || fail "$rel: name '$name' does not match file name '$base'"
  [[ -n "$desc" ]] || fail "$rel: empty description"
  [[ "$base" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || fail "$rel: name must be lowercase kebab-case"
  grep -q "\`$base\`" "$ROOT/README.md" || fail "$rel: not listed in README.md"
  grep -q "\`$base\`" "$ROOT/docs/provenance.md" || fail "$rel: not listed in docs/provenance.md"
  # Personas must stay project-agnostic: no private IPs or e-mail addresses.
  if grep -nE '\b(10|192\.168|172\.(1[6-9]|2[0-9]|3[01]))\.[0-9]+\.[0-9]+\b|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' "$f"; then
    fail "$rel: contains a private IP address or e-mail address"
  fi
  names+=("$base")
done < <(find "$ROOT/personas" -type f -name '*.agent.md' | sort)

dupes="$(printf '%s\n' "${names[@]}" | sort | uniq -d)"
[[ -z "$dupes" ]] || fail "duplicate persona names: $dupes"

# Every command file referenced by the manifest must exist.
while IFS= read -r file; do
  [[ -f "$ROOT/$file" ]] || fail "extension.yml references missing file: $file"
done < <(sed -n 's/^[[:space:]]*\(file\|template\):[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}[[:space:]]*$/\2/p' "$ROOT/extension.yml")

echo "${#names[@]} personas checked, $errors error(s)"
[[ $errors -eq 0 ]]
