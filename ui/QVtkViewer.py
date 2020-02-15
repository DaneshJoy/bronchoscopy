import vtk
from PyQt5.QtWidgets import QFrame
from PyQt5 import QtWidgets, QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np

class QVtkViewer3D(QFrame):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.colors = vtk.vtkNamedColors()
        self.colors.SetColor("SkinColor", [204, 153, 51, 255]) # rgba
        self.colors.SetColor("BkgColor", [51, 77, 102, 255])
        self.axes = vtk.vtkOrientationMarkerWidget()
        # Make the actual QtWidget a child so that it can be reparented
        self.interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.interactor)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.width = (size.width()) // 2 - 100
        self.height = (size.height()) // 2 - 50
        self.interactor.setMinimumSize(self.width, self.height)
        self.interactor.setMaximumSize(self.width, self.height)
        self.setLayout(self.layout)

        self.initCamViewUp = (0, 0, 1)
        self.initCamPosition = (0, 1, 0)
        self.initCamFocalPoint = (0, 0, 0)

        self.points = None

        # Setup VTK Environment
        self.ren = vtk.vtkRenderer()
        self.interactor.GetRenderWindow().AddRenderer(self.ren)

        # self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.SetInteractorStyle(self.MyInteractorStyle(self))
        self.ren.SetBackground(0, 0, 0)
        # ren.SetBackground(colors.GetColor3D("BkgColor"))
        self.interactor.Initialize()

    def RemoveImage(self):
        self.ren.RemoveAllViewProps()
        self.ren.ResetCamera()

    def showImage(self, reader):

        # Isosurface
        self.surfaceExtractor = vtk.vtkMarchingCubes()
        self.surfaceExtractor.SetInputConnection(reader.GetOutputPort())
        ''' 
        Marching Cubes is used to build a surface from iso-values field
        It thresholds the data into binary information,
        such that if an iso-value is above it gets 1 and 0 otherwise.
        Finally, it computes the surface interpolating triangles near the iso-value.
        SetValue(i, isoVal) is used to select which iso-value you want to threshold for the Marching Cubes algorithm.
        i = contour number and isoVal = the iso-value representing the contour you looking for.
        You can build multiple surfaces by setting different contour number i, for different iso-value.
        '''
        self.surfaceExtractor.SetValue(0, -600)

        # Mapper
        surfaceMapper = vtk.vtkPolyDataMapper()
        surfaceMapper.SetInputConnection(self.surfaceExtractor.GetOutputPort())
        surfaceMapper.ScalarVisibilityOff()
        # skinMapper.UseLookupTableScalarRangeOn()

        # Actor
        self.surface = vtk.vtkActor()
        self.surface.SetMapper(surfaceMapper)
        # self.surface.GetProperty().SetDiffuseColor(0.8, 0.6, 0.2)
        self.surface.GetProperty().SetAmbient(0.1)
        # self.surface.GetProperty().SetOpacity(0.9)
        # self.surface.GetProperty().SetDiffuseColor(1, .49, .25)
        self.surface.GetProperty().SetDiffuseColor(self.colors.GetColor3d("SkinColor"))
        self.surface.GetProperty().SetSpecular(0.7)
        self.surface.GetProperty().SetSpecularPower(40)
        self.surface.GetProperty().SetDiffuse(0.7)

        # Camera
        cam = vtk.vtkCamera()
        # self.cam.SetViewUp(0,-1,0) # the camera Y axis points down
        # self.cam.SetPosition(0, 0, 0)
        # self.cam.SetFocalPoint(0, 0, 1) # look in the +Z direction of the camera coordinate system
        cam.SetViewUp(0, 0, 1)
        cam.SetPosition(0, 1, 0)
        cam.SetFocalPoint(0, 0, 0)
        cam.ComputeViewPlaneNormal()
        # cam.Azimuth(30.0)
        # cam.Elevation(30.0)
        cam.Dolly(1.5) # Moves the camera towards the FocalPoint

        # self.updateTextActor()

        self.ShowOrientationWidget()

        self.ren.AddActor(self.surface)

        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
        self.ren.ResetCameraClippingRange()

        self.initCamViewUp = self.ren.GetActiveCamera().GetViewUp()
        self.initCamPosition = self.ren.GetActiveCamera().GetPosition()
        self.initCamFocalPoint = self.ren.GetActiveCamera().GetFocalPoint()

        # self.renderer = ren
        # self.interactor = interactor
        self.interactor.Initialize()
        # self.interactor.Start()

    def ShowOrientationWidget(self):
        # # Cube Actor
        # cubeActor = vtk.vtkAnnotatedCubeActor()
        # cubeActor.SetXPlusFaceText('+X')
        # cubeActor.SetXMinusFaceText('-X')
        # cubeActor.SetYMinusFaceText('-Y')
        # cubeActor.SetYPlusFaceText('+Y')
        # cubeActor.SetZMinusFaceText('-Z')
        # cubeActor.SetZPlusFaceText('+Z')
        # cubeActor.GetTextEdgesProperty().SetColor(0,1,1)
        # cubeActor.GetTextEdgesProperty().SetLineWidth(1)
        # cubeActor.GetCubeProperty().SetColor(0.7,0.7,0.7)

        # Axes Actor
        # axesActor = vtk.vtkAxesActor()

        # Human Actor.
        readerH = vtk.vtkXMLPolyDataReader()
        readerH.SetFileName('Human.vtp')
        readerH.Update()
        humanMapper = vtk.vtkPolyDataMapper()
        humanMapper.SetInputConnection(readerH.GetOutputPort())
        humanMapper.SetScalarModeToUsePointFieldData()
        humanMapper.SelectColorArray("Color")
        humanMapper.SetColorModeToDirectScalars()
        humanActor = vtk.vtkActor()
        humanActor.SetMapper(humanMapper)
        bounds = self.surface.GetBounds()
        humanActor.SetScale(max(bounds)/10.0)
        
        self.axes.SetOrientationMarker(humanActor)
        self.axes.SetInteractor(self.interactor)
        # Position lower left in the viewport.
        self.axes.SetViewport(0.0, 0.85, 0.15, 1.0)  # (xmin,ymin,xmax,ymax)
        self.axes.EnabledOn() # <== application freeze-crash
        self.axes.InteractiveOn()

    def ResetView(self):
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().SetViewUp(self.initCamViewUp)
        self.ren.GetActiveCamera().SetPosition(self.initCamPosition)
        self.ren.GetActiveCamera().SetFocalPoint(self.initCamFocalPoint)
        self.ren.GetActiveCamera().ComputeViewPlaneNormal()
        # self.ren.GetActiveCamera().Dolly(1.5)
        self.ren.ResetCameraClippingRange()
        self.interactor.ReInitialize()

    def DrawPoints(self, points):
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

        # flipTrans = vtk.vtkTransform()
        # flipTrans.Scale(-1,-1,1)
        # flipFilt = vtk.vtkTransformPolyDataFilter()
        # # flipFilt = vtk.vtkTransformFilter()
        # flipFilt.SetTransform(flipTrans)
        # flipFilt.SetInputData(poly)
        # flipFilt.Update()
        # pmap.SetInputDataObject(flipFilt.GetOutput())

        pmap.SetInputDataObject(poly)

        # actor
        self.points = vtk.vtkActor()
        self.points.SetMapper(pmap)
        self.points.GetProperty().SetPointSize(2)
        self.points.GetProperty().SetColor(0.5,1,1) # (R,G,B)

        # assign actor to the renderer
        self.ren.AddActor(self.points)
        self.interactor.ReInitialize()
        # self.ren.ResetCameraClippingRange()

    def RemovePoints(self):
        if self.points == None:
            return
        self.ren.RemoveActor(self.points)
        self.ren.RemoveActor(self.startPoint)
        self.ren.RemoveActor(self.endPoint)
        self.interactor.ReInitialize()
        self.points = None
        self.startPoint = None
        self.endPoint = None

    def AddStartPoint(self, pos, color=[0,1,0]):
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

        sphere.SetRadius(2)
        # sphere.SetThetaResolution(2)
        # sphere.SetPhiResolution(2)

        # mapper
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(t_sphere.GetOutput())
        else:
            mapper.SetInputConnection(t_sphere.GetOutputPort())

        # actor
        self.startPoint = vtk.vtkActor()
        self.startPoint.SetMapper(mapper)
        self.startPoint.GetProperty().SetColor(color) # (R,G,B)

        # assign actor to the renderer
        self.ren.AddActor(self.startPoint)

        self.interactor.ReInitialize()

    def AddEndPoint(self, pos, color=[1,0,0]):
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

        sphere.SetRadius(2)
        # sphere.SetThetaResolution(2)
        # sphere.SetPhiResolution(2)

        # mapper
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(t_sphere.GetOutput())
        else:
            mapper.SetInputConnection(t_sphere.GetOutputPort())

        # actor
        self.endPoint = vtk.vtkActor()
        self.endPoint.SetMapper(mapper)
        self.endPoint.GetProperty().SetColor(color) # (R,G,B)

        # assign actor to the renderer
        self.ren.AddActor(self.endPoint)
        self.interactor.ReInitialize()

    def setCamera(self, cam_pos):

        ''' Set Camera Intrinsics '''
        px = 206.147
        py = 153.122
        fx = 120.030
        fy = 120.726
        w, h = self.interactor.GetSize()

        # factor = h / self.height
        # px = factor * px
        # we = np.round(factor * self.width)
        # if (we != w):
        #     diffX = (w - we)/2
        #     px = px + diffX

        # py = factor * py

        # cx = self.width - px
        # cy = py

        # convert the principal point to window center (normalized coordinate system) and set it
        # wcx = cx / ((w-1)/2) - 1
        # wcy = cy / ((h-1)/2) - 1
        wcx = -2.0*(px - w/2.0) / w
        wcy =  2.0*(py - h/2.0) / h
        self.ren.GetActiveCamera().SetWindowCenter(wcx, wcy)

        # Set vertical view angle as a indirect way of setting the y focal distance
        view_angle = 180 / np.pi * 2.0 * np.arctan2(h / 2.0, fy)
        self.ren.GetActiveCamera().SetViewAngle(view_angle)

        # Set the image aspect ratio as an indirect way of setting the x focal distance
        m = np.eye(4)
        aspect = fy/fx
        m[0,0] = 1.0/aspect
        t = vtk.vtkTransform()
        t.SetMatrix(m.flatten())
        self.ren.GetActiveCamera().SetUserTransform(t)

        ''' Set Camera Extrinsics '''
        pr = vtk.vtkMatrix4x4() # extrinsic Real world
        # copy from numpy to vtkMatrix4x4
        pr.DeepCopy(cam_pos.ravel()) 
        # pr.Invert()

        pv = vtk.vtkMatrix4x4() # extrinsic VTK world
        pv.DeepCopy(self.ren.GetActiveCamera().GetViewTransformMatrix())

        newMat = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Multiply4x4(pr, pv, newMat)
        transform = vtk.vtkTransform()
        transform.SetMatrix(newMat)
        transform.Update()

        self.ren.GetActiveCamera().ApplyTransform(transform)

        self.ren.GetActiveCamera().Yaw(180)

        self.ren.GetActiveCamera().Zoom(0.901)
        # Use the following two lines to have a nice start from far!
        # self.ren.GetActiveCamera().Azimuth(180)
        # self.ren.GetActiveCamera().Dolly(1.2)

        # near = 0.1
        # far = 1000.0
        # self.ren.GetActiveCamera().SetClippingRange(near, far)
        self.ren.ResetCameraClippingRange()
        # self.ren.GetActiveCamera().ComputeViewPlaneNormal()
        # self.ren.GetActiveCamera().OrthogonalizeViewUp()
        # self.ren.Render()

        self.interactor.ReInitialize()

        # self.updateTextActor() # This function has interactor.ReInitialize() in it

    def updateTextActor(self):
        # create a text actor
        renSize = self.ren_win.GetSize()
        self.ren.RemoveActor(self.txt)
        self.txt.SetInput('Cam Position: ' + str(np.round(self.ren.GetActiveCamera().GetPosition(),2)) + '\n' + \
                          'Focal Point:   '+str(np.round(self.ren.GetActiveCamera().GetFocalPoint(), 2)))
        txtprop=self.txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(12)
        txtprop.SetColor(0.7,1,1)
        self.txt.SetDisplayPosition(0,renSize[1]-30)
        self.ren.AddActor2D(self.txt)
        # self.ren.RemoveActor(txtActor)
        # self.ren.SetActiveCamera(self.cam)
        # self.ren.ResetCameraClippingRange()
        self.interactor.ReInitialize()

    class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance
            self.AddObserver("LeftButtonReleaseEvent", self.left_button_press_event)
            self.AddObserver("RightButtonReleaseEvent", self.right_button_press_event)
            self.AddObserver("MiddleButtonReleaseEvent", self.middle_button_press_event)
            self.AddObserver("MouseWheelForwardEvent", self.wheel_forward_event)
            self.AddObserver("MouseWheelBackwardEvent", self.wheel_backward_event)

        def left_button_press_event(self, obj, event):
            # self.outer_instance.updateTextActor()
            self.OnLeftButtonUp()
            return

        def right_button_press_event(self, obj, event):
            # self.outer_instance.updateTextActor()
            self.OnRightButtonUp()
            return

        def middle_button_press_event(self, obj, event):
            # self.outer_instance.updateTextActor()
            self.OnMiddleButtonUp()
            return

        def wheel_forward_event(self, obj, event):
            # self.outer_instance.updateTextActor()
            self.OnMouseWheelForward()
            return

        def wheel_backward_event(self, obj, event):
            # self.outer_instance.updateTextActor()
            self.OnMouseWheelBackward()
            return


