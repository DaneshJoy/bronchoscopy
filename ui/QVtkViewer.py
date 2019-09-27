import vtk
from PyQt5.QtWidgets import QFrame
from PyQt5 import QtWidgets, QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np

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
        self.interactor.setMinimumSize(width+30, height)
        self.setLayout(self.layout)

        # Setup VTK Environment
        self.ren = vtk.vtkRenderer()
        self.ren_win = self.interactor.GetRenderWindow()
        self.ren_win.AddRenderer(self.ren)
        self.ren_win.SetSize(size.width(), size.height())

        # self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.SetInteractorStyle(self.MyInteractorStyle(self))
        self.ren.SetBackground(0, 0, 0)
        # ren.SetBackground(colors.GetColor3D("BkgColor"))
        self.interactor.Initialize()

    def removeImage(self):
        self.ren.RemoveAllViewProps()

    def showImage(self, reader):

        # Flip the image
        # flipZFilter = vtk.vtkImageFlip()
        # flipZFilter.SetFilteredAxis(2) # flip z axis
        # flipZFilter.SetInputConnection(reader.GetOutputPort())
        # flipZFilter.Update()

        flipXFilter = vtk.vtkImageFlip()
        flipXFilter.SetFilteredAxis(0); # flip x axis
        flipXFilter.SetInputConnection(reader.GetOutputPort())
        flipXFilter.Update()

        flipYFilter = vtk.vtkImageFlip()
        flipYFilter.SetFilteredAxis(1); # flip y axis
        flipYFilter.SetInputConnection(flipXFilter.GetOutputPort())
        flipYFilter.Update()

        # Isosurface
        skinExtractor = vtk.vtkMarchingCubes()
        skinExtractor.SetInputConnection(flipYFilter.GetOutputPort())
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
        skin.GetProperty().SetOpacity(0.5)
        # skin.GetProperty().SetDiffuseColor(1, .49, .25)
        # skin.GetProperty().SetDiffuseColor(colors.GetColor3D("SkinColor"))
        skin.GetProperty().SetSpecular(.45)
        skin.GetProperty().SetSpecularPower(20)
        skin.GetProperty().SetDiffuse(.9)

        # Camera
        self.cam = vtk.vtkCamera()
        self.cam.SetViewUp(0, 0, -1)
        self.cam.SetPosition(0, -1, 0)
        self.cam.SetFocalPoint(0, 0, 0)
        self.cam.ComputeViewPlaneNormal()
        # self.cam.Azimuth(30.0)
        # self.cam.Elevation(30.0)

        self.txt = vtk.vtkTextActor()
        self.updateTextActor()

        self.ren.AddActor(skin)
        self.ren.SetActiveCamera(self.cam)
        self.ren.ResetCamera()
        self.cam.Dolly(1.5)  # Moves the camera towards the FocalPoint
        self.ren.ResetCameraClippingRange()

        # self.renderer = ren
        # self.interactor = interactor
        self.interactor.Initialize()
        # self.interactor.Start()

    def drawPoints(self, points):
        from vtk.util.numpy_support import numpy_to_vtkIdTypeArray

        pts = vtk.vtkPoints()
        conn = vtk.vtkCellArray()
        poly = vtk.vtkPolyData()
        nPoints = points.shape[-1]

        for i in range(0,nPoints):
            pos = points[:,:,i]
            pts.InsertNextPoint(pos[0,3], pos[1,3], pos[2,3])

        cells = np.hstack((np.ones((nPoints, 1)),
                                np.arange(nPoints).reshape(-1, 1)))
        cells = np.ascontiguousarray(cells, dtype=np.int64)

        conn.SetCells(nPoints, numpy_to_vtkIdTypeArray(cells, deep=True))

        poly.SetPoints(pts)
        poly.SetVerts(conn)
    
        pmap = vtk.vtkPolyDataMapper()
        pmap.SetInputDataObject(poly)

        # actor
        actor = vtk.vtkActor()
        actor.SetMapper(pmap)
        actor.GetProperty().SetPointSize(1)
        actor.GetProperty().SetColor(0.5,1,1) # (R,G,B)

        # assign actor to the renderer
        self.ren.AddActor(actor)
        self.interactor.ReInitialize()
        self.ren.ResetCameraClippingRange()

    def drawSphere(self, pos, color=[0,1,0]):
        # create source
        sphere = vtk.vtkSphereSource()
        # source.SetCenter(pos)

        newMat = vtk.vtkMatrix4x4()
        newMat.DeepCopy(pos.ravel())

        transform = vtk.vtkTransform()
        transform.SetMatrix(newMat)
        t_sphere = vtk.vtkTransformFilter()
        t_sphere.SetTransform(transform)
        t_sphere.SetInputConnection(sphere.GetOutputPort())

        sphere.SetRadius(3)
        # sphere.SetThetaResolution(2)
        # sphere.SetPhiResolution(2)

        # mapper
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(t_sphere.GetOutput())
        else:
            mapper.SetInputConnection(t_sphere.GetOutputPort())

        # actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color) # (R,G,B)

        # assign actor to the renderer
        self.ren.AddActor(actor)
        self.interactor.ReInitialize()

    def setCamera(self, cam_pos):
        # self.ren.ResetCamera()
        cam = self.ren.GetActiveCamera()
        # cam = vtk.vtkCamera()

        pr = vtk.vtkMatrix4x4() # extrinsic Real world
        # copy from numpy to vtkMatrix4x4
        pr.DeepCopy(cam_pos.ravel()) 

        pv = vtk.vtkMatrix4x4() # extrinsic VTK world
        pv.DeepCopy(self.cam.GetViewTransformMatrix())
        
        pr.Invert()

        newMat = vtk.vtkMatrix4x4()
        # newMat.DeepCopy(cam_pos.ravel()) 

        vtk.vtkMatrix4x4.Multiply4x4(pr, pv, newMat)
        transform = vtk.vtkTransform()
        transform.SetMatrix(newMat)
        transform.Update()

        # print(newMat)
        # cam = self.ren.GetActiveCamera()
        cam.ApplyTransform(transform)
        # cam.SetModelTransformMatrix(newMat)
        cam.Modified()
        self.ren.ResetCamera()
        self.ren.SetActiveCamera(cam)
        self.ren.Render()

        # # convert the principal point to window center (normalized coordinate system) and set it
        # wcx = -2*(principal_pt.x() - double(nx)/2) / nx
        # wcy =  2*(principal_pt.y() - double(ny)/2) / ny
        # self.cam.SetWindowCenter(wcx, wcy)

        # # convert the focal length to view angle and set it
        # view_angle = vnl_math::deg_per_rad * (2.0 * np.arctan2(ny/2.0, focal_len))
        # self.cam.SetViewAngle( view_angle );

        # # the camera Y axis points down
        # self.cam.SetViewUp(0,-1,0)
        # # the camera can stay at the origin because we are transforming the scene objects
        # self.cam.SetPosition(0, 0, 0)
        # # look in the +Z direction of the camera coordinate system
        # self.cam.SetFocalPoint(0, 0, 1)

        # cam.SetViewUp(0, 0, -1)
        # cam.SetPosition(0, -1, 0)
        # cam.SetFocalPoint(0, 0, 0)
        cam.ComputeViewPlaneNormal()

        # self.cam = self.ren.GetActiveCamera()
        # # cam.SetFocalPoint(*cam_focal)
        # # camera.SetViewUp(*cam_up)
        # self.cam.SetPosition(*cam_pos)

        # self.ren.SetActiveCamera(cam)
        self.interactor.ReInitialize()
        self.updateTextActor()

    def updateTextActor(self):
        # create a text actor
        renSize = self.ren_win.GetSize()
        self.ren.RemoveActor(self.txt)
        self.txt.SetInput('Cam Position: ' + str(np.round(self.cam.GetPosition(),2)) + '\n' + \
                          'Focal Point:   '+str(np.round(self.cam.GetFocalPoint(), 2)))
        txtprop=self.txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(12)
        txtprop.SetColor(0.7,1,1)
        self.txt.SetDisplayPosition(0,renSize[1]-30)
        self.ren.AddActor2D(self.txt)
        # self.ren.RemoveActor(txtActor)
        self.ren.SetActiveCamera(self.cam)
        self.ren.ResetCameraClippingRange()
        self.interactor.ReInitialize()

        print('ViewTransformMatrix:')
        print(self.cam.GetViewTransformMatrix())

    class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance
            self.AddObserver("LeftButtonReleaseEvent", self.left_button_press_event)
            self.AddObserver("RightButtonReleaseEvent", self.right_button_press_event)
            self.AddObserver("MiddleButtonReleaseEvent", self.middle_button_press_event)
            self.AddObserver("MouseWheelForwardEvent", self.wheel_forward_event)
            self.AddObserver("MouseWheelBackwardEvent", self.wheel_backward_event)

        def left_button_press_event(self, obj, event):
            self.outer_instance.updateTextActor()
            self.OnLeftButtonUp()
            return

        def right_button_press_event(self, obj, event):
            self.outer_instance.updateTextActor()
            self.OnRightButtonUp()
            return

        def middle_button_press_event(self, obj, event):
            self.outer_instance.updateTextActor()
            self.OnMiddleButtonUp()
            return

        def wheel_forward_event(self, obj, event):
            self.outer_instance.updateTextActor()
            self.OnMouseWheelForward()
            return

        def wheel_backward_event(self, obj, event):
            self.outer_instance.updateTextActor()
            self.OnMouseWheelBackward()
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
        self.interactor.setMinimumSize(width+30, height)
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

    def removeImage(self):
        self.ren.RemoveAllViewProps()

    def showImage(self, reader):

        image = reader.GetOutput()
        self.dims = image.GetDimensions()

        # imageViewerDCM = vtk.vtkImageViewer2()
        # imageViewerDCM.SetInputConnection(reader.GetOutputPort())
        # # mMinSliderX = imageViewerDCM.GetSliceMin()
        # # mMaxSliderX = imageViewerDCM.GetSliceMax()
        # imageViewerDCM.SetRenderWindow(self.ren.GetRenderWindow())

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
            self.plane.SetDisplayExtent(0, self.dims[0], 0, self.dims[1], self.dims[2]//2, self.dims[2]//2)
            # cam.SetPosition(0, 0, -1)
            cam.Roll(180)
            # cam.OrthogonalizeViewUp()
        elif self.planeType == "coronal":
            self.plane.SetDisplayExtent(0, self.dims[0], self.dims[1]//2, self.dims[1]//2, 0, self.dims[2])
            # cam.SetPosition(0, -1, 0)
            cam.Elevation(90)
            # cam.OrthogonalizeViewUp()
        else:  # self.planeType == "sagittal"
            self.plane.SetDisplayExtent(self.dims[0]//2, self.dims[0]//2, 0, self.dims[1], 0, self.dims[2])
            # cam.SetPosition(-1, 0, 0)
            cam.Azimuth(90)
            cam.Roll(90)
            # cam.OrthogonalizeViewUp()

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
        # self.interactor.Start()

    def setSlice(self, sliceNumber):
        if self.planeType == "axial":
            self.plane.SetDisplayExtent(0, self.dims[0], 0, self.dims[1], sliceNumber, sliceNumber)
            # # cam.SetPosition(0, 0, -1)
            # cam.Roll(180)

        elif self.planeType == "coronal":
            self.plane.SetDisplayExtent(0, self.dims[0], sliceNumber, sliceNumber, 0, self.dims[2])
            # # cam.SetPosition(0, -1, 0)
            # cam.Elevation(90)
            # cam.OrthogonalizeViewUp()
        else:  # self.planeType == "sagittal"
            self.plane.SetDisplayExtent(sliceNumber, sliceNumber, 0, self.dims[1], 0, self.dims[2])
            # # cam.SetPosition(-1, 0, 0)
            # cam.Azimuth(90)
            # cam.Roll(90)
            # cam.OrthogonalizeViewUp()
