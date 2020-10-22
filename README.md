# Bronchoscopy

[![Parsiss](https://img.shields.io/badge/Company-Parsiss-blue.svg?style=for-the-badge&logo=c)](http://parsiss.com/)
[![AitinTech](https://img.shields.io/badge/Company-AitinTech-blue.svg?style=for-the-badge&logo=c)](http://AitinTech.ir/)

### PyQt5 + VTK/VMTK in Python for Navigation in Bronchoscopy

-----------

## Instructions (Windows)

1. **Install [Anaconda](https://anaconda.org/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)**

2. **Create environment and install requirements:**
    ```
    > conda create --name bv python=3.6
    > conda activate bv
    > conda install --force-reinstall -c vmtk vmtk
    > conda install scipy pyqt matplotlib
    > pip install scikit-surgerynditracker pypiwin32 pycpd
    ```
    > NOTE: You can change the name (bv) to whatever you want, but you should do the the same change in the compile_ui.bat and run.bat files
3. **Optional: Compile ui files (only if you've changed the ui files)**
    ```
    > compile_ui.bat
    ```

4. **Run the application**
    ```
    > run.bat
    ```
--------------


