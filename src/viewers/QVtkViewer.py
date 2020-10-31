import vtk
from PyQt5.QtWidgets import QFrame
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QSurfaceFormat
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np
from abc import abstractmethod

'''
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
'''

class QVTKViewer(QFrame):
    def __init__(self, panel, size, viewType):
        super().__init__(panel)

        QSurfaceFormat.defaultFormat().setProfile(QSurfaceFormat.CompatibilityProfile)
        vtk.qt.QVTKRWIBase = "QGLWidget"
        
        self.viewType = viewType
        self.colors = vtk.vtkNamedColors()
        self.colors.SetColor("SkinColor", [204, 153, 51, 255]) # rgba
        self.colors.SetColor("BkgColor", [51, 77, 102, 255])
        self.axes = vtk.vtkOrientationMarkerWidget()
        # Make the actual QtWidget a child so that it can be reparented
        self.interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.interactor)
        # self.layout.setStretchFactor(self.interactor,1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.width = (size.width()) // 2 - 100
        self.height = (size.height()) // 2 - 50
        self.interactor.setMinimumSize(self.width, self.height)
        self.interactor.setMaximumSize(self.width, self.height)
        self.setLayout(self.layout)

        self.initCamViewUp = (0, 0, 1)
        self.initCamPosition = (0, 1, 0)
        self.initCamFocalPoint = (0, 0, 0)

        self.cross = None
        self.points = None

        self.actor = vtk.vtkImageActor()

        # Setup VTK Environment
        self.ren = vtk.vtkOpenGLRenderer()
        self.interactor.GetRenderWindow().AddRenderer(self.ren)

        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        # interactor = MyInteractorStyle(self)
        # self.interactor.SetInteractorStyle(interactor)
        self.ren.SetBackground(0, 0, 0)
        # ren.SetBackground(colors.GetColor3D("BkgColor"))
        self.interactor.Initialize()

    @abstractmethod
    def show_image(self, reader, *args, **kwargs):
        pass

    def remove_image(self):
        self.ren.RemoveAllViewProps()
        self.ren.ResetCamera()
        self.cross = None

    def create_cross(self, size, is3D=False):
        # Create endpoints
        pts = vtk.vtkPoints()
        pts.InsertNextPoint(-size / 2, 0, 0)
        pts.InsertNextPoint(size / 2, 0, 0)
        pts.InsertNextPoint(0, -size / 2, 0)
        pts.InsertNextPoint(0, size / 2, 0)
        if is3D:
            pts.InsertNextPoint(0, 0, -size / 2)
            pts.InsertNextPoint(0, 0, size / 2)
        
        # Setup the colors array
        color = (0, 170, 170)
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3) # 3=RGB, 4=RGBA
        colors.SetName("Colors")
        # Add the color for the 1st line
        colors.InsertNextValue(color[0])
        colors.InsertNextValue(color[1])
        colors.InsertNextValue(color[2])
        # Add the colors for the 2nd line
        colors.InsertNextValue(color[0])
        colors.InsertNextValue(color[1])
        colors.InsertNextValue(color[2])
        if is3D:
            # Add the colors for the 3rd line
            colors.InsertNextValue(color[0])
            colors.InsertNextValue(color[1])
            colors.InsertNextValue(color[2])

        # Create lines
        line0 = vtk.vtkLine()
        line0.GetPointIds().SetId(0, 0) # (start point, pts[0])
        line0.GetPointIds().SetId(1, 1) # (end point, pts[1])
        line1 = vtk.vtkLine()
        line1.GetPointIds().SetId(0, 2)
        line1.GetPointIds().SetId(1, 3)
        # Create a cell array to store the lines
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(line0)
        lines.InsertNextCell(line1)
        if is3D:
            line2 = vtk.vtkLine()
            line2.GetPointIds().SetId(0, 4)
            line2.GetPointIds().SetId(1, 5)
            lines.InsertNextCell(line2)

        # Create a polydata to store everything in
        linesPolyData = vtk.vtkPolyData()
        # Add the points to the dataset
        linesPolyData.SetPoints(pts)
        # Add the lines to the dataset
        linesPolyData.SetLines(lines)
        # Color the lines
        linesPolyData.GetCellData().SetScalars(colors)
        return linesPolyData

    def remove_cross(self):
        self.ren.RemoveActor(self.cross)
        self.ren.GetRenderWindow().Render()
        self.cross = None

    def set_cross_position(self, x, y, z=1, is3D=False):
            if self.cross == None:
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(self.create_cross(50, is3D))
                self.cross = vtk.vtkActor()
                self.cross.GetProperty().SetLineWidth(2)
                self.cross.SetMapper(mapper)
                self.ren.AddActor(self.cross)
            self.cross.SetPosition(x, y, z)
            self.ren.GetRenderWindow().Render()

    def reset_view(self, is3D):
        self.ren.ResetCamera()

        if is3D:
            self.ren.GetActiveCamera().SetViewUp(self.initCamViewUp)
            self.ren.GetActiveCamera().SetPosition(self.initCamPosition)
            self.ren.GetActiveCamera().SetFocalPoint(self.initCamFocalPoint)
            self.ren.GetActiveCamera().ComputeViewPlaneNormal()
            # self.ren.GetActiveCamera().Dolly(1.5)
            self.ren.ResetCameraClippingRange()
        else:
            self.ren.GetActiveCamera().Zoom(1.5)
            self.actor.GetProperty().SetColorWindow(255)
            self.actor.GetProperty().SetColorLevel(127.5)

        self.interactor.ReInitialize()



        