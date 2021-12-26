# BronchoVision
### Navigation with Electromagnetic Tracker in Bronchoscopy

[![Parsiss](https://img.shields.io/badge/Copyright-Parsiss-blue.svg?style=for-the-badge&logo=c)](http://parsiss.com/)

-----------

### Application Requirements

1. **Install [Anaconda](https://anaconda.org/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)**

2. **Create an environment and install the requirements:**
   
    1. Method 1 (Automatic)
    ```
    > conda env create -f environment.yml
    ```
    
    2. Method 2 (Manual)
    ```
    > conda create --name bv python=3.6
    > conda activate bv
    > conda install -c conda-forge itk opencv
    > conda install --force-reinstall -c vmtk vmtk
    > conda install scipy=1.1 pyqt=5.9.2 matplotlib
    > pip install scikit-surgerynditracker pypiwin32 pycpd
    ```
> NOTE: You can change the name (bv) to whatever you want, but you should do the the same change in the compile_ui.bat and run.bat files

3. **Run the application**
    ```
    > src\run.bat
    ```
--------------

### Tracker Installation

1. **Install NDI_ToolBox**

2. **in Windows Device Manager:**
    1. First Driver
        - Under "Other Devices", right click "NDI Host USB Converter" or "NDI Aurora SCU"
        (which has a yellow mark on it)
        - Select "Update Driver Software..." then select "Browse my computer for driver software"
        - Select "Program Files\Northern Digital Inc\ToolBox\USB Driver". Select Next and install
    2. Second Driver
        - Under "Other Devices", right click on "USB Serial Port"
        (which has a yellow mark on it)
        - Select "Update Driver Software..." then select "Browse my computer for driver software"
        - Select "Program Files\Northern Digital Inc\ToolBox\USB Driver". Select Next and install

3. **Attach the "Reference" sensor to the 1st port and the "Tool" sensor to the 2nd port**

> Check the "NDI Track" application to test the tracker and sensors


