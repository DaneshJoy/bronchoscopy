# Bronchoscopy

[!["Language"](https://img.shields.io/github/languages/top/saeeddiscovery/bronchoscopy.svg)](http://python.org/)
![dependencies](https://img.shields.io/badge/dependencies-PyQt5-orange)

[![Generic badge](https://img.shields.io/badge/Company-Parsiss-blue.svg)](http://parsiss.com/)
[![Generic badge](https://img.shields.io/badge/Company-AitinTech-blue.svg)](http://AitinTech.ir/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

PyQT + VTK in Python code for Navigation in Bronchoscopy

## Instructions (Windows)

### Open command window (cmd), go to the directory that contains the code and do the following:**

1. Create a virtual env and activate it (venv or conda)
    - venv
    ```bash
    > python venv bronchovision
    > bronchovision\Scripts\activate
    ```
    - conda
    ```bash
    > conda create -n bronchovision python=3.6
    > conda activate bronchovision
    ```

2. Install packages
    ```bash
    > pip install -r requirements.txt
    ```

3. Compile ui files (only if you changed the ui)
    ```bash
    > 1-compile_ui.bat
    ```

4. Run application
    ```bash
    > 2-run.bat
    ```
--------------
### For PyInstaller (creating .exe file)
1. Activate the `bronchovision` environment.
2. Install packages from `requirements_installer.txt`.
3. Run `Make_exe.bat` and wait for it to finish.
4. Find the created file[s] in `dist\BronchoVision`

