# Bronchoscopy

[!["Language"](https://img.shields.io/github/languages/top/saeeddiscovery/bronchoscopy.svg)](http://python.org/)
![dependencies](https://img.shields.io/badge/dependencies-PyQt5-orange)

[![Generic badge](https://img.shields.io/badge/Company-Parsiss-blue.svg)](http://parsiss.com/)
[![Generic badge](https://img.shields.io/badge/Company-AitinTech-blue.svg)](http://AitinTech.ir/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

### PyQt5 + VTK in Python code for Navigation in Bronchoscopy

-----------

## Instructions (Windows)

### Open a command window (e.g. cmd), go to the directory that contains the code and do the following:

----------------

1. **Create a virtual env and install requirements:**
    - Using Conda (_recomended_)
      - Create env and install requirements in one command:
        ```bash
        > conda env create -f environment.yml
        ```
        **or**
      - Create environment and then install requirements:
        ```bash
        > conda create -n bronchovision python=3.6
        > conda activate bronchovision
        > conda env update --prefix bronchovision --file environment.yml  --prune

    - Using venv (with Python 3.6)
        ```bash
        > python -m venv bronchovision
        > bronchovision\Scripts\activate
        > pip install -r requirements.txt
        ```
        > If you used the venv method, make sure to change the ```conda activate bronchovision``` to ```bronchovision\Scripts\activate``` in both "compile_ui.bat" and "run.bat" files

----------------

2. **Compile ui files (only if you've changed the ui files)**
    ```bash
    > compile_ui.bat
    ```
----------------

3. **Run application**
    ```bash
    > run.bat
    ```
--------------
### For PyInstaller (creating .exe file)
1. Activate the `bronchovision` environment or create a new one.
2. Install packages from `requirements_installer.txt`.
3. Run `Make_exe.bat` and wait for it to finish.
4. Find the created file[s] in `dist\BronchoVision`

