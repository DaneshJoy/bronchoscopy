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
        self.width = (size.width()-370) // 2
        self.height = (size.height()-170) // 2
        self.interactor.setMinimumSize(self.width+30, self.height)
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

        # Isosurface
        self.surfaceExtractor = vtk.vtkMarchingCubes()
        self.surfaceExtractor.SetInputConnection(reader.GetOutputPort())
        self.surfaceExtractor.SetValue(0, 300)

        # Mapper
        surfaceMapper = vtk.vtkPolyDataMapper()
        surfaceMapper.SetInputConnection(self.surfaceExtractor.GetOutputPort())
        surfaceMapper.ScalarVisibilityOff()
        # skinMapper.UseLookupTableScalarRangeOn()

        # Actor
        self.surface = vtk.vtkActor()
        self.surface.SetMapper(surfaceMapper)
        self.surface.GetProperty().SetDiffuseColor(0.8, 0.6, 0.2)
        self.surface.GetProperty().SetAmbient(0.1)
        # self.surface.GetProperty().SetOpacity(0.9)
        # self.surface.GetProperty().SetDiffuseColor(1, .49, .25)
        # self.surface.GetProperty().SetDiffuseColor(colors.GetColor3D("SkinColor"))
        self.surface.GetProperty().SetSpecular(0.7)
        self.surface.GetProperty().SetSpecularPower(40)
        self.surface.GetProperty().SetDiffuse(0.7)

        # Camera
        cam = vtk.vtkCamera()
        # self.cam.SetViewUp(0,-1,0) # the camera Y axis points down
        # self.cam.SetPosition(0, 0, 0)
        # self.cam.SetFocalPoint(0, 0, 1) # look in the +Z direction of the camera coordinate system
        cam.SetViewUp(0, 0, 1)
        cam.SetPosition(0, -1, 0)
        cam.SetFocalPoint(0, 0, 0)
        cam.ComputeViewPlaneNormal()
        # cam.Azimuth(30.0)
        # cam.Elevation(30.0)
        cam.Dolly(1.5) # Moves the camera towards the FocalPoint

        # self.updateTextActor()

        self.ren.AddActor(self.surface)
        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
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
        self.points = vtk.vtkActor()
        self.points.SetMapper(pmap)
        self.points.GetProperty().SetPointSize(2)
        self.points.GetProperty().SetColor(0.5,1,1) # (R,G,B)

        # assign actor to the renderer
        self.ren.AddActor(self.points)
        self.interactor.ReInitialize()
        # self.ren.ResetCameraClippingRange()

    def removePoints(self):
        self.ren.RemoveActor(self.points)
        self.ren.RemoveActor(self.startPoint)
        self.ren.RemoveActor(self.endPoint)
        self.interactor.ReInitialize()

    def addStartPoint(self, pos, color=[0,1,0]):
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

    def addEndPoint(self, pos, color=[1,0,0]):
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

        # Make the actual QtWidget a child so that it can be reparented
        self.interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.interactor)
        # self.layout.setStretchFactor(self.interactor,1)
        self.layout.setContentsMargins(0, 0, 0, 0)

        width = (size.width()) // 2
        height = (size.height()) // 2
        self.interactor.setMinimumSize(width, height)
        self.setLayout(self.layout)

        # Setup VTK Environment
        self.ren = vtk.vtkRenderer()

        self.interactor.GetRenderWindow().AddRenderer(self.ren)
        self.interactor.GetRenderWindow().SetSize(width, height)
        self.interactor.GetRenderWindow().SetWindowName(planeType)

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

    def showImage(self, reader, dims):
        # image = reader.GetOutput()
        # self.dims = image.GetDimensions()

        # black/white lookup table
        bwLut = vtk.vtkLookupTable()
        bwLut.SetTableRange(0, 1000)
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
        cam.SetFocalPoint(0, 0, 0)
        # cam.SetPosition(0, -1, 0)
        cam.ComputeViewPlaneNormal()
        # cam.Azimuth(30.0)
        # cam.Elevation(30.0)

        if self.planeType == "axial":
            currSlice = dims[2]//2
            self.plane.SetDisplayExtent(0, dims[0], 0, dims[1], currSlice, currSlice)
            # cam.SetPosition(0, 0, -1)
            cam.Yaw(180)
            cam.OrthogonalizeViewUp()
            cam.Dolly(2)
        elif self.planeType == "coronal":
            currSlice = dims[1]//2
            self.plane.SetDisplayExtent(0, dims[0], currSlice, currSlice, 0, dims[2])
            # cam.SetPosition(0, -1, 0)
            cam.Elevation(90)
            cam.OrthogonalizeViewUp()
            cam.Zoom(2)
        else:  # self.planeType == "sagittal"
            currSlice = dims[0]//2
            self.plane.SetDisplayExtent(currSlice, currSlice, 0, dims[1], 0, dims[2])
            # cam.SetPosition(-1, 0, 0)
            cam.Azimuth(90)
            cam.Roll(90)
            cam.OrthogonalizeViewUp()
            cam.Zoom(2)

        self.ren.AddActor(self.plane)

        #drawing a Line
        self.drawLine(currSlice, dims)

        # ren_win.Render()
        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
        # cam.Dolly(1.5)  # Moves the camera towards the FocalPoint
        self.ren.ResetCameraClippingRange()

        # self.renderer = ren
        # self.interactor = interactor

        # self.interactor.RemoveObservers('LeftButtonPressEvent')
        # self.interactor.AddObserver('LeftButtonPressEvent', self.DummyFunc1, 1.0)
        # self.interactor.AddObserver('LeftButtonPressEvent', self.DummyFunc2, -1.0)

        self.interactor.Initialize()
        # self.interactor.Start()

    def drawLine(self, sliceNumber, dims):
        winSize = self.interactor.GetRenderWindow().GetSize()
        if self.planeType == "axial":
            p0 = [winSize[0]//2, 0, sliceNumber]
            p1 = [winSize[0]//2, winSize[1], sliceNumber]
            p2 = [0, winSize[1]//2, sliceNumber+58]
            p3 = [winSize[0], winSize[1]//2, sliceNumber]
        elif self.planeType == "coronal":
            p0 = [dims[0]//2, 0, dims[2]//2]
            p1 = [dims[0]//2, dims[1], dims[2]//2]
            p2 = [0, dims[1]//2, dims[2]//2]
            p3 = [dims[0], dims[1]//2, dims[2]//2]
        else:  # self.planeType == "sagittal"
            p0 = [dims[0]//2, 0, dims[2]//2]
            p1 = [dims[0]//2, dims[1], dims[2]//2]
            p2 = [0, dims[1]//2, dims[2]//2]
            p3 = [dims[0], dims[1]//2, dims[2]//2]

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
        # linesPolyData.GetCellData().SetScalars(colors)

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

    def setSlice(self, sliceNumber, dims):
        self.ren.RemoveActor(self.lineActor)
        self.drawLine(sliceNumber, dims)
        if self.planeType == "axial":
            self.plane.SetDisplayExtent(0, dims[0], 0, dims[1], sliceNumber, sliceNumber)
            # # cam.SetPosition(0, 0, -1)
            # cam.Roll(180)
        elif self.planeType == "coronal":
            self.plane.SetDisplayExtent(0, dims[0], sliceNumber, sliceNumber, 0, dims[2])
            # # cam.SetPosition(0, -1, 0)
            # cam.Elevation(90)
            # cam.OrthogonalizeViewUp()
        else:  # self.planeType == "sagittal"
            self.plane.SetDisplayExtent(sliceNumber, sliceNumber, 0, dims[1], 0, dims[2])
            # # cam.SetPosition(-1, 0, 0)
            # cam.Azimuth(90)
            # cam.Roll(90)
            # cam.OrthogonalizeViewUp()