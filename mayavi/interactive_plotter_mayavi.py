# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 16:48:13 2018

@author: tbeleyur
"""
import easygui as eg
from mayavi import mlab
import numpy as np
import pandas as pd

  
figure = mlab.gcf()
mlab.clf()
figure.scene.disable_render = True
#open_file = eg.fileopenbox(msg='Select the traj file')
#try:
folder = 'C:\\Users\\tbeleyur\\Documents\\figuring_out\\interactive_plotting\\mayavi\\' 
raw_data = pd.read_csv(folder + 'example_assigned_traj_P14_27000_multibat_380frames.csv')
#except:
#    raise ValueError(open_file + 'Could not be opened..')
disp_data = raw_data.copy()

traj_2_color = {1:(0,0,0.9),2:(0,0.9,0),3:(0.9,0,0),4:(0,0.9,0.9)}

def assign_colors (X):
    '''
    '''
    try:
        color = traj_2_color[X]
        return(color)
    except:
        color = (0.21,0.21,0.21)
        
        return(color)
        
def conv_to_XYZ(pd_df):
    '''
    Parameters:
        pd_df : npoints x 3 columns with some kind of xyz data
        
    Returns:
        x,y,z : 3 columns of npoints length each
    '''
    
    xyz_dict = {}
    
    for i,axis in enumerate(['x','y','z']):
        print(axis)
        
        xyz_dict[axis] = np.array(pd_df.iloc[:,i])
    
    return(xyz_dict['x'],xyz_dict['y'],xyz_dict['z'])
        
        
        


def make_knwnplot(traj_data):
    '''Makes a line plot for each of the known trajectories 
    
    TODO:
        1) make sure the np.nan points in traj_num are being plotted ! 
        2) 
    
    traj_data : pd.DataFrame with following columns;
    
        x,y,z :
        
        x_knwn,y_knwn,z_knwn
        
        t 
        
        t_knwn
        
    '''
    
          
    unique_trajs = traj_data['traj_num'].unique()
    
    
    for each_traj in unique_trajs:
        print(each_traj)
        one_traj = traj_data[traj_data['traj_num'] == each_traj] 
            
        x_knwn,y_knwn,z_knwn = conv_to_XYZ(one_traj[['x_knwn','y_knwn','z_knwn']])
        x,y,z = conv_to_XYZ(one_traj[['x','y','z']])
        
        # verified points 
        known_glyphs = mlab.points3d(x_knwn,y_knwn,z_knwn, 
                                 color = assign_colors(each_traj),
                                 scale_factor = 0.05,
                                 opacity=0.6)
        
        #auto/manually labelled points which need to be checked
        labld_glyphs = mlab.points3d(x,y,z, color = assign_colors(each_traj),
                                   scale_factor = 0.1,
                                  mode='cube', opacity = 0.5)
        
        labld_points = labld_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()

    
    return(known_glyphs, labld_glyphs, labld_points)



known_glyphs, labld_glyphs, labld_points = make_knwnplot(disp_data)

outline = mlab.outline(line_width=3)
outline.outline_mode = 'cornered'
x, y, z = conv_to_XYZ(raw_data[['x','y','z']].dropna())
x_lab, y_lab, z_lab = conv_to_XYZ(raw_data[['x_knwn','y_knwn','z_knwn']])

outline.bounds = (x[0]-0.1, x[0]+0.1,
                  y[0]-0.1, y[0]+0.1,
                  z[0]-0.1, z[0]+0.1)
    
figure.scene.disable_render = False


def picker_callback(picker):
    """ Picker callback: this get called when on pick events.
    """
    click_text = mlab.text(0.6,0.6,'clicked')
    
    if picker.actor in labld_glyphs.actor.actors:
        # Find which data point corresponds to the point picked:
        # we have to account for the fact that each data point is
        # represented by a glyph with several points
        point_id = picker.point_id/labld_points.shape[0]
        # If the no points have been selected, we have '-1'
        if point_id != -1:
            # Retrieve the coordinnates coorresponding to that data
            # point
            x, y, z = x_lab[point_id], y_lab[point_id], z_lab[point_id]
            # Move the outline to the data point.
            outline.bounds = (x-0.1, x+0.1,
                              y-0.1, y+0.1,
                              z-0.1, z+0.1)
            
    click_text.text = str(np.random.choice([0,1,2],1)) 

picker = figure.on_mouse_pick(picker_callback)

# Decrease the tolerance, so that we can more easily select a precise
# point.
picker.tolerance = 0.001



mlab.title('Click on squares')

mlab.show()


