@ECHO OFF
ECHO.
ECHO Compiling Ui files...
ECHO ============================
ECHO.
CALL .venv\Scripts\activate
CALL pyuic5 -x ui/MainWindow.ui -o ui/MainWindow.py
ECHO -----* Ui Compiled
CALL pyrcc5 ui/resources.qrc -o resources_rc.py
ECHO -----* Resources Compiled
ECHO.
PAUSE