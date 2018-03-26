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

traj_2_color_triplet = {1:(0,0,0.9),2:(0,0.9,0),3:(0.9,0,0),4:(0,0.9,0.9)}
start_col = 0.1
traj_2_color_float = {  i+1:(i+0.5)/10.0    for i in range(9)    }
        
def assign_colors_float(X):
    '''Outputs a float value between 0 and 1 
    at 
    '''
    try:
        color = traj_2_color_float[X]
        return(color)
    except:
        color = 0.01
        return(color)

def assign_colors_triplet(X):
    '''Outputs a float value between 0 and 1 
    at 
    '''
    try:
        color = traj_2_color_triplet[X]
        return(color)
    except:
        color = (0.05,0.05,0.05)
        return(color)
      

def assign_colors(X):
    '''
    '''   
    
    try:
        color = assign_colors_float(X)
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
       
        xyz_dict[axis] = np.array(pd_df.iloc[:,i])
    
    return(xyz_dict['x'],xyz_dict['y'],xyz_dict['z'])
        
        
        


def make_knwnplot(traj_data):
    '''Makes a 3d plot with known/verified trajecotyr points 
    as circles and the corresponding auto/manually labelled points as 
    squares. 
    
    
    TODO:
        1) make sure the np.nan points in traj_num are being plotted ! 
        2) 
    
    traj_data : pd.DataFrame with following columns;
    
        x,y,z :
        
        x_knwn,y_knwn,z_knwn
        
        t 
        
        t_knwn
        
    '''
    
    traj_data['colors'] = traj_data['traj_num'].apply(assign_colors_float,1)
              
    traj_data['size'] = np.tile(0.05,traj_data.shape[0])
      
    glyph_colors = np.array(traj_data['colors'])
    
    #unique_trajs = traj_data['traj_num'].unique()    
    
    
    #print(each_traj)
    #one_traj = traj_data[traj_data['traj_num'] == each_traj] 
        
    x_knwn,y_knwn,z_knwn = conv_to_XYZ(traj_data[['x_knwn','y_knwn','z_knwn']])
    x,y,z = conv_to_XYZ(traj_data[['x','y','z']])
    
    # verified points 
    known_glyphs = mlab.points3d(x_knwn, y_knwn, z_knwn, scale_factor=0.1,
                                 mode='sphere')    
    known_glyphs.glyph.scale_mode = 'scale_by_vector'
    known_glyphs.mlab_source.dataset.point_data.scalars = glyph_colors
    
    #auto/manually labelled points which need to be checked
    labld_glyphs = mlab.points3d(x, y, z, scale_factor=0.1
                                 , mode='cube')
    labld_glyphs.glyph.scale_mode = 'scale_by_vector'
    labld_glyphs.mlab_source.dataset.point_data.scalars = glyph_colors
    
    labld_points = labld_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()
    knwn_points = known_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()
    
    return(known_glyphs, labld_glyphs, labld_points, knwn_points)



known_glyphs, labld_glyphs, labld_points, known_points = make_knwnplot(disp_data)
all_pointsxyz = [known_points, labld_points]
all_glyphs = [ known_glyphs.actor.actors, labld_glyphs.actor.actors]

x, y, z = conv_to_XYZ(raw_data[['x_knwn','y_knwn','z_knwn']])
x_lab, y_lab, z_lab = conv_to_XYZ(raw_data[['x','y','z']])


outline = mlab.outline(line_width=3,color=(0.9,0.9,0.9))
outline.outline_mode = 'cornered'
outline.bounds = (x[0]-0.1, x[0]+0.1,
                  y[0]-0.1, y[0]+0.1,
                 z[0]-0.1, z[0]+0.1)

reassign_outline = mlab.outline(line_width=3,color= (1,1,1))
reassign_outline.bounds = (x[0]-0.1, x[0]+0.1,
                  y[0]-0.1, y[0]+0.1,
                  z[0]-0.1, z[0]+0.1)

    
figure.scene.disable_render = False
click_text = mlab.text(0.6,0.6,' not clicked')
traj_text = mlab.text(0.6,0.7,'Trajectory number')

def picker_labpts_callback(picker):
    """ A square frame appears around either the known or the
    labelled points. 
    """
    click_text.text=''
    
    closest_glyph = [picker.actor in disp_glyphs for disp_glyphs in all_glyphs ]
    
    
    try:
        which_glyph = int(np.argwhere(closest_glyph) )
        print('which_glyph',which_glyph)
        
        points_xyz = all_pointsxyz[which_glyph]
    except:
        return()
    
    
    if picker.actor in all_glyphs[which_glyph]:
       
        print(picker.point_id)
        point_id = picker.point_id/points_xyz.shape[0]
        print('point_id',point_id)
        # If the no points have been selected, we have '-1'
        if point_id != -1:
            # Retrieve the coordinnates coorresponding to that data
            # point
            if which_glyph==0:
                print('known point chosen')
                x_pt, y_pt, z_pt = x[point_id], y[point_id], z[point_id]
                print(x.shape)
            else:
                x_pt, y_pt, z_pt = x_lab[point_id], y_lab[point_id], z_lab[point_id]
                
            # Move the outline to the data point.
            outline.bounds = (x_pt-0.1, x_pt+0.1,
                              y_pt-0.1, y_pt+0.1,
                              z_pt-0.1, z_pt+0.1)
    
            # display the x,y,z and time info on the selected point        
            click_text.text = str([np.around(x_pt,2),
                                       np.around(y_pt,2), np.around(z_pt,2)
                                       , raw_data['t'][point_id]]) 
            # display the trajectory number of the selected point 
            traj_text.text = 'Traj number: ' + str(disp_data['traj_num'][point_id])
    
        
        else:
            print('failed :', point_id)



def reassign_callback(picker):
    """ Picker callback: this get called when on pick events.
    """
    click_text.text=''
    
    
    if picker.actor in labld_glyphs.actor.actors:
        # Find which data point corresponds to the point picked:
        # we have to account for the fact that each data point is
        # represented by a glyph with several points
        print(picker.point_id)
        point_id = picker.point_id/labld_points.shape[0]
        print('point_id',point_id)
        # If the no points have been selected, we have '-1'
        if point_id != -1:
            # Retrieve the coordinnates coorresponding to that data
            # point
            x_pt, y_pt, z_pt = x_lab[point_id], y_lab[point_id], z_lab[point_id]
            # Move the outline to the data point.
            reassign_outline.bounds = (x_pt-0.3, x_pt+0.3,
                              y_pt-0.3, y_pt+0.3,
                              z_pt-0.3, z_pt+0.3)
            
            click_text.text = str([np.around(x_pt,2),
                                       np.around(y_pt,2), np.around(z_pt,2)
                                       , raw_data['t'][point_id]]) 
            try:        
                new_trajnum = eg.integerbox('Please enter the re-assigned trajectory number')
                print('New traj num', new_trajnum)
                # change the trajectory number of the displayed data : 
                disp_data['traj_num'][point_id] = new_trajnum                
               
            except:
                pass
            
        else:
            print('failed :', point_id)
        
        
    return(make_knwnplot(disp_data))



picker = figure.on_mouse_pick(picker_labpts_callback)
picker.tolerance = 0.005


reassign_picker = figure.on_mouse_pick(reassign_callback,
                                       type='point',   button='Right')
reassign_picker.tolerance = 0.01









mlab.xlabel('X')
mlab.title('Click on squares')

mlab.show()


