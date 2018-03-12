# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 11:54:14 2018

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
import sys
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = stdout

class traj_cleaner():
    
    def __init__(self,dataset,a0):
        self.dataset = dataset
        self.a0 = a0
        self.traj_time_subset = []
        self.shown_trajs = []
        self.starttime = 0.0
        self.endtime = 0.01
                        
        try:
            self.trajectories = dataset['traj_num'].dropna().unique()
        except:
            raise ValueError('Could not extract values from traj_num found \
                             column')            
            
        self.disp_trajs = { str(each_traj) : True  for each_traj in self.trajectories   }
        
        self.disp_data = dataset.copy()
                       
        self.knwn_trajs = {}
        self.assigned_trajs = {}
        
        self.initiate_plot()   
                
       
            
    def initiate_plot(self):       
        
        self.a0.plot(self.disp_data['x_knwn'],self.disp_data['y_knwn'],
                     self.disp_data['z_knwn'],'-*')
        
        self.a0.plot(self.disp_data['x'],self.disp_data['y'],
                     self.disp_data['z'],'^')
    
    
    def update_starttime(self, user_input):
        '''
        '''
        self.starttime = float(user_input)  
        self.update_displayplot(True)
        
               
    def update_endtime(self, user_input):
        
        self.endtime = float(user_input)   
        self.update_displayplot(True)
        
        
        
    def update_vistraj(self, user_input):        

        self.disp_trajs[user_input] = not self.disp_trajs[user_input]     
        self.update_displayplot(True)
        
        
    
    def update_displayplot(self, user_input):  
        self.a0.cla()           
        
        # choose all trajectories to be shown : 
        try:
            self.shown_trajs = [float(key) for key, value in self.disp_trajs.iteritems() if value ]
            self.traj_subset = self.disp_data[self.disp_data['traj_num'].isin(self.shown_trajs)]
            
            # choose the timerange within which these trajectories are to be shown:
            
            
            self.traj_time_subset = self.traj_subset[(self.traj_subset['t'] >= self.starttime) &
                                                     (self.traj_subset['t'] <= self.endtime) ]
        except:
            self.a0.set_title('IMPROPER DATA RANGE')                
         
       

#        # make the plot : 
        for each_traj in self.traj_time_subset['traj_num'].unique():
            
            self.each_traj_data = self.traj_time_subset[self.traj_time_subset['traj_num']==each_traj]
            self.each_traj_data = self.each_traj_data.dropna().reset_index(drop=True)
            
            self.a0.plot(self.each_traj_data['x_knwn'],
                                 self.each_traj_data['y_knwn'],
                                 self.each_traj_data['z_knwn'],'-*',
                                 label=str(each_traj)) 
            
            
            self.a0.plot(self.each_traj_data['x'],
                                 self.each_traj_data['y'],
                                 self.each_traj_data['z'],'*',
                                                         label=str(each_traj))
        
        plt.show()    
        self.a0.legend()
        
        
            
        
fig = plt.figure(1,figsize=(8,8))   
a5 =  plt.subplot(111,projection='3d')
 
axcolor = 'lightgoldenrodyellow'
rax = plt.axes([0.0, 0.5, 0.1, 0.45], facecolor=axcolor)
     

timebox_start = plt.axes([0.1, 0.05, 0.105, 0.055])
timestart_textbox = TextBox(timebox_start, 'Time range', initial='0')
timebox_end = plt.axes([0.15, 0.05, 0.12, 0.055])





if __name__ =='__main__':
    
    dx_knwn  = np.linspace(-1,1,100)
    dx_uknwn = dx_knwn + 0.1
    
    dy_knwn = np.sin(2*np.pi*dx_knwn*0.5)
    dy_ukwn = dy_knwn + np.random.normal(0,0.1,dy_knwn.size)
    
    dz_knwn = np.random.normal(0,0.2,dx_knwn.size)
    dz_ukwn = dz_knwn + 0.05
    
    
    d = np.column_stack((dx_knwn,dx_uknwn, dy_knwn, dy_ukwn, dz_knwn, dz_ukwn))
    t = np.linspace(0,1,d.shape[0])
    trajs = np.concatenate((np.tile(1,25),np.tile(2,25),np.tile(3,25),
                                                    np.tile(4,25)))
    traj_data = pd.DataFrame(data=np.column_stack((d,t)))
    traj_data.columns = ['x','x_knwn','y','y_knwn','z','z_knwn','t']
    traj_data['traj_num'] = trajs
    
    
    actual_data = pd.read_csv('example_assigned_traj_P14_27000_multibat_380frames.csv')
    A = traj_cleaner(actual_data,a5)
    
    rax_labels = A.disp_data['traj_num'].dropna().unique()
    checkbox = CheckButtons(rax, rax_labels,np.tile(True,rax_labels.size))
    
    timeend_textbox = TextBox(timebox_end, '', initial=str(max(A.disp_data['t'])))
    
    timestart_textbox.on_submit(A.update_starttime)
    timeend_textbox.on_submit(A.update_endtime)
    
    checkbox.on_clicked(A.update_vistraj)
    
    axnext = plt.axes([0.7, 0.05, 0.1, 0.075])
    update_button = Button(axnext, 'Update')
    update_button.on_clicked(A.update_displayplot)


    
    


    
    
    
    
        
    
    
    
        
        