import vtk
from PyQt5.QtWidgets import QFrame
from PyQt5 import QtWidgets, QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class QVtkViewer3D(QFrame):
    def __init__(self, parent, size):
        super().__init__(parent)

        colors = vtk.vtkNamedColors()
        colors.SetColor("SkinColor", [255, 125, 64, 255])
        colors.SetColor("BkgColor", [51, 77, 102, 255])

        # Make the actual QtWidget a child so that it can be reparented
        self.interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.interactor)
        self.layout.setContentsMargins(5, 5, 5, 5)
        width = (size.width()-370) // 2
        height = (size.height()-170) // 2
        self.interactor.setMinimumSize(width, height)
        self.setLayout(self.layout)

        # Setup VTK Environment
        self.ren = vtk.vtkRenderer()
        ren_win = self.interactor.GetRenderWindow()
        ren_win.AddRenderer(self.ren)

        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.ren.SetBackground(0, 0, 0)
        # ren.SetBackground(colors.GetColor3D("BkgColor"))
        self.interactor.Initialize()

    def showImage(self, reader):
        # Isosurface
        skinExtractor = vtk.vtkMarchingCubes()
        skinExtractor.SetInputConnection(reader.GetOutputPort())
        skinExtractor.SetValue(0, 300)

        # Mapper
        skinMapper = vtk.vtkPolyDataMapper()
        skinMapper.SetInputConnection(skinExtractor.GetOutputPort())
        skinMapper.ScalarVisibilityOff()
        # skinMapper.UseLookupTableScalarRangeOn()

        # Actor
        skin = vtk.vtkActor()
        skin.SetMapper(skinMapper)
        skin.GetProperty().SetDiffuseColor(0.8, 0.6, 0.2)
        # skin.GetProperty().SetDiffuseColor(colors.GetColor3D("SkinColor"))

        # Camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0, 0, -1)
        cam.SetPosition(0, -1, 0)
        cam.SetFocalPoint(0, 0, 0)
        cam.ComputeViewPlaneNormal()
        cam.Azimuth(30.0)
        cam.Elevation(30.0)

        self.ren.AddActor(skin)
        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
        cam.Dolly(1.5)  # Moves the camera towards the FocalPoint
        self.ren.ResetCameraClippingRange()

        # self.renderer = ren
        # self.interactor = interactor
        self.interactor.Initialize()
        self.interactor.Start()


class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("MiddleButtonPressEvent", self.middle_button_press_event)
        self.AddObserver("MiddleButtonReleaseEvent", self.middle_button_release_event)

    def middle_button_press_event(self, obj, event):
        print("Middle Button pressed")
        self.OnMiddleButtonDown()
        return

    def middle_button_release_event(self, obj, event):
        print("Middle Button released")
        self.OnMiddleButtonUp()
        return


class QVtkViewer2D(QFrame):
    def __init__(self, parent, size, planeType):
        super().__init__(parent)

        # Make the actual QtWidget a child so that it can be reparented
        self.interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.interactor)
        self.layout.setContentsMargins(5, 5, 5, 5)
        width = (size.width()-370) // 2
        height = (size.height()-170) // 2
        self.interactor.setMinimumSize(width, height)
        self.setLayout(self.layout)

        # Setup VTK Environment
        self.ren = vtk.vtkRenderer()
        ren_win = self.interactor.GetRenderWindow()
        ren_win.AddRenderer(self.ren)
        # self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera)
        # self.interactor.SetInteractorStyle(MyInteractorStyle())
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())
        self.ren.SetBackground(0, 0, 0)
        # ren.SetBackground(colors.GetColor3D("BkgColor"))
        self.interactor.Initialize()

        self.plane = vtk.vtkImageActor()
        self.planeType = planeType

    def DummyFunc1(self, obj, ev):
        print("Before Event")

    def DummyFunc2(self, obj, ev):
        print("After Event")

    def showImage(self, reader):
        # black/white lookup table
        bwLut = vtk.vtkLookupTable()
        bwLut.SetTableRange(0, 2000)
        bwLut.SetSaturationRange(0, 0)
        bwLut.SetHueRange(0, 0)
        bwLut.SetValueRange(0, 1)
        bwLut.Build()

        # plane
        planeColors = vtk.vtkImageMapToColors()
        planeColors.SetInputConnection(reader.GetOutputPort())
        planeColors.SetLookupTable(bwLut)
        planeColors.Update()

        
        self.plane.GetMapper().SetInputConnection(planeColors.GetOutputPort())

        # Camera
        cam = vtk.vtkCamera()
        # cam.SetViewUp(0, 0, -1)
        cam.SetFocalPoint(0, 0, 0)
        cam.ComputeViewPlaneNormal()
        # cam.Azimuth(30.0)
        # cam.Elevation(30.0)

        if self.planeType == "axial":
            self.plane.SetDisplayExtent(0, 255, 0, 255, 46, 46)
            # cam.SetPosition(0, 0, -1)
            cam.Roll(180)

        elif self.planeType == "coronal":
            self.plane.SetDisplayExtent(0, 255, 128, 128, 0, 92)
            # cam.SetPosition(0, -1, 0)
            cam.Elevation(90)
            cam.OrthogonalizeViewUp()
        else:  # self.planeType == "sagittal"
            self.plane.SetDisplayExtent(128, 128, 0, 255, 0, 92)
            # cam.SetPosition(-1, 0, 0)
            cam.Azimuth(90)
            cam.Roll(90)
            cam.OrthogonalizeViewUp()

        self.ren.AddActor(self.plane)
        # ren_win.Render()
        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
        cam.Dolly(1.5)  # Moves the camera towards the FocalPoint
        self.ren.ResetCameraClippingRange()

        # self.renderer = ren
        # self.interactor = interactor

        # self.interactor.RemoveObservers('LeftButtonPressEvent')
        # self.interactor.AddObserver('LeftButtonPressEvent', self.DummyFunc1, 1.0)
        # self.interactor.AddObserver('LeftButtonPressEvent', self.DummyFunc2, -1.0)

        self.interactor.Initialize()
        self.interactor.Start()

    def setSlice(sliceNumber):
        if self.planeType == "axial":
            self.plane.SetDisplayExtent(0, 255, 0, 255, sliceNumber, sliceNumber)
            # # cam.SetPosition(0, 0, -1)
            # cam.Roll(180)

        elif self.planeType == "coronal":
            self.plane.SetDisplayExtent(0, 255, sliceNumber, sliceNumber, 0, 92)
            # # cam.SetPosition(0, -1, 0)
            # cam.Elevation(90)
            # cam.OrthogonalizeViewUp()
        else:  # self.planeType == "sagittal"
            self.plane.SetDisplayExtent(sliceNumber, sliceNumber, 0, 255, 0, 92)
            # # cam.SetPosition(-1, 0, 0)
            # cam.Azimuth(90)
            # cam.Roll(90)
            # cam.OrthogonalizeViewUp()
