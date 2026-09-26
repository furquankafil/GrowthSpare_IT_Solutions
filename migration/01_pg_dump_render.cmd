@echo off
rem 01_pg_dump_render.cmd — verified backup of the LIVE Render PostgreSQL database.
rem Windows CMD equivalent of 01_pg_dump_render.sh (Bash/WSL unavailable on this machine).
rem
rem READ-ONLY against production (pg_dump never writes to the source database).
rem Writes ONLY to migration\backups\ (git-ignored).
rem
rem Required env (current CMD session only — never commit, never echo):
rem   set RENDER_DATABASE_URL=postgres://...
rem Usage:
rem   migration\01_pg_dump_render.cmd
rem
rem Quoting rules for the URL: wrap in double quotes when setting it. A literal
rem percent sign in a password must be URL-encoded as %%25 (standard URI rule).
rem Delayed expansion is deliberately OFF so ! & | characters stay literal.
rem
rem Required tools on PATH: pg_dump, pg_restore.
setlocal

if "%RENDER_DATABASE_URL%"=="" (echo ERROR: RENDER_DATABASE_URL is not set. Aborting ^(nothing was touched^). 1>&2 & exit /b 2)
where pg_dump >nul 2>&1
if errorlevel 1 (echo ERROR: pg_dump not found on PATH. 1>&2 & exit /b 2)
where pg_restore >nul 2>&1
if errorlevel 1 (echo ERROR: pg_restore not found on PATH. 1>&2 & exit /b 2)

if not exist "migration\backups" mkdir "migration\backups"
for /F "delims=" %%D in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyy-MM-dd_HHmm')" 2^>nul') do set STAMP=%%D
if "%STAMP%"=="" set STAMP=manual-%RANDOM%
if "%OUT_DUMP%"=="" set OUT_DUMP=migration\backups\growthspare_render_%STAMP%.dump

if exist "%OUT_DUMP%" if not "%OVERWRITE%"=="1" (echo ERROR: %OUT_DUMP% already exists. Set OVERWRITE=1 to replace it. 1>&2 & exit /b 2)

echo -^> Dumping Render production database (custom format, compressed)...
echo    destination: %OUT_DUMP%
set DUMP_LOG=%OUT_DUMP%.log
pg_dump "%RENDER_DATABASE_URL%" --format=custom --compress=9 --verbose --file="%OUT_DUMP%" >"%DUMP_LOG%" 2>&1
if errorlevel 1 goto :dumpfailed
type "%DUMP_LOG%" | findstr /V /I password
goto :verify

:dumpfailed
type "%DUMP_LOG%" | findstr /V /I password
echo ERROR: pg_dump failed (see %DUMP_LOG%). Aborting. 1>&2
exit /b 1

:verify
echo -^> Verifying dump integrity (table of contents readable)...
set TABLES=0
for /F %%N in ('pg_restore --list "%OUT_DUMP%" 2^>nul ^| find /C "TABLE DATA"') do set TABLES=%%N
echo    TABLE DATA sections: %TABLES%
if %TABLES% LSS 20 (echo ERROR: unexpectedly few tables in dump (%TABLES%). Investigate before proceeding. 1>&2 & exit /b 1)

echo OK: backup written and verified: %OUT_DUMP%
echo NEXT: record the source baseline with 02_record_row_counts.cmd
exit /b 0
