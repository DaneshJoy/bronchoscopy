from viewers.QVtkViewer import QVTKViewer
import vtk

class QVtkViewer2D(QVTKViewer):
    def __init__(self, panel, size, viewType):
        super().__init__(panel, size, viewType)
        self.reslice = vtk.vtkImageReslice()
    
    def show_image(self, reader, dims, spacing, origin):
        # image = reader.GetOutput()
        # self.dims = image.GetDimensions()

        # Camera
        cam = vtk.vtkCamera()

        # Create a greyscale lookup table
        grLut = vtk.vtkLookupTable()
        # grLut.SetTableRange(0, 1000)  # image intensity range
        grLut.SetTableRange(-1300, 100)  # image intensity range
        grLut.SetValueRange(0, 1)  # from black to white
        grLut.SetSaturationRange(0, 0)  # no color saturation
        grLut.SetRampToLinear()
        grLut.SetHueRange(0, 0)
        grLut.Build()

        # Calculate the center of the volume
        self.spacing = spacing
        self.origin = origin
        # self.spacing = reader.GetOutput().GetSpacing()
        # self.origin = reader.GetOutput().GetOrigin()
        center = [self.origin[0] + self.spacing[0] * 0.5 * dims[0],
                self.origin[1] + self.spacing[1] * 0.5 * dims[1],
                self.origin[2] + self.spacing[2] * 0.5 * dims[2]]

        # Matrices for axial, coronal, sagittal view orientations
        axial = vtk.vtkMatrix4x4()
        axial.DeepCopy((1, 0, 0, center[0],
                        0, 1, 0, center[1],
                        0, 0, 1, center[2],
                        0, 0, 0, 1))

        coronal = vtk.vtkMatrix4x4()
        coronal.DeepCopy((1, 0, 0, center[0],
                        0, 0, -1, center[1],
                        0, 1, 0, center[2],
                        0, 0, 0, 1))

        sagittal = vtk.vtkMatrix4x4()
        sagittal.DeepCopy((0, 0, -1, center[0],
                        1, 0, 0, center[1],
                        0, 1, 0, center[2],
                        0, 0, 0, 1))

        self.reslice.SetInputConnection(reader.GetOutputPort())
        self.reslice.SetOutputDimensionality(2)
        if self.viewType == "Axial":
            self.reslice.SetResliceAxes(axial)
            # cam.SetViewUp(0, -1, 0)
        elif self.viewType == "Coronal":
            self.reslice.SetResliceAxes(coronal)
        else:  # self.viewType == "Sagittal"
            self.reslice.SetResliceAxes(sagittal)
        self.reslice.SetInterpolationModeToCubic()

        # Map the image through the lookup table
        colors = vtk.vtkImageMapToColors()
        colors.SetInputConnection(self.reslice.GetOutputPort())
        colors.SetLookupTable(grLut)
        colors.Update()

        self.actor.GetMapper().SetInputConnection(colors.GetOutputPort())
        self.ren.AddActor2D(self.actor)

        cam.ComputeViewPlaneNormal()
        # cam.SetViewUp(0, -1, 0)
        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
        cam.Zoom(2)
        self.ren.ResetCameraClippingRange()
        self.interactor.Initialize()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())

    def set_slice(self, sliceNumber):
        self.reslice.Update()
        matrix = self.reslice.GetResliceAxes()
        # move the center point that we are slicing through
        if self.viewType == "Axial":
            sliceNumber = self.origin[2] + sliceNumber*self.spacing[2]
            matrix.SetElement(2, 3, sliceNumber)
        elif self.viewType == "Coronal":
            sliceNumber = self.origin[1] + sliceNumber*self.spacing[1]
            matrix.SetElement(1, 3, sliceNumber)
        else:  # self.viewType == "Sagittal"
            sliceNumber = self.origin[0] + sliceNumber*self.spacing[0]
            matrix.SetElement(0, 3, sliceNumber)
        self.ren.GetRenderWindow().Render()