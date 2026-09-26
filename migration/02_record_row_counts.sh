#!/bin/sh
# 02_record_row_counts.sh — per-table row-count baseline from ANY database URL.
#
# STRICTLY READ-ONLY: issues only SELECT count(*) queries. Safe to run against
# the live Render database, a local test restore, or Supabase.
#
# Required env:
#   DATABASE_URL   Connection string of the database to measure.
#   OUT_CSV        Destination CSV path (e.g. migration/backups/row_counts_render_2026-01-01.csv).
# Usage:
#   DATABASE_URL='postgres://...' OUT_CSV=migration/backups/row_counts_render.csv sh migration/02_record_row_counts.sh
#
# Required tools: psql.
set -eu

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set. Aborting." >&2
  exit 2
fi
if [ -z "${OUT_CSV:-}" ]; then
  echo "ERROR: OUT_CSV is not set. Aborting." >&2
  exit 2
fi
command -v psql >/dev/null 2>&1 || { echo "ERROR: psql not found in PATH." >&2; exit 2; }

TABLES_FILE="${TABLES_FILE:-migration/tables.txt}"
RECORDED_AT="$(date -u +%FT%TZ)"
TMP_OUT="${OUT_CSV}.tmp"
printf 'table,count,recorded_at\n' > "$TMP_OUT"

while IFS= read -r table || [ -n "$table" ]; do
  case "$table" in ''|\#*) continue ;; esac
  exists="$(psql "$DATABASE_URL" -tAX -c "SELECT to_regclass('public.$table') IS NOT NULL;")"
  if [ "$exists" != "t" ]; then
    printf '%s,MISSING,%s\n' "$table" "$RECORDED_AT" >> "$TMP_OUT"
    echo "   MISSING: $table" >&2
    continue
  fi
  count="$(psql "$DATABASE_URL" -tAX -c "SELECT count(*) FROM public.\"$table\";")"
  printf '%s,%s,%s\n' "$table" "$count" "$RECORDED_AT" >> "$TMP_OUT"
  echo "   $table = $count" >&2
done < "$TABLES_FILE"

mv "$TMP_OUT" "$OUT_CSV"
echo "OK: baseline written: $OUT_CSV"
