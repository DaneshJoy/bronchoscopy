# Bronchoscopy

[![Parsiss](https://img.shields.io/badge/Company-Parsiss-blue.svg?style=for-the-badge&logo=c)](http://parsiss.com/)
[![AitinTech](https://img.shields.io/badge/Company-AitinTech-blue.svg?style=for-the-badge&logo=c)](http://AitinTech.ir/)

### PyQt5 + VTK in Python code for Navigation in Bronchoscopy

-----------

## Instructions (Windows)

1. **Install [Anaconda](https://anaconda.org/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)**

2. **Create environment and install requirements:**
    ```
    > conda env create -f environment.yml
    > conda activate vmtk
    ```

    if it failed, try this one:
    ```
    > conda create --name vmtk --file spec-file.txt
    > conda activate vmtk
    ```

3. **Compile ui files (Optional: only if you've changed the ui files)**
    ```
    > compile_ui.bat
    ```

4. **Run application**
    ```
    > run.bat
    ```
--------------


