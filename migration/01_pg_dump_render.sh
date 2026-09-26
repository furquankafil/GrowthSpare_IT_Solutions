#!/bin/sh
# 01_pg_dump_render.sh — verified backup of the LIVE Render PostgreSQL database.
#
# READ-ONLY against production (pg_dump never writes to the source database).
# Writes ONLY to migration/backups/ (git-ignored).
#
# Required env:
#   RENDER_DATABASE_URL   External connection string from the Render dashboard
#                         (growthspare-db -> Connect -> External Connection String).
#                         NEVER commit this value. NEVER echo it (this script won't).
# Usage:
#   RENDER_DATABASE_URL='postgres://...' sh migration/01_pg_dump_render.sh
#   # optional custom path: RENDER_DATABASE_URL='...' OUT_DUMP=path.dump sh ...
#
# Required tools: pg_dump, pg_restore (PostgreSQL client tools).
set -eu

if [ -z "${RENDER_DATABASE_URL:-}" ]; then
  echo "ERROR: RENDER_DATABASE_URL is not set. Aborting (nothing was touched)." >&2
  exit 2
fi
command -v pg_dump >/dev/null 2>&1 || { echo "ERROR: pg_dump not found in PATH." >&2; exit 2; }
command -v pg_restore >/dev/null 2>&1 || { echo "ERROR: pg_restore not found in PATH." >&2; exit 2; }

BACKUP_DIR="migration/backups"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%F_%H%M)"
OUT_DUMP="${OUT_DUMP:-$BACKUP_DIR/growthspare_render_${STAMP}.dump}"

if [ -e "$OUT_DUMP" ] && [ "${OVERWRITE:-0}" != "1" ]; then
  echo "ERROR: $OUT_DUMP already exists. Set OVERWRITE=1 to replace it." >&2
  exit 2
fi

echo "-> Dumping Render production database (custom format, compressed)..."
echo "   destination: $OUT_DUMP"
DUMP_LOG="${OUT_DUMP}.log"
if pg_dump "$RENDER_DATABASE_URL" --format=custom --compress=9 --verbose \
    --file="$OUT_DUMP" >"$DUMP_LOG" 2>&1; then
  grep -v -i "password" "$DUMP_LOG" || true
else
  grep -v -i "password" "$DUMP_LOG" || true
  echo "ERROR: pg_dump failed (see $DUMP_LOG). Aborting." >&2
  exit 1
fi

echo "-> Verifying dump integrity (table of contents readable)..."
ENTRIES="$(pg_restore --list "$OUT_DUMP" | wc -l)"
TABLES="$(pg_restore --list "$OUT_DUMP" | grep -c "TABLE DATA" || true)"
echo "   toc entries: $ENTRIES, TABLE DATA sections: $TABLES"
if [ "$TABLES" -lt 20 ]; then
  echo "ERROR: unexpectedly few tables in dump ($TABLES). Investigate before proceeding." >&2
  exit 1
fi

echo "OK: backup written and verified: $OUT_DUMP"
echo "NEXT: record the source baseline:"
echo "  RENDER_DATABASE_URL='...' OUT_CSV=migration/backups/row_counts_render_${STAMP}.csv sh migration/02_record_row_counts.sh"
