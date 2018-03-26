# -*- coding: utf-8 -*-
"""Trajectory cleaner 

Created on Mon Mar 19 13:17:09 2018

@author: tbeleyur
"""

import easygui as eg
import numpy as np 
import pandas as pd

from traits.api import HasTraits, Range, Instance, \
        on_trait_change
from traitsui.api import View, Item, Group

from mayavi import mlab
from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, \
                MlabSceneModel



class TrajCleaner(HasTraits):  
    '''
    TODO : 
        1) Implement recalculation of point colors everytime the 
           timesubsetting occurs !!  
        
        2) Subsetting of displayed points according to trajectory tags ...
            coming in the later future maybe ??
    
    Creates a Mayavi Visualisation window with options to :
        1) Display a time range of the trajectory datasets
        2) View trajectory point information when a point is left-button clicked
        3) Re-assign the *labelled* trajectory points when the point is
            right-button clicked. If 'Cancel' is pressed OR the window is closed
            then the trajectory tag is set to nan. 
    
    Usage : 
        # Initiate a TrajCleaner instance 
        
        traj_cleaner = TrajCleaner()
        
        # assign the labelled and known trajectory datasets to the instance 
        
         traj_cleaner.knwntraj_data = kn_data
         traj_cleaner.labtraj_data = lab_data
         
        # begin the Mayavi interactive visualisation
        
        traj_cleaner.configure_traits()
        
        # After checking the trajectory assignment close the 
        # Mayavi window and save the labld_traj pd.DataFrame to a csv 
        
        traj_cleaner.labld_traj.to_csv('labelled_traj_verified.csv')
        
    User-controlled parameters :
        
        tag_offset : the distance between the numeric trajectory tag and 
                     the displayed trajectory points
        
        tag_size : size of the numeric trajectory tag  
        
        
        
        
    
    '''    
    
    Time_range_start = Range(0, 30.0,0.000)#mode='spinner')
    Time_range_end= Range(0, 30.0,29.99)#mode='spinner')
    scene = Instance(MlabSceneModel, ())   
    
    labld_glyphs = None
    known_glyphs = None
    
    outline = None
    labld_glyphcolors = None 
    
    trajtags= [0,1,2]  # dummy
    tag_size = 0.05
    tag_offset = 2*10**-2
    
    @on_trait_change('scene.activated')
    def setup(self):
        print('running setup')
        self.generate_color_and_size()
        self.fig = mlab.figure(figure=mlab.gcf())
        self.update_plot()
        
        # The general mouse based clicker - which reveals point information
        # of the known and labelled datapoints
        self.info_picker = self.fig.on_mouse_pick(self.view_point_information)
        self.info_picker.tolerance = 0.01
        
        # picker which allows to re-assign the point trajectory number
        self.reassign_picker = self.fig.on_mouse_pick(self.reassign_callback,
                                                      type='point',
                                                      button='Right')
        self.reassign_picker.tolerance = 0.01
        
        # outline which indicates which point has been clicked on
        self.outline = mlab.outline(line_width=3,color=(0.9,0.9,0.9),
                                   )        
        self.outline.outline_mode = 'cornered'
        self.outline.bounds = (0.05, 0.05,
                                  0.05, 0.05,
                                  0.05, 0.05)
        
        
        
        
        
        self.click_text = mlab.text(0.8,0.8,'STARTING INFO')
        self.traj_text = mlab.text(0.8,0.6,'Trajectory number')
        self.pointtype_text = mlab.text(0.8,0.87,'Point Type')
        self.pointtype_info = mlab.text(0.8,0.82,'')
        
        mlab.axes()
    
    @on_trait_change(['Time_range_start','Time_range_end'])      
    def update_plot(self):
        '''Makes a 3d plot with known/verified trajecotyr points 
        as circles and the corresponding auto/manually labelled points as 
        squares.         
        
       TODO:
           1) allow for interactive choosing of points even with tsubsetting - DONE
           2) the POINTCOLORS should remain the same 
        
        Instance  parameters used : 
            
        knwn_trajdata : pd.DataFrame with following columns:
            x_knwn,y_knwn,z_knwn,t_knwn, traj_num
            
        lab_trajdata : pd.DataFrame with following columns:
            x,y,z,t,traj_num        
              
            
        '''
        print('updating plotted data')
        #mlab.gcf().scene.disable_render = True 
        self.tsubset_knwntraj = self.subset_in_time(self.knwntraj_data)
        self.tsubset_labldtraj = self.subset_in_time(self.labtraj_data,False)
        
            
        self.x_knwn,self.y_knwn,self.z_knwn = conv_to_XYZ(self.tsubset_knwntraj[['x_knwn','y_knwn','z_knwn']])
        self.x,self.y,self.z = conv_to_XYZ(self.tsubset_labldtraj[['x','y','z']])
        
        #set colors for each point 
        self.known_glyphcolors = np.array(self.tsubset_knwntraj['colors'])  
        self.labld_glyphcolors = np.array(self.tsubset_labldtraj['colors']) 
   
        # verified points 
        if self.known_glyphs is None:
            # if the glyphs are being called the first time
            self.known_glyphs = mlab.points3d(self.x_knwn, self.y_knwn,
                                              self.z_knwn,
                                     scale_factor=0.05,
                                     mode='sphere', colormap='hsv',
                                     figure=self.fig)  
            # thanks goo.gl/H9mdao
            self.known_glyphs.glyph.scale_mode = 'scale_by_vector'            
            self.known_glyphs.mlab_source.dataset.point_data.scalars = self.known_glyphcolors           
            
        else:
            # only change the traits of the object while keeping its
            # identity in the scene  

            self.known_glyphs.mlab_source.reset(x = self.x_knwn,
                                                y = self.y_knwn,
                                                z = self.z_knwn,
                                                scale_factor=0.05,
                                     mode='sphere', colormap='hsv',
                                     figure=self.fig)
            self.known_glyphs.glyph.scale_mode = 'scale_by_vector'            
            self.known_glyphs.mlab_source.dataset.point_data.scalars = self.known_glyphcolors                   
                        
        #auto/manually labelled points which need to be checked
        if self.labld_glyphs is None:
            
            self.labld_glyphs = mlab.points3d(self.x, self.y, self.z,
                                              scale_factor=0.05,
                                     mode='cube', colormap='hsv',
                                     figure=self.fig)
            self.labld_glyphs.glyph.scale_mode = 'scale_by_vector'
            
            self.labld_glyphs.mlab_source.dataset.point_data.scalars = self.labld_glyphcolors
        else:
            self.labld_glyphs.mlab_source.reset(x = self.x,
                                                y = self.y,
                                                z = self.z,
                                                scale_factor=0.05,
                                     mode='cube', colormap='hsv',
                                     figure=self.fig,
                                     scalars = self.labld_glyphcolors)
            self.labld_glyphs.glyph.scale_mode = 'scale_by_vector'                  
            self.labld_glyphs.mlab_source.dataset.point_data.scalars = self.labld_glyphcolors                    
                    
        # get the xyz points of the plotted points 
        self.labld_points = self.labld_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()
        self.knwn_points = self.known_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()
        
        self.create_trajectorytags()
        
        #mlab.gcf().scene.disable_render = False 
        #mlab.draw(figure=self.fig)         

  
    
    def view_point_information(self,picker):
        '''Callback function when a glyph is left-button clicked. 
        Information on the xyz and time of recording/emission is displayed
        
        '''
        #print('MOUSE CALLBACK')
            
        
        self.click_text.text = ''
 
        
        all_glyphs = [ self.known_glyphs.actor.actors, 
                                          self.labld_glyphs.actor.actors]
    
        closest_glyph = [picker.actor in disp_glyphs for disp_glyphs in all_glyphs ]
        all_pointsxyz = [self.knwn_points, self.labld_points]
        
        
        try:
            which_glyph = int(np.argwhere(closest_glyph) )
            #print('which_glyph',which_glyph)
            
            points_xyz = all_pointsxyz[which_glyph]
        except:
            return()
            
        if which_glyph == 0:
            time_col = 't_knwn'
        elif which_glyph == 1:
            time_col = 't'
        #print('time col:', time_col)
        
        if picker.actor in all_glyphs[which_glyph]:
           
            #print(picker.point_id)
            point_id = picker.point_id/points_xyz.shape[0]
            #print('point_id',point_id)
            # If the no points have been selected, we have '-1'
            if point_id != -1:
                # Retrieve the coordinnates coorresponding to that data
                # point
                if which_glyph==0:
                    #print('known point chosen')
                    x_pt, y_pt, z_pt = self.x_knwn[point_id], self.y_knwn[point_id], self.z_knwn[point_id]                                                                                                    
                    pt_type = 'Known'
                else:
                    #print('labelled point chosen')

                    x_pt, y_pt, z_pt = self.x[point_id], self.y[point_id],  self.z[point_id]
                    pt_type = 'Labelled'
                # Move the outline to the data point.
                self.outline.bounds = (x_pt-0.05, x_pt+0.05,
                                  y_pt-0.05, y_pt+0.05,
                                  z_pt-0.05, z_pt+0.05)
                self.outline.visible = True
                        
                #display the x,y,z and time info on the selected point #
                
                if which_glyph == 0:
                    time_stamp = np.around(self.tsubset_knwntraj[time_col][point_id],4)
                    traj_num = self.tsubset_knwntraj['traj_num'][point_id]
                    #print('known point traj num:', traj_num)
                    
                else :
                    time_stamp = np.around(self.tsubset_labldtraj[time_col][point_id],4)
                    traj_num = self.tsubset_labldtraj['traj_num'][point_id]
                    
                self.click_text.text = str([np.around(x_pt,2),
                                           np.around(y_pt,2), np.around(z_pt,2)
                                           ,time_stamp ]) 
                #display the trajectory number of the selected point 
                self.traj_text.text = 'Traj number: ' + str(traj_num)
                self.pointtype_info.text = pt_type
            
            
         
            else:
                print('failed :', point_id)
                
    def reassign_callback(self,picker):
        """ Picker callback: this get called when on pick events.
        
        A user prompt appears when the picker is triggered for 
        entry of the trajectory number. Input >=1 and <=99 is expected. 
        If the trajectory number needs to be set to a NaN, then simply click
        on 'Cancel'
        
        
        
        """              
        
        if picker.actor in self.labld_glyphs.actor.actors:
   
           
            point_id = picker.point_id/self.labld_points.shape[0]
            
            # If the no points have been selected, we have '-1'
            if point_id != -1:
                # Retrieve the coordinnates coorresponding to that data
                # point
                print('labelled point chosen')
        
                x_pt, y_pt, z_pt = self.x[point_id], self.y[point_id],  self.z[point_id]                
                # Move the outline to the data point.
                self.outline.bounds = (x_pt-0.15, x_pt+0.15,
                                  y_pt-0.15, y_pt+0.15,
                                  z_pt-0.15, z_pt+0.15)
                
                self.outline.visible = True
                try:        
                    new_trajnum = eg.integerbox('Please enter the re-assigned trajectory number',
                                                lowerbound=1,upperbound=99,
                                                default = None)
                    print('New traj num', new_trajnum)
                    
                    self.trajectory_reassignment(new_trajnum,point_id)                    
                   
                except:
                    print('Unable to re-assign point')
                              
    
                
                
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
            tsubset_df = tsubset_df.reset_index(drop=True)
            
            return(tsubset_df)
        except:
            print('Wrong time ranges !! ')                     
                
        
         
        
    
    # The layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                Group(
                        '_', 'Time_range_start', 'Time_range_end',
                     ),
                resizable=True,
                )
    
            
          
    def identify_orig_rowindex(self,orig_df,df_row):
        '''When a point has been chosen for trajectory re-assignment, 
        find its original row index in the dataset and change the value there
        
        Parameters:
            
            orig_df : pd.DataFrame with multiple rows and columns
            
            df_row : 1 x Ncolumns pd.DataFrame. 
            
        Returns:
            
            orig_index : int. Row index of the original DataFrame pd1 with 
                        values that match df_row
        
        
        '''
        x_match = orig_df['x'] == df_row.x
        y_match = orig_df['y'] == df_row.y
        z_match = orig_df['z'] == df_row.z
        
        try:
            row_index = orig_df.loc[x_match & y_match & z_match].index
            return(row_index)
        except:
            print('Matching row not found !! Returning None')
            
    def generate_color_and_size(self):
            for each_trajtype in [self.knwntraj_data, self.labtraj_data]:        
                each_trajtype['colors'] = each_trajtype['traj_num'].apply(assign_colors_float,1)                 
                each_trajtype['size'] = np.tile(0.05,each_trajtype.shape[0])
                         
        
            self.end_time = np.max([np.max(self.labtraj_data['t']),
                               np.max(self.knwntraj_data['t_knwn'])]) 
        
    def trajectory_reassignment(self, new_trajnum, pt_id):
        '''Re-assigns the trajectory number of a labelled point in the original 
        labld_traj pd.DataFrame
        
        Parameters:
            
            new_trajnum: int. New trajectory number
            
            pt_id : int. row number of the tsubset_labdtraj which needs to be
                    accessed
        '''
        
        self.current_row = self.tsubset_labldtraj.loc[pt_id]
        
        #print('trying to re-assign')
        #print(self.current_row)
        orig_index = self.identify_orig_rowindex(self.labtraj_data, self.current_row)
        
        try:
            self.labtraj_data['traj_num'][orig_index] = new_trajnum
            
            print('Trajectory succesfully re-assigned for point #'+str(orig_index))
            self.generate_color_and_size()
            self.update_plot()
        except:
            print('Unable to re-assign !!') 

    def create_trajectorytags(self):
        '''Make a label which shows the trajectory number for each plotted point
        '''
        for each_tag in self.trajtags:
            try:
                each_tag.visible = False # clear out all traj labels             
                
            except:
                print('Could not set each_tag.visible to False')
                pass
        self.trajtags[:] = []
        
        
        known_data = self.tsubset_knwntraj[['x_knwn','y_knwn','z_knwn','traj_num']]
        labld_data = self.tsubset_labldtraj[['x','y','z','traj_num']]
        
        
                
        for point_collection in [known_data, labld_data]:
            for i,each_row in point_collection.iterrows():                
                try:
                    trajtag = mlab.text3d(each_row.x_knwn + self.tag_offset,
                                          each_row.y_knwn + self.tag_offset,
                                          each_row.z_knwn + self.tag_offset,
                            str(each_row.traj_num),
                            scale=self.tag_size,
                            figure=mlab.gcf())
                except:
                    trajtag = mlab.text3d(each_row.x+ self.tag_offset,
                                          each_row.y+ self.tag_offset,
                                          each_row.z+ self.tag_offset,
                            str(each_row.traj_num),scale=self.tag_size,
                            figure=mlab.gcf())
            
            
                self.trajtags.append(trajtag)
            

