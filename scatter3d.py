"""
==============
3D Scatterplot of Centerlines
==============
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


def coord2points(coords):
    numPoints = coords.shape[-1]
    # numPoints = len(coords)
    points = np.zeros([numPoints, 3])
    for i in range(numPoints):
        points[i, :] = coords[:, :, i][:, 3][:-1]
    return points


image_cl = 'patients/Patient_3/image_centerline.npy'
tracker_cl = 'patients/Patient_2/tracker_centerline.npy'

cl1 = coord2points(np.load(image_cl))
cl2 = coord2points(np.load(tracker_cl))

fig = plt.figure()
ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(cl1[:, 0], cl1[:, 1], cl1[:, 2], color='red', marker='+')
ax2 = fig.add_subplot(122, projection='3d')
ax2.scatter(cl2[:, 0], cl2[:, 1], cl2[:, 2], color='blue', marker='.')

fig.tight_layout()
plt.show()
