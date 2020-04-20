# Bronchoscopy

[!["Language"](https://img.shields.io/github/languages/top/saeeddiscovery/bronchoscopy.svg?style=for-the-badge&logo=python)](http://python.org/)
![dependencies](https://img.shields.io/badge/dependencies-PyQt5-brightgreen.svg?style=for-the-badge)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://lbesson.mit-license.org/)

[![Company](https://img.shields.io/badge/Company-Parsiss-blue.svg?style=for-the-badge&logo=c)](http://parsiss.com/)
[![Company](https://img.shields.io/badge/Company-AitinTech-blue.svg?style=for-the-badge&logo=c)](http://AitinTech.ir/)

[!["Contributors"](https://img.shields.io/github/contributors/saeeddiscovery/bronchoscopy.svg?style=social&logo=visual%20studio%20code)](https://github.com/saeeddiscovery/bronchoscopy/graphs/contributors)

### PyQt5 + VTK in Python code for Navigation in Bronchoscopy

-----------

## Instructions (Windows)

### Open command window (cmd), go to the directory that contains the code and do the following:**

1. Create a virtual env and activate it (venv or conda) 
    - conda
    ```bash
    > conda create -n bronchovision python=3.6
    > conda activate bronchovision
    ```
    - venv (Python 3.6)
    ```bash
    > python -m venv bronchovision
    > bronchovision\Scripts\activate
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
1. Activate the `bronchovision` environment or create a new one.
2. Install packages from `requirements_installer.txt`.
3. Run `Make_exe.bat` and wait for it to finish.
4. Find the created file[s] in `dist\BronchoVision`

