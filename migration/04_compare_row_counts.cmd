@echo off
rem 04_compare_row_counts.cmd — verify Supabase matches the Render baseline.
rem Windows CMD equivalent of 04_compare_row_counts.sh.
rem
rem READ-ONLY against both sides (re-records the target with SELECT count(*)
rem and diffs against the baseline CSV). Exits 0 only on a full match.
rem
rem Required env (current CMD session only):
rem   set BASELINE_CSV=migration\backups\row_counts_render_<date>.csv
rem   set DATABASE_URL=postgres://...  (RESTORED Supabase database)
rem   set OUT_CSV=migration\backups\row_counts_supabase_<date>.csv
rem Usage:
rem   migration\04_compare_row_counts.cmd
setlocal

if "%BASELINE_CSV%"=="" (echo ERROR: BASELINE_CSV is not set. Aborting. 1>&2 & exit /b 2)
if not exist "%BASELINE_CSV%" (echo ERROR: BASELINE_CSV not found: %BASELINE_CSV%. Aborting. 1>&2 & exit /b 2)
if "%DATABASE_URL%"=="" (echo ERROR: DATABASE_URL (restore target) is not set. Aborting. 1>&2 & exit /b 2)
if "%OUT_CSV%"=="" (echo ERROR: OUT_CSV is not set. Aborting. 1>&2 & exit /b 2)

call "%~dp002_record_row_counts.cmd"
if errorlevel 1 (echo ERROR: target recount failed. Aborting. 1>&2 & exit /b 1)

echo -^> Comparing baseline vs restored...
set MISMATCH=0
for /F "usebackq eol=# tokens=1,2 delims=," %%A in ("%BASELINE_CSV%") do call :cmp "%%A" "%%B"
if not "%MISMATCH%"=="0" (echo RESULT: FAIL - counts differ. Do NOT cut over. 1>&2 & exit /b 1)
echo RESULT: PASS - all table counts match.
exit /b 0

:cmp
if "%~1"=="table" exit /b 0
if "%~1"=="" exit /b 0
set TARGET=
for /F "tokens=2 delims=," %%T in ('findstr /B /C:"%~1," "%OUT_CSV%" 2^>nul') do set TARGET=%%T
if not "%TARGET%"=="%~2" (echo MISMATCH: %~1 baseline=%~2 restored=%TARGET% 1>&2 & set MISMATCH=1 & exit /b 0)
exit /b 0
