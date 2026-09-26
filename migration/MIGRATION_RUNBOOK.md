# Migration Runbook — Render PostgreSQL → Supabase PostgreSQL

For the GrowthSpare IT Solutions Django application (`Django 6.0.6`, `psycopg2-binary`,
single `default` database via `DATABASE_URL`, DB-backed sessions, no PG-specific features).

> **Rules:** never write to the Render database from these steps (all reads are `SELECT`
> or `pg_dump`). Connection strings live **only in environment variables on the operator
> machine** — never in git, chat logs, or script files. `*.dump`, `*.sql` and
> `migration/backups/` are git-ignored. Do not run any step marked MANUAL out of order.

Prerequisites on the operator machine: `pg_dump`, `pg_restore`, `psql` (PostgreSQL 15+
client tools), Python + this repo (for the Django staging test), network access to both
databases. Scripts are POSIX `sh` (run under Git Bash/WSL/macOS/Linux).

---

## A. How to obtain the Render external PostgreSQL connection string (MANUAL)

1. Open the Render dashboard → **growthspare-db** (PostgreSQL) → **Connect**.
2. Copy the **External Connection String** (`postgres://growthspare_user:…@dpg-…/growthspare_db`).
3. On the operator machine only, export it for the current shell (do not save it in a file):
   `export RENDER_DATABASE_URL='postgres://paste-here'`
4. Record the server version for the checklist: `psql "$RENDER_DATABASE_URL" -tAc 'SELECT version();'`

## B. How to create a verified pg_dump (scripted, read-only on source)

```sh
export RENDER_DATABASE_URL='postgres://paste-here'
sh migration/01_pg_dump_render.sh
```

What it does: `pg_dump --format=custom --compress=9` into
`migration/backups/growthspare_render_<date>.dump` (refuses to overwrite without
`OVERWRITE=1`), then verifies the dump's table of contents (`pg_restore --list`) and
aborts unless ≥20 `TABLE DATA` sections are present. `pg_dump` never modifies the source.

## C. How to verify the dump

1. Automatic: step B already asserts a readable TOC with all tables.
2. Manual spot-check: `pg_restore --list migration/backups/<file>.dump | grep "TABLE DATA" | wc -l`
   (expect ~27: 21 app tables + M2M + contrib + sessions).
3. Strong verification: restore into an empty **local** database and run the Django
   staging test from §H against it before ever touching Supabase.

## D. How to record source row counts (scripted, SELECT-only)

```sh
export RENDER_DATABASE_URL='postgres://paste-here'
RENDER_DATABASE_URL="$RENDER_DATABASE_URL" \
DATABASE_URL="$RENDER_DATABASE_URL" \
OUT_CSV=migration/backups/row_counts_render_$(date +%F).csv \
sh migration/02_record_row_counts.sh
```

Covers every table in `migration/tables.txt` (all 10 apps + M2M + sessions/migrations/admin).
Missing tables are recorded as `MISSING`, never fatal. Keep this CSV — it is the
baseline everything else is compared against. Also record `SELECT version();` output.

## E. How to obtain the Supabase PostgreSQL connection string (MANUAL)

1. Supabase dashboard → new project (region closest to Render region + users) → wait for green.
2. Project Settings → Database → **Connection string → URI**, **direct connection**
   (`db.<ref>.supabase.co:5432`, NOT the 6543 pooler for the first migration).
3. Append the SSL parameter Django needs: `?sslmode=require`
   (full form: `postgres://postgres:<password>@db.<ref>.supabase.co:5432/postgres?sslmode=require`).
   No code change is required — `dj-database-url` maps this into the connection.
4. Export operator-side only: `export SUPABASE_DATABASE_URL='postgres://paste-here?sslmode=require'`

## F. How to restore to Supabase (scripted, guarded)

