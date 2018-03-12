# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 17:02:08 2018

@author: tbeleyur
"""
import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fig =plt.figure()
ax = plt.subplot(111,projection='3d')
xyz = np.random.rand(120).reshape((-1,3))
ax.scatter(xyz[:,0],xyz[:,1],xyz[:,2])

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y,event.z, event.xdata, event.ydata))
    print(event._offset)

def onpick3(event):
    x, y, z = event.artist._offsets3d
    print (x, y, z)


cid = fig.canvas.mpl_connect('button_press_event', onpick3)