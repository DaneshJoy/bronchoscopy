@ECHO OFF
ECHO.
ECHO Compiling Ui files...
ECHO ============================
ECHO.
CALL conda activate bronchovision
CALL pyuic5 -x ui/MainWin.ui -o ui/MainWin.py
CALL pyuic5 -x ui/ToolsWin.ui -o ui/ToolsWin.py
CALL pyuic5 -x ui/RegMatWin.ui -o ui/RegMatWin.py
ECHO -----* Ui Compiled
CALL pyrcc5 ui/resources.qrc -o resources_rc.py
ECHO -----* Resources Compiled
ECHO.
PAUSE