@ECHO OFF
ECHO.
ECHO Compiling Ui files...
ECHO ============================
ECHO.
CALL conda activate bronchovision
CALL pyuic5 -x ui/MainWindow.ui -o ui/MainWindow.py
CALL pyuic5 -x ui/ToolsWindow.ui -o ui/ToolsWindow.py
CALL pyuic5 -x ui/RegMatWindow.ui -o ui/RegMatWindow.py
ECHO -----* Ui Compiled
CALL pyrcc5 ui/resources.qrc -o resources_rc.py
ECHO -----* Resources Compiled
ECHO.
PAUSE