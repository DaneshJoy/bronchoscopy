# BronchoVision
### Navigation with Electromagnetic Tracker in Bronchoscopy

[![Parsiss](https://img.shields.io/badge/Copyright-Parsiss-blue.svg?style=for-the-badge&logo=c)](http://parsiss.com/)

-----------

## Instructions (Windows)

1. **Install [Anaconda](https://anaconda.org/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)**

2. **Create an environment and install the requirements:**
    ```
    > conda create --name bv python=3.6
    > conda activate bv
    > conda install --force-reinstall -c vmtk vmtk
    > conda install scipy=1.1 pyqt=5.9.2 matplotlib
    > pip install scikit-surgerynditracker pypiwin32 pycpd
    ```
    > NOTE: You can change the name (bv) to whatever you want, but you should do the the same change in the compile_ui.bat and run.bat files

3. **Run the application**
    ```
    > run.bat
    ```
--------------


