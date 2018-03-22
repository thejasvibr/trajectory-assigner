# trajectory-assigner
A Mayavi based visualisation tool that allows the visualisation and re-assignment of a trajectory label when there are two
sets of sources for the same trajectory/ies

Use case :
When an object's position is being estimated by two tracking systems, eg. video and acoustic tracking - it can be tricky to assign the positions from either system to the same trajectory. This module assumes a *known* source of trajectory points that have reliable trajectory tags (eg. those from video tracking), and a *labelled* set of trajectory points that have been assigned manuall or automatically, but may be unreliable (eg. those from acoustic tracking). 

### What it does : 
The current version of the module allows a user to :
1) visualise both *known* and *labelled* points
2) Interactively display a subset of points based on the chosen time range through the user interface
3) Point information is displayed when the user left-clicks on a point
4) Trajectory tag reassignment is done by right-clicking on a *labelled* point. 

### What it does not do:
1) Deletion of points
2) Addition of points
3) Trajectory reassignment of *known* points 


### Usage : 
Initiate a TrajCleaner instance 
        
        traj_cleaner = TrajCleaner()
        
        # assign the labelled and known trajectory datasets to the instance 
        
         traj_cleaner.knwntraj_data = kn_data
         traj_cleaner.labtraj_data = lab_data
         
Begin the Mayavi interactive visualisation
        
        traj_cleaner.configure_traits()
        
After checking the trajectory assignment and performing reassignment close the
Mayavi window and save the labld_traj pd.DataFrame to a csv 
        
        traj_cleaner.labld_traj.to_csv('labelled_traj_verified.csv')
        
User-controlled parameters :
        
     tag_offset : the distance between the numeric trajectory tag and 
                     the displayed trajectory points
        
     tag_size : size of the numeric trajectory tag
