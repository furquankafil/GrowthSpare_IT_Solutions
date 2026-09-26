@echo off
rem 02_record_row_counts.cmd — per-table row-count baseline from ANY database URL.
rem Windows CMD equivalent of 02_record_row_counts.sh.
rem
rem STRICTLY READ-ONLY: issues only SELECT count(*) queries. Safe to run against
rem the live Render database, a local test restore, or Supabase.
rem
rem Required env (current CMD session only):
rem   set DATABASE_URL=postgres://...
rem   set OUT_CSV=migration\backups\row_counts_render_2026-01-01.csv
rem Usage:
rem   migration\02_record_row_counts.cmd
rem
rem Same URL quoting rules as 01_pg_dump_render.cmd (percent must be %%25-encoded).
rem Required tools on PATH: psql.
setlocal

if "%DATABASE_URL%"=="" (echo ERROR: DATABASE_URL is not set. Aborting. 1>&2 & exit /b 2)
if "%OUT_CSV%"=="" (echo ERROR: OUT_CSV is not set. Aborting. 1>&2 & exit /b 2)
where psql >nul 2>&1
if errorlevel 1 (echo ERROR: psql not found on PATH. 1>&2 & exit /b 2)
if "%TABLES_FILE%"=="" set TABLES_FILE=migration\tables.txt
if not exist "%TABLES_FILE%" (echo ERROR: table list not found: %TABLES_FILE%. 1>&2 & exit /b 2)

rem Connectivity pre-check: abort here (not mid-run) if the URL is unreachable.
psql "%DATABASE_URL%" -tAX -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (echo ERROR: cannot connect with DATABASE_URL. Aborting before measuring anything. 1>&2 & exit /b 2)

for /F "delims=" %%D in ('powershell -NoProfile -Command "(Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')" 2^>nul') do set RECORDED_AT=%%D
if "%RECORDED_AT%"=="" set RECORDED_AT=unknown-time
set TMP_OUT=%OUT_CSV%.tmp
> "%TMP_OUT%" echo table,count,recorded_at
for /F "usebackq eol=# tokens=* delims=" %%T in ("%TABLES_FILE%") do call :record "%%T"
if errorlevel 1 exit /b 1
move /Y "%TMP_OUT%" "%OUT_CSV%" >nul
if errorlevel 1 (echo ERROR: could not write %OUT_CSV%. 1>&2 & exit /b 1)
echo OK: baseline written: %OUT_CSV%
exit /b 0

:record
set TBL=%~1
if "%TBL%"=="" exit /b 0
set EXISTS=
for /F "delims=" %%E in ('psql "%DATABASE_URL%" -tAX -c "SELECT to_regclass('public.%TBL%') IS NOT NULL;" 2^>nul') do set EXISTS=%%E
if not "%EXISTS%"=="t" (echo    MISSING: %TBL% 1>&2 & >> "%TMP_OUT%" echo %TBL%,MISSING,%RECORDED_AT% & exit /b 0)
set COUNT=
for /F "delims=" %%C in ('psql "%DATABASE_URL%" -tAX -c "SELECT count(*) FROM public.%TBL%;" 2^>nul') do set COUNT=%%C
if "%COUNT%"=="" (echo ERROR: count query failed for %TBL%. Aborting. 1>&2 & exit /b 1)
>> "%TMP_OUT%" echo %TBL%,%COUNT%,%RECORDED_AT%
echo    %TBL% = %COUNT% 1>&2
exit /b 0
