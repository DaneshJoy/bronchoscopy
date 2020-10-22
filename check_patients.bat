@ECHO OFF
ECHO.
ECHO Patients:
ECHO.
sqlite3 Patients\\patients.db ".header on" ".mode column" "select* from patients;"
ECHO.
PAUSE