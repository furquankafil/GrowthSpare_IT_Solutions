#!/bin/sh
# 04_compare_row_counts.sh — verify Supabase matches the Render baseline.
#
# READ-ONLY against both sides (re-records the target with SELECT count(*)
# and diffs against the baseline CSV). Exits 0 only on a full match.
#
# Required env:
#   BASELINE_CSV   CSV produced by 02_record_row_counts.sh against Render.
#   DATABASE_URL   Connection string of the RESTORED (Supabase) database.
#   OUT_CSV        Where to write the fresh target counts CSV.
# Usage:
#   BASELINE_CSV=migration/backups/row_counts_render.csv \
#   DATABASE_URL='postgres://...' \
#   OUT_CSV=migration/backups/row_counts_supabase.csv \
#   sh migration/04_compare_row_counts.sh
set -eu

if [ -z "${BASELINE_CSV:-}" ] || [ ! -f "$BASELINE_CSV" ]; then
  echo "ERROR: BASELINE_CSV missing. Aborting." >&2
  exit 2
fi
if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL (restore target) is not set. Aborting." >&2
  exit 2
fi
if [ -z "${OUT_CSV:-}" ]; then
  echo "ERROR: OUT_CSV is not set. Aborting." >&2
  exit 2
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DATABASE_URL="$DATABASE_URL" OUT_CSV="$OUT_CSV" TABLES_FILE="$SCRIPT_DIR/tables.txt" \
  sh "$SCRIPT_DIR/02_record_row_counts.sh"

echo "-> Comparing baseline vs restored..."
MISMATCH=0
while IFS=, read -r table base_count _rest; do
  case "$table" in table|\#*|'') continue ;; esac
  target_count="$(awk -F, -v t="$table" '$1==t {print $2}' "$OUT_CSV")"
  if [ "$target_count" != "$base_count" ]; then
    echo "MISMATCH: $table baseline=$base_count restored=${target_count:-<absent>}"
    MISMATCH=1
  fi
done < "$BASELINE_CSV"

if [ "$MISMATCH" -ne 0 ]; then
  echo "RESULT: FAIL — counts differ. Do NOT cut over." >&2
  exit 1
fi
echo "RESULT: PASS — all table counts match."
