#!/bin/bash
# Weekly: ask a short Sonnet run to draw conclusions from the daily snapshots.
# Read-only analysis; the result lands in ~/.claude/model-manager/reviews/.
set -euo pipefail
ROOT="$HOME/.claude/model-manager"
SOURCE="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/reviews"
cd "$ROOT"
OUT="reviews/$(date +%F).md"
PROMPT="Oceń działanie pluginu model-manager. Polityka: $SOURCE/hooks/policy.md. Dane: pliki JSON w snapshots/ (narastająco od 2026-11-01, pierwszego pełnego dnia po wdrożeniu; ostatni plik jest najpełniejszy) oraz wcześniejsze wnioski w reviews/. Punkt odniesienia z 14 dni przed wdrożeniem: subagenci Sonnet 57% kosztu, sesja główna Opus 31%, subagenci Opus 11%, Haiku poniżej 1%; 74% zapisów cache subagentów Sonnet po przerwie ponad 5 minut. Napisz po polsku, maksymalnie 300 słów: co się zmieniło względem punktu odniesienia (liczby), co działa, co nie działa, i maksymalnie 3 konkretne zmiany w tabeli lub zasadach, każda z dowodem z danych. Liczby mniejsze niż 20 zleceń oznacz jako niewystarczające. Niczego nie zmieniaj."
timeout 300 claude -p --model sonnet --effort medium --allowedTools Read --disallowedTools Edit,Write,Bash,Agent > "$OUT.tmp" <<< "$PROMPT"
mv "$OUT.tmp" "$OUT"