```sh
export SUPABASE_DATABASE_URL='postgres://paste-here?sslmode=require'
SUPABASE_DATABASE_URL="$SUPABASE_DATABASE_URL" \
DUMP_FILE=migration/backups/growthspare_render_<date>.dump \
SUPABASE_RESTORE_ACK=I-UNDERSTAND-THIS-OVERWRITES-SUPABASE \
sh migration/03_restore_supabase.sh
```

Locks: refuses without the ACK string, without an existing dump file, and if the target
URL looks like Render/localhost/sqlite instead of Supabase. Uses
`pg_restore --clean --if-exists --no-owner` **without** `--create` (refreshes objects
inside the existing Supabase DB; never drops the database itself).

## G. How to compare row counts (scripted, read-only)

```sh
BASELINE_CSV=migration/backups/row_counts_render_<date>.csv \
DATABASE_URL="$SUPABASE_DATABASE_URL" \
OUT_CSV=migration/backups/row_counts_supabase_<date>.csv \
sh migration/04_compare_row_counts.sh
```

Exits `0`/prints `RESULT: PASS` only on a full per-table match; any `MISMATCH` line is a
hard stop — **do not cut over**. Also compare `SELECT version();` on both servers.

## H. How to test Django against Supabase (staging, writes only test rows)

```sh
DATABASE_URL="$SUPABASE_DATABASE_URL" DJANGO_SETTINGS_MODULE=config.settings.development \
python manage.py check
DATABASE_URL="$SUPABASE_DATABASE_URL" DJANGO_SETTINGS_MODULE=config.settings.development \
python manage.py showmigrations   # every entry must show [X]; migrate would be a no-op
```

Then run the dev server pointed at Supabase and verify: `/admin/` login with the existing
superuser, homepage + 4 local landing pages + 6 articles render, `/sitemap.xml` complete,
one test contact submission appears in the Supabase table editor (delete it afterwards).
Expected Django behavior notes: `CONN_MAX_AGE=600` persistent connections are fine on the
direct 5432 endpoint (≤16 app connections: 4 gunicorn workers × 4 threads).

## I. How to perform the Render DATABASE_URL cutover (MANUAL, dashboard)

1. Preconditions: backup verified (§B–C), counts match (§G), staging test green (§H).
2. Render dashboard → **growthspare-web** → Environment: **rename** the current
   `DATABASE_URL` to `DATABASE_URL_RENDER_backup` (do NOT delete it), then set the new
   `DATABASE_URL` to the Supabase URI **with `?sslmode=require`**.
3. **Manual Deploy** (or restart) so the container boots against Supabase.
   Boot runs `migrate` (no-op — `django_migrations` was restored), idempotent seeds,
   `collectstatic`, gunicorn. Watch logs for clean startup.
4. Production smoke test in order: `/ping`, `/`, 4 landing pages, 6 articles,
   `/sitemap.xml`, `/robots.txt`, admin login, one real test lead + booking (verify in
   Supabase, then process/delete them).
5. Media caveat: files under `/app/mediafiles` are NOT in Postgres and Render has no
   Disk declared in code — confirm the fate of uploads separately (see audit report §F).
6. Keep the Render database untouched for **≥14 days**.

## J. How to rollback (MANUAL, minutes)

1. In Render dashboard → growthspare-web → Environment: set `DATABASE_URL` back to the
   value saved as `DATABASE_URL_RENDER_backup`. Restart/redeploy.
2. Production immediately reads the untouched Render database again.
3. Reconcile the gap: any leads/bookings/comments created on Supabase after cutover must
   be exported first, e.g.
   `psql "$SUPABASE_DATABASE_URL" -c "COPY (SELECT * FROM contact_contactmessage WHERE created_at > '<cutover-UTC>') TO STDOUT CSV HEADER" > gap_leads.csv`
   (repeat per table in `migration/tables.txt` with `created_at`), then re-enter or import
   them. Decide rollback within hours to keep this window trivial.
4. Only delete the Render database after the 14-day retention AND a final verified backup.
