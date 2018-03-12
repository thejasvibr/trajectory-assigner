# -*- coding: utf-8 -*-
""" creates GUI that loads a dataset and plots the 3d plot.
Created on Fri Mar 09 14:22:41 2018

@author: tbeleyur
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
plt.switch_backend('Qt4Agg')
from matplotlib.widgets import Button,  CheckButtons, TextBox
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d


t= np.linspace(0,1,100)
dataxyz = {'x':t,'y':np.sin(2*np.pi*0.5*t),
               'z':np.random.normal(1.5,0.1,t.size),'t':t
               ,'x_knwn': t+np.random.normal(0,0.5,t.size)
               ,'y_knwn': np.sin(2*np.pi*0.6*t),
                'z_knwn':np.random.normal(2.5,0.1,t.size),
                'traj_num':np.concatenate((np.tile(1,25),np.tile(2,25),
                                           np.tile(3,25),np.tile(4,25)
                                           )),
                                           't':t}
data = pd.DataFrame(data=dataxyz)

plt.figure()
a0 = plt.subplot(111,projection='3d')

all_trajs = []
unique_trajs = data['traj_num'].dropna().unique()

for each_traj in unique_trajs:
    subset_data = data[data['traj_num']==int(each_traj)]
    subset_data = subset_data.reset_index(drop=True)
    L, = a0.plot(subset_data['x'],subset_data['y'],
                              subset_data['z'], '-*', visible=True)
    all_trajs.append( L )
  
    
def func(label):
    
    
    if label=='1':
        print('Hey')
        all_trajs[0].set_visible(not all_trajs[0].get_visible())
    elif label=='2':
        all_trajs[1].set_visible(not all_trajs[1].get_visible())        
    elif label=='3':
        all_trajs[2].set_visible(not all_trajs[2].get_visible())
        
        
        
        


def plot_this_traj(chosen_trajnum):
    '''
    '''
    print(chosen_trajnum)
    subset_data = data[data['traj_num']==int(chosen_trajnum)]
    subset_data = subset_data.reset_index(drop=True)
    print(subset_data.head())
    a0.plot(subset_data['x'],subset_data['y'],subset_data['z'], '-*')
    plt.draw()


axcolor = 'lightgoldenrodyellow'
rax = plt.axes([0.0, 0.5, 0.1, 0.45], facecolor=axcolor)
rax_labels = data['traj_num'].unique()
checkbox = CheckButtons(rax, rax_labels,np.tile(True,rax_labels.size))


checkbox.on_clicked(func)


def submit(text):
    a0.plot(np.random.normal(0,1,10),np.random.normal(0,1,10),
            np.random.normal(0,1,10), '-*')
    

axbox = plt.axes([0.1, 0.05, 0.105, 0.055])
axbox2 = plt.axes([0.2, 0.05, 0.25, 0.055])

text_box = TextBox(axbox, 'Time', initial='0')
text_box.on_submit(submit)
text_box2 = TextBox(axbox2, '', initial='1')
text_box2.on_submit(submit)


ax_xlims_minbox = plt.axes([0.008, 0.3, 0.02, 0.25])
ax_xlims_maxbox =  plt.axes([0.03, 0.3, 0.035, 0.25])
xlims_minbox = TextBox(ax_xlims_minbox, 'X', initial='0')
xlims_maxbox = TextBox(ax_xlims_maxbox, '', initial='9')

ax_ylims_minbox = plt.axes([0.008, 0.2, 0.02, 0.15])
ax_ylims_maxbox =  plt.axes([0.03, 0.2, 0.035, 0.15])
ylims_minbox = TextBox(ax_ylims_minbox, 'Y', initial='0')
ylims_maxbox = TextBox(ax_ylims_maxbox, '', initial='9')


ax_zlims_minbox = plt.axes([0.008, 0.1, 0.02, 0.05])
ax_zlims_maxbox =  plt.axes([0.03, 0.1, 0.035, 0.05])
zlims_minbox = TextBox(ax_zlims_minbox, 'Z', initial='0')
zlims_maxbox = TextBox(ax_zlims_maxbox, '', initial='9')

plt.show()