class QVtkViewer2D(QFrame):
    def __init__(self, parent, size, planeType):
        super().__init__(parent)

        self.colors = vtk.vtkNamedColors()
        self.colors.SetColor("BkgColor", [0, 0, 0, 255])

        # Make the actual QtWidget a child so that it can be reparented
        self.interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.interactor)
        # self.layout.setStretchFactor(self.interactor,1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.width = (size.width()) // 2 - 100
        self.height = (size.height()) // 2 - 50
        self.interactor.setMinimumSize(self.width, self.height)
        self.interactor.setMaximumSize(self.width, self.height)
        self.setLayout(self.layout)

        self.cross = None
        
        # Setup VTK Environment
        self.ren = vtk.vtkRenderer()

        self.interactor.GetRenderWindow().AddRenderer(self.ren)
        # self.interactor.GetRenderWindow().SetSize(self.width, self.height)
        self.interactor.GetRenderWindow().SetWindowName(planeType)

        # self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera)
        # self.interactor.SetInteractorStyle(MyInteractorStyle())
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())

        # self.ren.SetBackground(0, 0, 0)
        self.ren.SetBackground(self.colors.GetColor3d("BkgColor"))
        self.interactor.Initialize()

        self.actor = vtk.vtkImageActor()
        self.planeType = planeType

    def DummyFunc1(self, obj, ev):
        clickPos = self.interactor.GetEventPosition()
        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToDisplay()
        coordinate.SetValue(clickPos[0], clickPos[1])
        disp1 = coordinate.GetComputedWorldValue(self.ren)

        # Pick from this location.
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        # Pick position (world coordinates)
        pos = picker.GetPickPosition()

        # Click on Axial:
        # saggital_slice = (origin[0]+pos[0])/spacing[0]
        # coronal_slice = (origin[1]+pos[1])/spacing[1]

        # Click on Coronal:
        # axial_slice = (origin[2]+pos[0])/spacing[2]
        # saggital_slice = (origin[1]+pos[1])/spacing[1]

        # Click on Saggital:
        # coronal_slice = (origin[1]+pos[0])/spacing[1]
        # axial_slice = (origin[2]+pos[1])/spacing[2]

        self.SetCrossPosition(pos[0], pos[1])
        # self.interactor.ReInitialize()
        print("Before Event")

    def DummyFunc2(self, obj, ev):
        print("After Event")

    def SetCrossPosition(self, x, y):
        if self.cross == None:
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(self.CreateCross(50))
            self.cross = vtk.vtkActor()
            self.cross.GetProperty().SetLineWidth(2)
            self.cross.SetMapper(mapper)
            self.ren.AddActor(self.cross)
        self.cross.SetPosition(x, y, 1)
        self.ren.GetRenderWindow().Render()

    def RemoveImage(self):
        self.ren.RemoveAllViewProps()
        self.cross = None
        self.ren.ResetCamera()

    def RemoveCross(self):
        self.ren.RemoveActor(self.cross)
        self.ren.GetRenderWindow().Render()
        self.cross = None

    def showImage(self, reader, dims):
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
        ''' ==================== Show Planes Method 1 ==================== '''

        # # plane
        # planeColors = vtk.vtkImageMapToColors()
        # planeColors.SetInputConnection(reader.GetOutputPort())
        # planeColors.SetLookupTable(grLut)
        # planeColors.Update()
        # self.actor.GetMapper().SetInputConnection(planeColors.GetOutputPort())

        # if self.planeType == "axial":
        #     currSlice = dims[2]//2
        #     self.actor.SetDisplayExtent(0, dims[0], 0, dims[1], currSlice, currSlice)
        #     # cam.SetPosition(0, 0, -1)
        #     cam.Yaw(180) # Flip L/R
        #     cam.Pitch(180) # Flip U/D
        #     cam.OrthogonalizeViewUp()
        #     # cam.Dolly(2)
        # elif self.planeType == "coronal":
        #     currSlice = dims[1]//2
        #     self.actor.SetDisplayExtent(0, dims[0], currSlice, currSlice, 0, dims[2])
        #     # cam.SetPosition(0, -1, 0)
        #     cam.Yaw(180) # Flip L/R
        #     # cam.Roll(180) # Flip U/D
        #     cam.Elevation(90)
        #     cam.OrthogonalizeViewUp()
        #     # cam.Zoom(2)
        # else:  # self.planeType == "sagittal"
        #     currSlice = dims[0]//2
        #     self.actor.SetDisplayExtent(currSlice, currSlice, 0, dims[1], 0, dims[2])
        #     # cam.SetPosition(-1, 0, 0)
        #     cam.Yaw(180) # Flip L/R
        #     cam.Roll(180) # Flip U/D
        #     cam.Azimuth(90)
        #     cam.Roll(90)
        #     cam.OrthogonalizeViewUp()
        #     # cam.Zoom(2)
        ''' ============================================================ '''

        ''' ==================== Show Planes Method 2 ==================== '''
        # Calculate the center of the volume
        self.spacing = reader.GetOutput().GetSpacing()
        self.origin = reader.GetOutput().GetOrigin()
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

        self.reslice = vtk.vtkImageReslice()
        self.reslice.SetInputConnection(reader.GetOutputPort())
        self.reslice.SetOutputDimensionality(2)
        if self.planeType == "axial":
            self.reslice.SetResliceAxes(axial)
        elif self.planeType == "coronal":
            self.reslice.SetResliceAxes(coronal)
        else:  # self.planeType == "sagittal"
            self.reslice.SetResliceAxes(sagittal)
        self.reslice.SetInterpolationModeToCubic()

        # Map the image through the lookup table
        colors = vtk.vtkImageMapToColors()
        colors.SetInputConnection(self.reslice.GetOutputPort())
        colors.SetLookupTable(grLut)
        colors.Update()

        self.actor.GetMapper().SetInputConnection(colors.GetOutputPort())
        ''' ============================================================ '''

        self.ren.AddActor2D(self.actor)

        ''' ==================== Add Orientation Widget ==================== '''
        # # Human Actor.
        # readerH = vtk.vtkXMLPolyDataReader()
        # readerH.SetFileName('Human.vtp')
        # readerH.Update()
        # humanMapper = vtk.vtkPolyDataMapper()
        # humanMapper.SetInputConnection(readerH.GetOutputPort())
        # humanMapper.SetScalarModeToUsePointFieldData()
        # humanMapper.SelectColorArray("Color")
        # humanMapper.SetColorModeToDirectScalars()
        # humanActor = vtk.vtkActor()
        # humanActor.SetMapper(humanMapper)
        # bounds = self.actor.GetBounds()
        # humanActor.SetScale(max(bounds)/10.0)
        
        # self.axes.SetOrientationMarker(humanActor)
        # self.axes.SetInteractor(self.interactor)
        # # Position lower left in the viewport.
        # self.axes.SetViewport(0.0, 0.85, 0.15, 1.0)  # (xmin,ymin,xmax,ymax)
        # self.axes.EnabledOn()
        # self.axes.InteractiveOn()
        ''' ============================================================ '''

        # cam.SetFocalPoint(0, 0, 0)
        # cam.SetPosition(0, -1, 0)
        cam.ComputeViewPlaneNormal()
        # cam.Azimuth(30.0)
        # cam.Elevation(30.0)
        # ren_win.Render()
        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
        cam.Zoom(1.5)
        # self.ren.GetActiveCamera.Zoom(2)
        # cam.Dolly(1.5)  # Moves the camera towards the FocalPoint

        #drawing a Line
        # self.drawLine(0)

        ''' Create and Show Cross '''
        # imageData = reader.GetOutput()
        # imageCenter = imageData.GetCenter()
        # bounds = imageData.GetBounds()
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputData(self.CreateCross(50))
        # self.cross = vtk.vtkActor()
        # self.cross.GetProperty().SetLineWidth(2)
        # self.cross.SetPosition(imageCenter[0],imageCenter[1],imageCenter[2]);
        # self.cross.SetMapper(mapper)
        # self.ren.AddActor(self.cross)

        # # self.interactor.RemoveObservers('LeftButtonPressEvent')
        # self.interactor.AddObserver('LeftButtonPressEvent', self.DummyFunc1, 1.0)
        # # self.interactor.AddObserver('LeftButtonPressEvent', self.DummyFunc2, -1.0)
        ''' =============== '''

        self.ren.ResetCameraClippingRange()
        # self.renderer = ren
        # self.interactor = interactor

        self.interactor.Initialize()
        # self.interactor.Start()

        # create a cross
    def CreateCross(self, size):
        #Create a vtkPoints object and store the points in it
        pts = vtk.vtkPoints()
        pts.InsertNextPoint(-size / 2, 0, 0)
        pts.InsertNextPoint(size / 2, 0, 0)
        pts.InsertNextPoint(0, -size / 2, 0)
        pts.InsertNextPoint(0, size / 2, 0)

        # Setup the colors array
        color = (0, 170, 170)
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")

        # Add the colors we created to the colors array
        colors.InsertNextValue(color[0])
        colors.InsertNextValue(color[1])
        colors.InsertNextValue(color[2])

        colors.InsertNextValue(color[0])
        colors.InsertNextValue(color[1])
        colors.InsertNextValue(color[2])

        # Create the first line
        line0 = vtk.vtkLine()
        line0.GetPointIds().SetId(0, 0)
        line0.GetPointIds().SetId(1, 1)

        # Create the second line
        line1 = vtk.vtkLine()
        line1.GetPointIds().SetId(0, 2)
        line1.GetPointIds().SetId(1, 3)

        # Create a cell array to store the lines in and add the lines to it
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(line0)
        lines.InsertNextCell(line1)

        # Create a polydata to store everything in
        linesPolyData = vtk.vtkPolyData()
        # Add the points to the dataset
        linesPolyData.SetPoints(pts)
        # Add the lines to the dataset
        linesPolyData.SetLines(lines)
        # Color the lines
        linesPolyData.GetCellData().SetScalars(colors)
        return linesPolyData

    def drawLine(self, sliceNumber):
        winSize = self.interactor.GetRenderWindow().GetSize()
        p0 = [0, -self.height//2, 1]
        p1 = [0, self.height//2, 1]
        p2 = [-self.width//2, 0, 1]
        p3 = [self.width//2, 0, 1]

        # Create a vtkPoints object and store the points in it
        pts = vtk.vtkPoints()
        pts.InsertNextPoint(p0)
        pts.InsertNextPoint(p1)
        pts.InsertNextPoint(p2)
        pts.InsertNextPoint(p3)

        # Create the first line (between Origin and P0)
        line0 = vtk.vtkLine()
        line0.GetPointIds().SetId(0,0) # the second 0 is the index of P0 in the vtkPoints
        line0.GetPointIds().SetId(1,1) # the second 1 is the index of P1 in the vtkPoints

        # Create the second line (between Origin and P1)
        line1 = vtk.vtkLine()
        line1.GetPointIds().SetId(0,2) # the second 0 is the index of the Origin in the vtkPoints
        line1.GetPointIds().SetId(1,3) # 2 is the index of P1 in the vtkPoints

        # Create a cell array to store the lines in and add the lines to it
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(line0)
        lines.InsertNextCell(line1)

        # Setup the colors array
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")
    
        # Add the colors we created to the colors array
        colors.InsertNextTuple3(0, 170, 170)
        colors.InsertNextTuple3(0, 170, 170)

        # Create a polydata to store everything in
        linesPolyData = vtk.vtkPolyData()

        # Add the points to the dataset
        linesPolyData.SetPoints(pts)

        # Add the lines to the dataset
        linesPolyData.SetLines(lines)

        # Color the lines - associate the first component (red) of the
        # colors array with the first component of the cell array (line 0)
        # and the second component (green) of the colors array with the
        # second component of the cell array (line 1)
        linesPolyData.GetCellData().SetScalars(colors)

        # Visualize
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInputConnection(linesPolyData.GetProducerPort())
        else:
            mapper.SetInputData(linesPolyData)
            mapper.Update()

        self.lineActor = vtk.vtkActor()
        self.lineActor.SetMapper(mapper)
        self.ren.AddActor2D(self.lineActor)

    # def setSlice(self, sliceNumber, dims):
    def setSlice(self, sliceNumber):
        # self.ren.RemoveActor(self.lineActor)
        # self.drawLine(sliceNumber, dims)

        ''' ==================== Show Planes Method 1 ==================== '''
        # if self.planeType == "axial":
        #     # sliceNumber = int(sliceNumber)
        #     self.actor.SetDisplayExtent(0, dims[0], 0, dims[1], sliceNumber, sliceNumber)
        #     # # cam.SetPosition(0, 0, -1)
        #     # cam.Roll(180)
        # elif self.planeType == "coronal":
        #     # sliceNumber = int(sliceNumber)
        #     self.actor.SetDisplayExtent(0, dims[0], sliceNumber, sliceNumber, 0, dims[2])
        #     # # cam.SetPosition(0, -1, 0)
        #     # cam.Elevation(90)
        #     # cam.OrthogonalizeViewUp()
        # else:  # self.planeType == "sagittal"
        #     # sliceNumber = int(sliceNumber)
        #     self.actor.SetDisplayExtent(sliceNumber, sliceNumber, 0, dims[1], 0, dims[2])
        #     # # cam.SetPosition(-1, 0, 0)
        #     # cam.Azimuth(90)
        #     # cam.Roll(90)
        #     # cam.OrthogonalizeViewUp()

        ''' ==================== Show Planes Method 2 ==================== '''
        self.reslice.Update()
        matrix = self.reslice.GetResliceAxes()
        # move the center point that we are slicing through
        if self.planeType == "axial":
            sliceNumber = self.origin[2] + sliceNumber*self.spacing[2]
            matrix.SetElement(2, 3, sliceNumber)
        elif self.planeType == "coronal":
            sliceNumber = self.origin[1] + sliceNumber*self.spacing[1]
            matrix.SetElement(1, 3, sliceNumber)
        else:  # self.planeType == "sagittal"
            sliceNumber = self.origin[0] + sliceNumber*self.spacing[0]
            matrix.SetElement(0, 3, sliceNumber)
        self.ren.GetRenderWindow().Render()

    def ResetView(self):
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.5)
        self.actor.GetProperty().SetColorWindow(255)
        self.actor.GetProperty().SetColorLevel(127.5)
        self.interactor.ReInitialize()

