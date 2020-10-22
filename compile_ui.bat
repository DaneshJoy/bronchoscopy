@ECHO OFF
ECHO.
ECHO Compiling Ui files...
ECHO ============================
ECHO.
CALL conda activate bv
CALL pyuic5 -x src/ui/MainWin.ui -o src/ui/MainWin.py
CALL pyuic5 -x src/ui/ToolsWin.ui -o src/ui/ToolsWin.py
CALL pyuic5 -x src/ui/RegMatWin.ui -o src/ui/RegMatWin.py
CALL pyuic5 -x src/ui/NewPatientWin.ui -o src/ui/NewPatientWin.py
ECHO -----* Ui Compiled
CALL pyrcc5 src/ui/resources.qrc -o src/resources_rc.py
ECHO -----* Resources Compiled
ECHO.
PAUSE