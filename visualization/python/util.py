import numpy as np
import math
import os
from scipy import ndimage
from scipy.io import loadmat

def read_tensor(filename, varname='voxels'):
    """ return a 4D matrix, with dimensions point, x, y, z """
    assert(filename[-4:] == '.mat')
    mats = loadmat(filename)
    if varname not in mats:
        print ".mat file only has these matrices:",
        for var in mats: 
            print var,
        assert(False)

    voxels = mats[varname]
    dims = voxels.shape
    if len(dims) == 5:
        assert dims[1] == 1
        dims = (dims[0],) + tuple(dims[2:])
    elif len(dims) == 3:
        dims = (1) + dims
    else:
        assert len(dims) == 4    
    result = np.reshape(voxels, dims)
    return result

def sigmoid(z, offset=0, ratio=1):
    s = 1.0 / (1.0 + np.exp(-1.0 * (z-offset) * ratio))
    return s
    
############################################################################
### Voxel Utility functions 
############################################################################
def blocktrans_cen2side(cen_size):
    """ Convert from center rep to side rep
    In center rep, the 6 numbers are center coordinates, then size in 3 dims
    In side rep, the 6 numbers are lower x, y, z, then higher x, y, z """
    cx = float(cen_size[0])
    cy = float(cen_size[1])
    cz = float(cen_size[2])
    sx = float(cen_size[3])
    sy = float(cen_size[4])
    sz = float(cen_size[5])
    lx,ly,lz = cx-sx/2., cy-sy/2., cz-sz/2.
    hx,hy,hz = cx+sx/2., cy+sy/2., cz+sz/2.
    return [lx,ly,lz,hx,hy,hz]

def blocktrans_side2cen6(side_size):
    """ Convert from side rep to center rep
    In center rep, the 6 numbers are center coordinates, then size in 3 dims
    In side rep, the 6 numbers are lower x, y, z, then higher x, y, z """
    lx,ly,lz = float(side_size[0]), float(side_size[1]), float(side_size[2])
    hx,hy,hz = float(side_size[3]), float(side_size[4]), float(side_size[5])
    return [(lx+hx)*.5,(ly+hy)*.5,(lz+hz)*.5,abs(hx-lx),abs(hy-ly),abs(hz-lz)]


def center_of_mass(voxels, threshold=0.1):
    """ Calculate the center of mass for the current object. 
    Voxels with occupancy less than threshold are ignored
    """
    assert voxels.ndim == 3
    center = [0]*3
    voxels_filtered = np.copy(voxels)
    voxels_filtered[voxels_filtered < threshold] = 0

    total = voxels_filtered.sum()
    if total == 0:
        print 'threshold too high for current object.'
        return [length / 2 for length in voxels.shape]   
    
    # calculate center of mass
    center[0] = np.multiply(voxels_filtered.sum(1).sum(1), np.arange(voxels.shape[0])).sum()/total
    center[1] = np.multiply(voxels_filtered.sum(0).sum(1), np.arange(voxels.shape[1])).sum()/total
    center[2] = np.multiply(voxels_filtered.sum(0).sum(0), np.arange(voxels.shape[2])).sum()/total

    return center

def downsample(voxels, step, method='max'):
    """
    downsample a voxels matrix by a factor of step. 
    downsample method options: max/mean 
    same as a pooling
    """
    assert step > 0
    assert voxels.ndim == 3 or voxels.ndim == 4
    assert method in ('max', 'mean')
    if step == 1:
        return voxels

    if voxels.ndim == 3:
        sx, sy, sz = voxels.shape[-3:]
        X, Y, Z = np.ogrid[0:sx, 0:sy, 0:sz]
        regions = sz/step * sy/step * (X/step) + sz/step * (Y/step) + Z/step
        if method == 'max':
            res = ndimage.maximum(voxels, labels=regions, index=np.arange(regions.max() + 1))
        elif method == 'mean':
            res = ndimage.mean(voxels, labels=regions, index=np.arange(regions.max() + 1))
        res.shape = (sx/step, sy/step, sz/step)
        return res
    else:
        res0 = downsample(voxels[0], step, method)
        res = np.zeros((voxels.shape[0],) + res0.shape)
        res[0] = res0
        for ind in xrange(1, voxels.shape[0]):
            res[ind] = downsample(voxels[ind], step, method)
        return res

def max_connected(voxels, distance):
    """ Keep the max connected component of the voxels (a boolean matrix). 
    distance is the distance considered as neighbors, i.e. if distance = 2, 
    then two blocks are considered connected even with a hole in between"""
    assert(distance > 0)
    max_component = np.zeros(voxels.shape, dtype=bool)
    voxels = np.copy(voxels)
    for startx in xrange(voxels.shape[0]):
        for starty in xrange(voxels.shape[1]):
            for startz in xrange(voxels.shape[2]):
                if not voxels[startx,starty,startz]:
                    continue
                # start a new component
                component = np.zeros(voxels.shape, dtype=bool)
                stack = [[startx,starty,startz]]
                component[startx,starty,startz] = True
                voxels[startx,starty,startz] = False
                while len(stack) > 0:
                    x,y,z = stack.pop()
                    for i in xrange(x-distance, x+distance + 1):
                        for j in xrange(y-distance, y+distance + 1):
                            for k in xrange(z-distance, z+distance + 1):
                                if (i-x)**2+(j-y)**2+(k-z)**2 > distance * distance:
                                    continue
                                if voxel_exist(voxels, i,j,k):
                                    voxels[i,j,k] = False
                                    component[i,j,k] = True
                                    stack.append([i,j,k])
                if component.sum() > max_component.sum():
                    max_component = component
    return max_component 


def voxel_exist(voxels, x,y,z):
    if x < 0 or y < 0 or z < 0 or x >= voxels.shape[0] or y >= voxels.shape[1] or z >= voxels.shape[2]:
        return False
    else :
        return voxels[x,y,z]
