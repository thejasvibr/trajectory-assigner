# -*- coding: utf-8 -*-
"""
https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot

@author: StackOverflow, RAfael J
"""

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d

def main():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')
    points = np.array([(1,1,1), (2,2,2)])
    labels = ['billy', 'bobby']
    plotlabels = []
    xs, ys, zs = np.split(points, 3, axis=1)
    sc = ax.scatter(xs,ys,zs)

    for txt, x, y, z in zip(labels, xs, ys, zs):
        x2, y2, _ = proj3d.proj_transform(x,y,z, ax.get_proj())
        label = plt.annotate(
            txt, xy = (x2, y2), xytext = (-20, 20),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '-', connectionstyle = 'arc3,rad=0'))
        plotlabels.append(label)
    fig.canvas.mpl_connect('motion_notify_event', lambda event: update_position(event,fig,ax,zip(plotlabels, xs, ys, zs)))
    plt.show()


def update_position(e,fig,ax,labels_and_points):
    for label, x, y, z in labels_and_points:
        x2, y2, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
        label.xy = x2,y2
        label.update_positions(fig.canvas.renderer)
    fig.canvas.draw()



if __name__ == '__main__':
    main()