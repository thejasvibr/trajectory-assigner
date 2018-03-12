# -*- coding: utf-8 -*-
"""
https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
@author: StackOverflow, DonCristobal
"""

import matplotlib.pyplot as plt, numpy as np
from mpl_toolkits.mplot3d import proj3d

def visualize3DData (X):
    """Visualize data in 3d plot with popover next to mouse position.

    Args:
        X (np.array) - array of points, of shape (numPoints, 3)
    Returns:
        None
    """
    fig = plt.figure(figsize = (16,10))
    ax = fig.add_subplot(111, projection = '3d')
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], depthshade = False, picker = True)
    return(fig)


def distance(point, event):
    """Return distance between mouse position and given data point

    Args:
        point (np.array): np.array of shape (3,), with x,y,z in data coords
        event (MouseEvent): mouse event (which contains mouse position in .x and .xdata)
    Returns:
        distance (np.float64): distance (in screen coords) between mouse pos and data point
    """
    assert point.shape == (3,), "distance: point.shape is wrong: %s, must be (3,)" % point.shape

    # Project 3d data space to 2d data space
    x2, y2, _ = proj3d.proj_transform(point[0], point[1], point[2], plt.gca().get_proj())
    # Convert 2d data space to 2d screen space
    x3, y3 = ax.transData.transform((x2, y2))

    return np.sqrt ((x3 - event.x)**2 + (y3 - event.y)**2)


def calcClosestDatapoint(X, event):
    """"Calculate which data point is closest to the mouse position.

    Args:
        X (np.array) - array of points, of shape (numPoints, 3)
        event (MouseEvent) - mouse event (containing mouse position)
    Returns:
        smallestIndex (int) - the index (into the array of points X) of the element closest to the mouse position
    """
    distances = [distance (X[i, 0:3], event) for i in range(X.shape[0])]
    return np.argmin(distances)


def annotatePlot(X, index):
    """Create popover label in 3d chart

    Args:
        X (np.array) - array of points, of shape (numPoints, 3)
        index (int) - index (into points array X) of item which should be printed
    Returns:
        None
    """
    # If we have previously displayed another label, remove it first
    if hasattr(annotatePlot, 'label'):
        annotatePlot.label.remove()
    # Get data point from array of points X, at position index
    x2, y2, _ = proj3d.proj_transform(X[index, 0], X[index, 1], X[index, 2], ax.get_proj())
    annotatePlot.label = plt.annotate( "Value %d" % index,
        xy = (x2, y2), xytext = (-20, 20), textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
    fig.canvas.draw()


def onMouseMotion(event):
    """Event that is triggered when mouse is moved. Shows text annotation over data point closest to mouse."""
    closestIndex = calcClosestDatapoint(X, event)
    annotatePlot (X, closestIndex)




if __name__ == '__main__':
    X = np.random.random((30,3))
    visualize3DData (X)

    fig.canvas.mpl_connect('motion_notify_event', onMouseMotion)  # on mouse motion
    plt.show()