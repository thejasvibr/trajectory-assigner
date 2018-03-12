# -*- coding: utf-8 -*-
""" Fooling around with point selection in a 3d plot in matplotlib

Created on Wed Mar 07 16:32:56 2018

@author: tbeleyur
"""
import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd

init_data = np.random.normal(0,1,150).reshape((-1,3))

fig = plt.figure()
a0 = plt.subplot(111,projection='3d')
a0.scatter(init_data[:,0],init_data[:,1],init_data[:,2],'*')



xyz = np.random.normal(0,1,120).reshape((-1,3))

df_data = pd.DataFrame(data=xyz,columns=['x','y','z'])
df_data['use_for_bft'] = True


def update():
    data2plot = df_data[df_data['use_for_bft']==True]

    a0.plot(data2plot['x'],data2plot['y'],data2plot['z'],'*')

def onpick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

def onpick3(event):
    ind = event.ind[0]
    x, y, z = event.artist._offsets3d
    print( x[ind], y[ind], z[ind])


fig.canvas.mpl_connect('pick_event', onpick3)
