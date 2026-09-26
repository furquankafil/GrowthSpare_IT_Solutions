@echo off
rem 03_restore_supabase.cmd — restore a verified dump into Supabase PostgreSQL.
rem Windows CMD equivalent of 03_restore_supabase.sh.
rem
rem SAFETY LOCKS (all must pass or the script aborts before touching anything):
rem   1. SUPABASE_DATABASE_URL must be set (direct port 5432 URI from the
rem      Supabase dashboard - Project Settings - Database - Connection string,
rem      with ?sslmode=require appended).
rem   2. DUMP_FILE must point at an existing, verified .dump file.
rem   3. SUPABASE_RESTORE_ACK must equal exactly: I-UNDERSTAND-THIS-OVERWRITES-SUPABASE
rem   4. The target URL must NOT look like Render/localhost/sqlite, and MUST
rem      look like a Supabase host (refuses otherwise).
rem
rem Restore uses --clean --if-exists --no-owner WITHOUT --create, so it refreshes
rem objects inside the existing Supabase database but never drops the database
rem itself or other databases on the server.
rem
rem Set vars in the current CMD session only, then run:
rem   set SUPABASE_DATABASE_URL=postgres://...
rem   set DUMP_FILE=migration\backups\growthspare_render_<stamp>.dump
rem   set SUPABASE_RESTORE_ACK=I-UNDERSTAND-THIS-OVERWRITES-SUPABASE
rem   migration\03_restore_supabase.cmd
rem
rem Same URL quoting rules as 01_pg_dump_render.cmd (percent must be %%25-encoded).
rem Required tools on PATH: pg_restore.
setlocal

if "%SUPABASE_DATABASE_URL%"=="" (echo ERROR: SUPABASE_DATABASE_URL is not set. Aborting ^(nothing was touched^). 1>&2 & exit /b 2)
if "%DUMP_FILE%"=="" (echo ERROR: DUMP_FILE is not set. Aborting. 1>&2 & exit /b 2)
if not exist "%DUMP_FILE%" (echo ERROR: DUMP_FILE not found: %DUMP_FILE%. Aborting. 1>&2 & exit /b 2)
if not "%SUPABASE_RESTORE_ACK%"=="I-UNDERSTAND-THIS-OVERWRITES-SUPABASE" (echo ERROR: explicit acknowledgement missing. Set SUPABASE_RESTORE_ACK=I-UNDERSTAND-THIS-OVERWRITES-SUPABASE to proceed. 1>&2 & exit /b 2)
where pg_restore >nul 2>&1
if errorlevel 1 (echo ERROR: pg_restore not found on PATH. 1>&2 & exit /b 2)

rem Refuse targets that look like production Render, local dev, or sqlite.
echo "%SUPABASE_DATABASE_URL%" | findstr /I "render\.com dpg- localhost 127\.0\.0\.1 sqlite" >nul
if not errorlevel 1 (echo ERROR: target URL looks like Render/localhost/sqlite, NOT Supabase. Refusing. 1>&2 & exit /b 2)
rem Require a Supabase-looking host.
echo "%SUPABASE_DATABASE_URL%" | findstr /I "supabase\.co supabase\.com" >nul
if errorlevel 1 (echo ERROR: target URL does not look like a Supabase host. Refusing. 1>&2 & exit /b 2)

echo -^> Restoring %DUMP_FILE% into Supabase (clean + no-owner, database itself preserved)...
set RESTORE_LOG=%DUMP_FILE%.restore.log
pg_restore --clean --if-exists --no-owner --verbose --dbname="%SUPABASE_DATABASE_URL%" "%DUMP_FILE%" >"%RESTORE_LOG%" 2>&1
if errorlevel 1 goto :restorefailed
type "%RESTORE_LOG%" | findstr /V /I password
goto :done

:restorefailed
type "%RESTORE_LOG%" | findstr /V /I password
echo ERROR: pg_restore failed (see %RESTORE_LOG%). Do NOT cut over. 1>&2
exit /b 1

:done
echo OK: restore finished. Compare row counts with 04_compare_row_counts.cmd
exit /b 0
