@ECHO OFF
ECHO.
ECHO Starting PyInstaller ...
ECHO ========================
ECHO.
CALL conda activate bronchovision
CALL PyInstaller BronchoVision.spec
PAUSE