num_colors = 20
traj_2_color_float = {  i+1 : (i+0.01)/num_colors    for i in range(1,num_colors+1)    }
         
def assign_colors_float(X):
    '''Outputs a float value between 0 and 1 
    at 
    '''
    try:
        color = traj_2_color_float[X]
        return(color)
    except:
        color = 0.99
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
    lin_inc = np.linspace(0,1.5,25) 
    lin_inc = np.random.normal(0,1,lin_inc.size)
    xyz = np.column_stack((lin_inc,lin_inc,lin_inc))
    txyz = np.column_stack((xyz, np.linspace(0,30,xyz.shape[0])))
    kn_data = pd.DataFrame(data=txyz, columns = ['x_knwn','y_knwn',
                                                 'z_knwn','t_knwn'])
    kn_data['traj_num'] = np.random.choice(range(2,4),xyz.shape[0])
    
    #num_pts = 25
    #some_rows = np.random.choice(range(xyz.shape[0]),num_pts,replace=False)
    xyz_lab = xyz 
    xyz_lab[:,0] += 0.5
    t_somerows = txyz[:,3]
    txyz_somerows = np.column_stack((xyz_lab,t_somerows))
    lab_data = pd.DataFrame(data=txyz_somerows, columns = ['x','y','z','t'])
    onecolor_pts = 7
    lab_data['traj_num'] = kn_data['traj_num']#np.random.choice(range(2,4),num_pts)#np.concatenate((np.tile(2,onecolor_pts),
                            #np.tile(1, num_pts-onecolor_pts)))
    
    traj_cleaner = TrajCleaner()
    traj_cleaner.knwntraj_data = kn_data
    traj_cleaner.labtraj_data = lab_data
    traj_cleaner.configure_traits()
  
    
    