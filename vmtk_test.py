from vmtk import pypes, vmtkscripts
fileName = 'D:\\Parsiss\\Bronchoscopy_project\\BronchoVision_others\\data\\Images\\ph3_2.mhd'
myArguments = f'vmtkimagereader -ifile {fileName} --pipe vmtkmarchingcubes -l 0.5 --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25 --pipe vmtksurfaceclipper'
# myArguments = f'vmtkimagereader -ifile {fileName} --pipe vmtkmarchingcubes -l 0.5 --pipe vmtksurfaceclipper'
myPype = pypes.PypeRun(myArguments)

tmpImage = myPype.GetScriptObject('vmtkimagereader','0').Image
myWriter = vmtkscripts.vmtkImageWriter()
myWriter.Image = tmpImage
myWriter.OutputFileName = 'c:\\dd.nii.gz'
myWriter.Execute()

# TODO: check orientation of the saved image

# vmtkimagereader -ifile {fileName} --pipe vmtkimagevoiselector -ofile image_volume_voi.vti