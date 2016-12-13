from util import * 
import matplotlib.cm
import vtk
import math

############################################################################
### VTK functions 
############################################################################
def block_generation(cen_size, color):
    """ generate a block up to actor stage
        User may choose to use VTK boxsource implementation, or the polydata implementation
    """
    cubeMapper = vtk.vtkPolyDataMapper()
    cubeActor = vtk.vtkActor()

    lx,ly,lz,hx,hy,hz = blocktrans_cen2side(cen_size)
    vertices = [ [lx,ly,lz], [hx,ly,lz], [hx,hy,lz], [lx,hy,lz],
    [lx,ly,hz], [hx,ly,hz], [hx,hy,hz], [lx,hy,hz]]

    pts =[[0,1,2,3], [4,5,6,7], [0,1,5,4],
    [1,2,6,5], [2,3,7,6], [3,0,4,7]]

    cube = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()

    for i in xrange(0,8):
      points.InsertPoint(i,vertices[i])

    for i in xrange(0,6):
      polys.InsertNextCell(4)
      for j in xrange(0,4):
        polys.InsertCellPoint(pts[i][j])
    cube.SetPoints(points)
    cube.SetPolys(polys)
    cubeMapper.SetInput(cube)
    cubeActor.SetMapper(cubeMapper)

    # set the colors
    cubeActor.GetProperty().SetColor(np.array(color[:3]))
    cubeActor.GetProperty().SetAmbient(0.5)
    cubeActor.GetProperty().SetDiffuse(.5)
    cubeActor.GetProperty().SetSpecular(0.1)
    cubeActor.GetProperty().SetSpecularColor(1,1,1)
    cubeActor.GetProperty().SetDiffuseColor(color[:3])
    # cubeActor.GetProperty().SetAmbientColor(1,1,1)
    # cubeActor.GetProperty().ShadingOn()
    return cubeActor

def generate_all_blocks(voxels, threshold=0.1, uniform_size=-1, use_colormap=False):
    """
    Generate one block per voxel, with block size and color dependent on probability. 
    Performance is desirable if number of blocks is below 20,000. 
    """
    assert voxels.ndim == 3
    actors = []
    counter = 0
    dims = voxels.shape

    cmap = matplotlib.cm.get_cmap('jet')
    DEFAULT_COLOR = [0.9,0,0]

    for k in xrange(dims[2]):
        for j in xrange(dims[1]):
            for i in xrange(dims[0]):
                    occupancy = voxels[i][j][k]
                    if occupancy < threshold:
                        continue

                    if use_colormap:
                        color = cmap(float(occupancy))
                    else:    # use default color
                        color = DEFAULT_COLOR

                    if uniform_size > 0 and uniform_size <= 1:
                        block_size = uniform_size
                    else:
                        block_size = occupancy
                    actors.append(block_generation([i+0.5, j+0.5, k+0.5, block_size, block_size, block_size], color=(color)))
                    counter = counter + 1

    print counter, "blocks filled"
    return actors

def display(actors, cam_pos, cam_vocal, cam_up, title=None):
    """ Display the scene from actors. 
    cam_pos: list of positions of cameras. 
    cam_vocal: vocal point of cameras
    cam_up: view up direction of cameras
    title: display window title
    """

    renWin = vtk.vtkRenderWindow()
    window_size = 1024

    renderer = vtk.vtkRenderer()
    for actor in actors:
        renderer.AddActor(actor)
    renderer.SetBackground(1,1,1)
    renWin.AddRenderer(renderer)

    camera = vtk.vtkCamera()
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()

    # the object is located at 0 <= x,y,z <= dims[i]
    camera.SetFocalPoint(*cam_vocal)
    camera.SetViewUp(*cam_up)
    camera.SetPosition(*cam_pos)
    
    renWin.SetSize(window_size, window_size)

    iren = vtk.vtkRenderWindowInteractor()
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)
    iren.SetRenderWindow(renWin)
    if title != None:
        renWin.SetWindowName(title)

    renderer.ResetCameraClippingRange()
    renWin.Render()

    iren.Initialize()
    iren.Start()

def visualization(voxels, threshold, title=None, uniform_size=-1, use_colormap=False):
    """
    Given a voxel matrix, plot all occupied blocks (defined by voxels[x][y][z] > threshold)
    if size_change is set to true, block size will be proportional to voxels[x][y][z]
    otherwise voxel matrix is transfered to {0,1} matrix, where consecutive blocks are merged for performance.

    The function saves an image at address ofilename, with form jpg/png. If form is empty string, no image is saved.

    """
    actors = generate_all_blocks(voxels, threshold, uniform_size=uniform_size, use_colormap=use_colormap)

    center = center_of_mass(voxels)
    dims = voxels.shape
    distance = voxels.shape[0] * 2.8
    height = voxels.shape[2] * 0.85
    rad = math.pi * 0.43 #+ math.pi
    cam_pos = [center[0] + distance * math.cos(rad), center[1] + distance * math.sin(rad), center[2] + height]

    display(actors, cam_pos, center, (0,0,1), title=title)