# -*- coding: utf-8 -*-
""" Tests and test datasets for interactive trajectory cleaner 
in Mayavi 

Created on Mon Mar 19 13:15:21 2018

@author: tbeleyur
"""
import numpy as np 
import pandas as pd

from trajassigner import *


def testing_with_linearincreasedata():
    ''' The known and labelled datasets increase linearly in the XYZ axes. 
    The known and labelled points are 3d diagonals and connect to form 
    a pair of parallel lines. 
    '''
    
    print('Testing with All data present \n')
    
    lin_inc = np.linspace(0,1.5,10) 
    lin_inc += np.random.normal(0,0.1,lin_inc.size)
    xyz = np.column_stack((lin_inc,lin_inc,lin_inc))
    txyz = np.column_stack((xyz, np.linspace(0,30,xyz.shape[0])))
    kn_data = pd.DataFrame(data=txyz, columns = ['x_knwn','y_knwn',
                                                 'z_knwn','t_knwn'])
    kn_data['traj_num'] = np.arange(lin_inc.size)
    #num_pts = 25
    #some_rows = np.random.choice(range(xyz.shape[0]),num_pts,replace=False)
    xyz_lab = xyz 
    xyz_lab[:,0] += 0.5
    t_somerows = txyz[:,3]
    txyz_somerows = np.column_stack((xyz_lab,t_somerows))
    lab_data = pd.DataFrame(data=txyz_somerows, columns = ['x','y','z','t'])
    lab_data['traj_num'] = kn_data['traj_num']#np.random.choice(range(2,4),num_pts)#np.concatenate((np.tile(2,onecolor_pts),
                            #np.tile(1, num_pts-onecolor_pts)))
    
    traj_cleaner = TrajAssigner()
    traj_cleaner.knwntraj_data = kn_data
    traj_cleaner.labtraj_data = lab_data
    traj_cleaner.configure_traits()
    
    return(traj_cleaner)




def testing_with_missingdata():
    ''' The known and labelled datasets increase linearly in the XYZ axes. 
    The known and labelled points are 3d diagonals and connect to form 
    a pair of parallel lines. 
    
    The labelled data has *NO* trajectory tags 
    
    '''
    
    print('Testing with missing trajectory tags \n')
    
    lin_inc = np.linspace(0,1.5,10) 
    lin_inc += np.random.normal(0,0.1,lin_inc.size)
    xyz = np.column_stack((lin_inc,lin_inc,lin_inc))
    txyz = np.column_stack((xyz, np.linspace(0,30,xyz.shape[0])))
    kn_data = pd.DataFrame(data=txyz, columns = ['x_knwn','y_knwn',
                                                 'z_knwn','t_knwn'])
    kn_data['traj_num'] = np.arange(1,lin_inc.size+1)
    
    #num_pts = 25
    #some_rows = np.random.choice(range(xyz.shape[0]),num_pts,replace=False)
    xyz_lab = xyz 
    xyz_lab[:,0] += 0.5
    t_somerows = txyz[:,3]
    txyz_somerows = np.column_stack((xyz_lab,t_somerows))
    lab_data = pd.DataFrame(data=txyz_somerows, columns = ['x','y','z','t'])
    lab_data['traj_num'] = kn_data['traj_num']
    
    traj_cleaner = TrajAssigner()
    traj_cleaner.knwntraj_data = kn_data
    traj_cleaner.labtraj_data = lab_data
    traj_cleaner.configure_traits()
    
    return(traj_cleaner)
    
def testing_with_missingxyz():
    ''' The known and labelled datasets increase linearly in the XYZ axes. 
    The known and labelled points are 3d diagonals and connect to form 
    a pair of parallel lines. 
    
    The 
    
    '''
    
    print('Testing with some missing xyz points in labelled data \n')
    
    lin_inc = np.linspace(0,1.5,10) 
    #lin_inc = np.random.normal(0,1,lin_inc.size)
    xyz = np.column_stack((lin_inc,lin_inc,lin_inc))
    txyz = np.column_stack((xyz, np.linspace(0,20,xyz.shape[0])))
    kn_data = pd.DataFrame(data=txyz, columns = ['x_knwn','y_knwn',
                                                 'z_knwn','t_knwn'])
    kn_data['traj_num'] = np.arange(1,lin_inc.size+1)
    
    num_missingrows = 5
    missing_rows = np.random.choice(range(kn_data.shape[0]),num_missingrows)
    
    #num_pts = 25
    #some_rows = np.random.choice(range(xyz.shape[0]),num_pts,replace=False)
    xyz_lab = xyz 
    xyz_lab[:,0] += 0.5
    t_somerows = txyz[:,3]
    txyz_somerows = np.column_stack((xyz_lab,t_somerows))
    lab_data = pd.DataFrame(data=txyz_somerows, columns = ['x','y','z','t'])
    lab_data['traj_num'] =  kn_data['traj_num']
    lab_data['x'][missing_rows] = np.nan
    
    traj_cleaner = TrajAssigner()
    traj_cleaner.knwntraj_data = kn_data
    traj_cleaner.labtraj_data = lab_data
    traj_cleaner.configure_traits()
    
    return(traj_cleaner)


def testing_with_multipletrajectories():
    ''' REcreate 4 trajectories with the same trajectory tag and see if 
    colour consistency remains. EAch trajectory should get a unique colour. 
    
    '''
    t = np.linspace(0,1.0,15)    
    freqs = np.linspace(1,5,5)
    
    traj_nums = range(1,freqs.size+1)
    
    kn_data = pd.DataFrame(data =None, columns=['x_knwn','y_knwn',
                                                'z_knwn','t_knwn','traj_num'])
    
    kn_data['t_knwn'] = np.tile(t,freqs.size)
    kn_data['y_knwn'] = np.concatenate(([ i*np.sin(2*np.pi*freqs[i]*t) for   i,each_traj in enumerate(traj_nums)]))
    kn_data['x_knwn'] = np.tile(t,freqs.size)
    kn_data['z_knwn'] = np.concatenate([np.tile(z,t.size) for z in traj_nums])
    
    
    lab_data = pd.DataFrame(data=None,columns=['x','y','z','t','traj_num'])
    lab_data['t'] = kn_data['t_knwn']+ 0.04
    lab_data['x'] = kn_data['x_knwn'].copy()
    lab_data['x'] += np.random.normal(0,0.1,lab_data['x'].size)
    lab_data['y'] = kn_data['y_knwn'].copy()
    lab_data['z'] = kn_data['z_knwn'].copy()
    lab_data['z'] += np.random.normal(0,0.5,lab_data['z'].size)
    
    kn_data['traj_num'] = kn_data['z_knwn'].copy()
    lab_data['traj_num'] = kn_data['z_knwn'].copy()
    
    traj_cleaner = TrajAssigner()
    traj_cleaner.knwntraj_data = kn_data
    traj_cleaner.labtraj_data = lab_data
    traj_cleaner.configure_traits()
    
    return(traj_cleaner)
    
    
    
    
    
    
    
    
    


if __name__ == '__main__':
    
    test1 = testing_with_linearincreasedata()
    
    #test_missing = testing_with_missingdata()
    
    #test_missingxyz = testing_with_missingxyz()
    
    #test_multitraj = testing_with_multipletrajectories()
    

    
    
