@ECHO OFF
ECHO.
sqlite3 Patients\patients.db ".header on" ".mode column" "select* from patients;"
ECHO.
PAUSE