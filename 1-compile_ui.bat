@ECHO OFF
ECHO.
ECHO Compiling Ui files...
ECHO ============================
ECHO.
CALL .venv\Scripts\activate
CALL pyuic5 -x ui/MainWindow.ui -o MainWindow.py
CALL pyuic5 -x ui/Layout_1.ui -o Layout_1.py
ECHO -----* Ui Compiled
CALL pyrcc5 ui/resources.qrc -o resources_rc.py
ECHO -----* Resources Compiled
ECHO.
PAUSE