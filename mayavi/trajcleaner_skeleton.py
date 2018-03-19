# -*- coding: utf-8 -*-
"""Trajectory cleaner 

Created on Mon Mar 19 13:17:09 2018

@author: tbeleyur
"""


import numpy as np 
import pandas as pd

from traits.api import HasTraits, Range, Instance, \
        on_trait_change
from traitsui.api import View, Item, Group

from mayavi import mlab
from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, \
                MlabSceneModel



class MyModel(HasTraits):      
    
    Time_range_start = Range(0, 30.0,0.001)#mode='spinner')
    Time_range_end= Range(0, 30.0,2)#mode='spinner')
    scene = Instance(MlabSceneModel, ())   
    
    
    @on_trait_change(['Time_range_start','Time_range_end'])      
    def update_plot(self):
        '''Makes a 3d plot with known/verified trajecotyr points 
        as circles and the corresponding auto/manually labelled points as 
        squares.         
        
        TODO:
            1) make sure the np.nan points in traj_num are being plotted ! 
            2) 
        
        Instance  parameters used : 
            
        knwn_trajdata : pd.DataFrame with following columns:
            x_knwn,y_knwn,z_knwn,t_knwn, traj_num
            
        lab_trajdata : pd.DataFrame with following columns:
            x,y,z,t,traj_num        
              
            
        '''
        print('updating plotted data')
        mlab.clf()

        self.tsubset_knwntraj = self.subset_in_time(self.knwntraj_data)
        self.tsubset_labldtraj = self.subset_in_time(self.labtraj_data,False)
        #print(self.tsubset_knwntraj)
            
        self.x_knwn,self.y_knwn,self.z_knwn = conv_to_XYZ(self.tsubset_knwntraj[['x_knwn','y_knwn','z_knwn']])
        self.x,self.y,self.z = conv_to_XYZ(self.tsubset_labldtraj[['x','y','z']])
        
        # verified points 
        self.known_glyphs = mlab.points3d(self.x_knwn, self.y_knwn, self.z_knwn,
                                     scale_factor=0.05,
                                     mode='sphere', colormap='hsv',
                                     figure=self.fig)    
        self.known_glyphs.glyph.scale_mode = 'scale_by_vector'
        self.known_glyphcolors = np.array(self.tsubset_knwntraj['colors'])
        self.known_glyphs.mlab_source.dataset.point_data.scalars = self.known_glyphcolors
        
        #auto/manually labelled points which need to be checked
        self.labld_glyphs = mlab.points3d(self.x, self.y, self.z,
                                          scale_factor=0.05
                                     , mode='cube', colormap='hsv',
                                     figure=self.fig)
        
        self.labld_glyphs.glyph.scale_mode = 'scale_by_vector'
        self.labld_glyphcolors = np.array(self.tsubset_labldtraj['colors'])
        self.labld_glyphs.mlab_source.dataset.point_data.scalars = np.array(self.labld_glyphcolors)
        
        # get the xyz points of the plotted points 
        self.labld_points = self.labld_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()
        self.knwn_points = self.known_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()
        
   
    
    def subset_in_time(self,traj_df,known=True):
        '''Make a subset of the knwon and labelled trajectory datasets
        such that the points displayed fall wihtin the start and end time
        of the user input.
        
        Parameters:
            
            traj_df : pd.DataFrame with at least one column named either 't'
                        or 't_knwn'
            known : Boolean. Defaults to True.
                    If True:
                        the column used for subsetting should be called 't'
                    If False:
                        the column used for subsetting should be called 't_knwn'
            
        Returns:
            
            tsubset_df : pd.DataFrame with at least one column named 
                        either 't' or 't_knwn'. See 'known'.
                                   
        
        '''
        colname = {True:'t_knwn', False:'t'}
        
        if self.Time_range_end <= self.Time_range_start:
            print('invalid Time range!')
            return(None)
        
        try:
            time_after = traj_df[colname[known]] >= self.Time_range_start
            time_before = traj_df[colname[known]] <= self.Time_range_end
            
            tsubset_df = traj_df[ (time_after) & (time_before ) ]
            
            return(tsubset_df)
        except:
            print('Wrong time ranges !! ')
            pass


        # generate columns with the required information for plotting for 
        # both datasets 
    @on_trait_change('scene.activated')
    def setup(self):
        self.generate_color_and_size()
        self.fig = mlab.figure(figure=self.scene.mayavi_scene)
        self.update_plot()
        
        self.picker = self.fig.on_mouse_pick(self.view_point_information)
        self.picker.tolerance = 0.01
        
        
        
        
    def generate_color_and_size(self):
        for each_trajtype in [self.knwntraj_data, self.labtraj_data]:        
            each_trajtype['colors'] = each_trajtype['traj_num'].apply(assign_colors_float,1)                 
            each_trajtype['size'] = np.tile(0.05,each_trajtype.shape[0])
              
        
    
        self.end_time = np.max([np.max(self.labtraj_data['t']),
                           np.max(self.knwntraj_data['t_knwn'])])
    
    def view_point_information(self,picker):
        '''Callback function when a glyph is left-button clicked. 
        Information on the xyz and time of recording/emission is displayed
        
        '''
        print('MOUSE CALLBACK')
        
        self.click_text = mlab.text(0.8,0.8,'')
        self.outline = mlab.outline(line_width=3,color=(0.9,0.9,0.9),
                                        figure=self.fig)
        self.outline.outline_mode = 'cornered'
        self.outline.visible = False 
        
        all_glyphs = [ self.known_glyphs.actor.actors, 
                                          self.labld_glyphs.actor.actors]
    
        closest_glyph = [picker.actor in disp_glyphs for disp_glyphs in all_glyphs ]
        all_pointsxyz = [self.knwn_points, self.labld_points]
        
        
        try:
            which_glyph = int(np.argwhere(closest_glyph) )
            print('which_glyph',which_glyph)
            
            points_xyz = all_pointsxyz[which_glyph]
        except:
            return()
            
        if which_glyph == 0:
            time_col = 't'
        elif which_glyph == 1:
            time_col = 't_knwn'
        print('time col:', time_col)
        
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
                    x_pt, y_pt, z_pt = self.x_knwn[point_id], self.y_knwn[point_id], self.z_knwn[point_id]
                                                                                                     
                    
                else:
                    x_pt, y_pt, z_pt = self.x[point_id], self.y[point_id],  self.z[point_id]
                    
                # Move the outline to the data point.
                self.outline.bounds = (x_pt-0.05, x_pt+0.05,
                                  y_pt-0.05, y_pt+0.05,
                                  z_pt-0.05, z_pt+0.05)
                self.outline.visible = True
                        
                #display the x,y,z and time info on the selected point #
                print(self.tsubset_knwntraj.head())
                if which_glyph == 1:
                    time_stamp = np.around(self.tsubset_knwntraj[time_col][point_id],6)
                    
                else :
                    time_stamp = np.around(self.tsubset_labldtraj[time_col][point_id],6)
                    
                self.click_text.text = str([np.around(x_pt,2),
                                           np.around(y_pt,2), np.around(z_pt,2)
                                           ,time_stamp ]) 
                 #display the trajectory number of the selected point 
                 #                self.traj_text.text = 'Traj number: ' + str(disp_data['traj_num'][point_id])
            
            
            
         
            else:
                print('failed :', point_id)
            
    
        
    def trajectory_reassignment(self):
        '''Callback function when the user right-clicks on the displayed points
        which triggers a user input box and also performs a change in traject-
        ory number in the original dataset
        '''
        
        
    def identify_orig_rowindex(self):
        '''When a point has been chosen for trajectory re-assignment, 
        find its original row index in the dataset and change the value there
        '''
        
        pass
         
        
    
    # The layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                Group(
                        '_', 'Time_range_start', 'Time_range_end',
                     ),
                resizable=True,
                )


num_colors = 20
traj_2_color_float = {  i+1 : (i+0.5)/num_colors    for i in range(num_colors)    }
         
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
        
        
   
if __name__ == '__main__':
    xyz = np.random.normal(0,1,270).reshape((-1,3))
    txyz = np.column_stack((xyz, np.linspace(0,1.5,xyz.shape[0])))
    kn_data = pd.DataFrame(data=txyz, columns = ['x_knwn','y_knwn',
                                                 'z_knwn','t_knwn'])
    kn_data['traj_num'] = np.tile(1,xyz.shape[0])
    
    some_rows = np.random.choice(range(xyz.shape[0]),15,replace=False)
    xyz_lab = xyz[some_rows,:]
    t_somerows = txyz[some_rows,3]
    txyz_somerows = np.column_stack((xyz_lab,t_somerows))
    lab_data = pd.DataFrame(data=txyz_somerows, columns = ['x','y','z','t'])
    lab_data['traj_num'] = np.concatenate((np.tile(2,7),
                            np.tile(1,8)))
    
    my_model = MyModel()
    my_model.knwntraj_data = kn_data
    my_model.labtraj_data = lab_data
    my_model.configure_traits()
    my_model.setup()    
    
    