from viewers.QVtkViewer import QVTKViewer
import vtk
import numpy as np

class QVtkViewer3D(QVTKViewer):
    def __init__(self, panel, size, viewType):
        super().__init__(panel, size, viewType)

    def show_image(self, reader):
        
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
        if self.viewType == 'Virtual':
            self.surfaceExtractor.SetValue(0, -600)
        else:
            self.surfaceExtractor.SetValue(0, -600)

        # Mapper
        surfaceMapper = vtk.vtkOpenGLPolyDataMapper()
        surfaceMapper.SetInputConnection(self.surfaceExtractor.GetOutputPort())
        surfaceMapper.ScalarVisibilityOff()
        # skinMapper.UseLookupTableScalarRangeOn()

        # Actor
        self.surface = vtk.vtkOpenGLActor()
        self.surface.SetMapper(surfaceMapper)
        # self.surface.GetProperty().SetDiffuseColor(0.8, 0.6, 0.2)
        self.surface.GetProperty().SetAmbient(0.1)
        if self.viewType == 'Normal':
            self.surface.GetProperty().SetOpacity(0.3)
            self.surface.GetProperty().SetSpecular(0.2)
        else:
            self.surface.GetProperty().SetSpecular(0.7)
        self.surface.GetProperty().SetSpecularPower(40)
        # self.surface.GetProperty().SetDiffuseColor(1, .49, .25)
        self.surface.GetProperty().SetDiffuseColor(self.colors.GetColor3d("SkinColor"))
        self.surface.GetProperty().SetDiffuse(0.7)

        # ###### Volume Rendering
        # volume = vtk.vtkVolume()
        # # Ray cast function know how to render the data
        # # volumeMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
        # volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        # volumeMapper.SetInputConnection(reader.GetOutputPort())
        # volumeMapper.SetBlendModeToMaximumIntensity()

        # # 2. Filter --&gt; Setting the color mapper, Opacity for VolumeProperty
        # s0, sf = reader.GetOutput().GetScalarRange()
        # colorFunc = vtk.vtkColorTransferFunction()
        # colorFunc.SetColorSpaceToHSV()
        # colorFunc.HSVWrapOff()
        # colorFunc.AddRGBPoint(s0, 1, 0, 0)
        # colorFunc.AddRGBPoint(sf, 0, 1, 0)

        # volumeProperty = vtk.vtkVolumeProperty()

        # # The opacity transfer function is used to control the opacity
        # # of different tissue types.
        # # Create transfer mapping scalar value to opacity
        # volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        # volumeScalarOpacity.AddPoint(0, 0.00)
        # volumeScalarOpacity.AddPoint(500, 0.55)
        # volumeScalarOpacity.AddPoint(800, 0.75)
        # volumeScalarOpacity.AddPoint(1000, 0.75)
        # volumeScalarOpacity.AddPoint(1150, 0.85)

        # # set the color for volumes
        # volumeProperty.SetColor(colorFunc)
        # # To add black as background of Volume
        # volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        # volumeProperty.SetInterpolationTypeToLinear()
        # volumeProperty.SetIndependentComponents(2)

        # volumeProperty.ShadeOn()
        # volumeProperty.SetAmbient(0.4)
        # volumeProperty.SetDiffuse(0.6)
        # volumeProperty.SetSpecular(0.2)

        # volume.SetMapper(volumeMapper)
        # volume.SetProperty(volumeProperty)
    
        # ############


        # Camera
        cam = vtk.vtkOpenGLCamera()
        # self.cam.SetViewUp(0,-1,0) # the camera Y axis points down
        # self.cam.SetPosition(0, 0, 0)
        # self.cam.SetFocalPoint(0, 0, 1) # look in the +Z direction of the camera coordinate system
        cam.SetFocalPoint(0, 0, 0)
        cam.ComputeViewPlaneNormal()

        # if self.viewType == 'Virtual':
        #     cam.SetViewUp(0, -1, 0)
        #     cam.SetPosition(0, 0, 1)
        # else:
        #     cam.SetViewUp(0, 1, 0)
        #     cam.SetPosition(0, -5, 1)


        self.ren.AddActor(self.surface)
        # self.ren.AddActor(volume)

        self.ren.SetActiveCamera(cam)
        self.ren.ResetCamera()
        cam.Zoom(1.5)
        cam.Dolly(1.5)
        self.ren.ResetCameraClippingRange()

        self.show_orientation_widget()

        self.initCamViewUp = self.ren.GetActiveCamera().GetViewUp()
        self.initCamPosition = self.ren.GetActiveCamera().GetPosition()
        self.initCamFocalPoint = self.ren.GetActiveCamera().GetFocalPoint()

        self.interactor.Initialize()

    def show_orientation_widget(self):
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
        readerH.SetFileName('ui\\Human.vtp')
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

    def update_text_actor(self):
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

    def set_camera(self, cam_pos):
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

    def register(self, pt_tracker):
        ### Decimate points for registration
        self.surfaceExtractor.Update()
        inputPolyData = self.surfaceExtractor.GetOutput()

        # print(inputPolyData.GetNumberOfPoints())
        # print(inputPolyData.GetNumberOfPolys())

        deci = vtk.vtkDecimatePro()
        deci.SetInputData(inputPolyData)
        deci.SetTargetReduction(0.9)
        deci.PreserveTopologyOn()
        deci.Update()

        deciPol = vtk.vtkPolyData()
        deciPol.ShallowCopy(deci.GetOutput())
        # print(deciPol.GetNumberOfPoints())
        # print(deciPol.GetNumberOfPolys())

        pt_ct = vtk_to_numpy(deciPol.GetPoints().GetData())

        from pycpd import rigid_registration
        reg = rigid_registration(**{ 'X': pt_tracker, 'Y':pt_ct })
        reg.register()
        print(reg.R)
        print(reg.t)

        # reg_mat = np.array([[RR[0][0], RR[0][1], RR[0][2], tt[0]],
        #                     [RR[1][0], RR[1][1], RR[1][2], tt[1]],
        #                     [RR[2][0], RR[2][1], RR[2][2], tt[2]],
        #                     [0       , 0       , 0       , 1]])

        reg_mat = np.array([[RR[0][0], RR[0][1], RR[0][2], 0],
                            [RR[1][0], RR[1][1], RR[1][2], 0],
                            [RR[2][0], RR[2][1], RR[2][2], 0],
                            [tt[0]   , tt[1]   , tt[2]   , 1]])
        reg_mat = np.transpose(reg_mat)

        # R R R 0
        # R R R 0
        # R R R 0
        # t t t 1
        # then transpose
        return reg_mat

    def draw_points(self, points):
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
    
    def remove_points(self):
        if self.points == None:
            return
        self.ren.RemoveActor(self.points)
        self.ren.RemoveActor(self.startPoint)
        self.ren.RemoveActor(self.endPoint)
        self.interactor.ReInitialize()
        self.points = None
        self.startPoint = None
        self.endPoint = None
    
    def add_start_point(self, pos, color=[0,1,0]):
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
    
    def add_end_point(self, pos, color=[1,0,0]):
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

    def setThreshold(self, value):
        self.surfaceExtractor.SetValue(0, value)
        self.ren.Render()
        self.interactor.ReInitialize()


