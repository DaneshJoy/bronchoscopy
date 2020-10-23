@ECHO OFF
ECHO.
ECHO Compiling Ui files...
ECHO ============================
ECHO.
CALL conda activate bv
CALL pyuic5 -x MainWin.ui -o MainWin.py
CALL pyuic5 -x ToolsWin.ui -o ToolsWin.py
CALL pyuic5 -x RegMatWin.ui -o RegMatWin.py
CALL pyuic5 -x NewPatientWin.ui -o NewPatientWin.py
ECHO -----* Ui Compiled
CALL pyrcc5 resources.qrc -o ../resources_rc.py
ECHO -----* Resources Compiled
ECHO.
PAUSE