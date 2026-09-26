#!/bin/sh
# 03_restore_supabase.sh — restore a verified dump into Supabase PostgreSQL.
#
# SAFETY LOCKS (all must pass or the script aborts before touching anything):
#   1. SUPABASE_DATABASE_URL must be set (direct port 5432 URI from the
#      Supabase dashboard -> Project Settings -> Database -> Connection string).
#   2. DUMP_FILE must point at an existing, verified .dump file.
#   3. SUPABASE_RESTORE_ACK must equal exactly: I-UNDERSTAND-THIS-OVERWRITES-SUPABASE
#   4. The target URL must NOT look like Render/localhost/sqlite (refuses to
#      restore into the production Render database or a dev database).
#
# Restore uses --clean --if-exists --no-owner WITHOUT --create, so it refreshes
# objects inside the existing Supabase database but never drops the database
# itself or other databases on the server.
#
# Usage:
#   SUPABASE_DATABASE_URL='postgres://...' \
#   DUMP_FILE=migration/backups/growthspare_render_<stamp>.dump \
#   SUPABASE_RESTORE_ACK=I-UNDERSTAND-THIS-OVERWRITES-SUPABASE \
#   sh migration/03_restore_supabase.sh
#
# Required tools: pg_restore.
set -eu

if [ -z "${SUPABASE_DATABASE_URL:-}" ]; then
  echo "ERROR: SUPABASE_DATABASE_URL is not set. Aborting (nothing was touched)." >&2
  exit 2
fi
if [ -z "${DUMP_FILE:-}" ] || [ ! -f "$DUMP_FILE" ]; then
  echo "ERROR: DUMP_FILE is missing or not a file. Aborting." >&2
  exit 2
fi
if [ "${SUPABASE_RESTORE_ACK:-}" != "I-UNDERSTAND-THIS-OVERWRITES-SUPABASE" ]; then
  echo "ERROR: explicit acknowledgement missing." >&2
  echo "Set SUPABASE_RESTORE_ACK=I-UNDERSTAND-THIS-OVERWRITES-SUPABASE to proceed." >&2
  exit 2
fi
command -v pg_restore >/dev/null 2>&1 || { echo "ERROR: pg_restore not found in PATH." >&2; exit 2; }

# Refuse targets that look like production Render, local dev, or sqlite.
case "$SUPABASE_DATABASE_URL" in
  *render.com*|*dpg-*|*localhost*|*127.0.0.1*|*sqlite*|*ondemand* )
    echo "ERROR: target URL looks like Render/localhost/sqlite, NOT Supabase. Refusing." >&2
    exit 2
    ;;
esac
case "$SUPABASE_DATABASE_URL" in
  *supabase.co*|*supabase.com*) ;;
  *)
    echo "ERROR: target URL does not look like a Supabase host. Refusing." >&2
    exit 2
    ;;
esac

echo "-> Restoring $DUMP_FILE into Supabase (clean + no-owner, database itself preserved)..."
RESTORE_LOG="${DUMP_FILE%.dump}.restore.log"
if pg_restore --clean --if-exists --no-owner --verbose \
    --dbname="$SUPABASE_DATABASE_URL" "$DUMP_FILE" >"$RESTORE_LOG" 2>&1; then
  grep -v -i "password" "$RESTORE_LOG" || true
else
  grep -v -i "password" "$RESTORE_LOG" || true
  echo "ERROR: pg_restore failed (see $RESTORE_LOG). Do NOT cut over." >&2
  exit 1
fi

echo "OK: restore finished. Now compare row counts:"
echo "  BASELINE_CSV=<render baseline csv> DATABASE_URL='\$SUPABASE...' OUT_CSV=<target csv> sh migration/04_compare_row_counts.sh"
