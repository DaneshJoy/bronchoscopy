@ECHO OFF
ECHO.
ECHO Compiling Ui files...
ECHO ============================
ECHO.
CALL pyuic5 -x MainWindow.ui -o MainWindow.py
ECHO -----* Ui Compiled
CALL pyrcc5 resources.qrc -o resources_rc.py
ECHO -----* Resources Compiled
ECHO.
PAUSE