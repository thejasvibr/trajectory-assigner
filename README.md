# trajectory-assigner
A Mayavi based visualisation tool that allows the visualisation and re-assignment of a trajectory label when there are two
sets of sources for the same trajectory/ies

Use case :
When an object's position is being estimated by two tracking systems, eg. video and acoustic tracking - it can be tricky to assign the positions from either system to the same trajectory. This module assumes a *known* source of trajectory points that have reliable trajectory tags (eg. those from video tracking), and a *labelled* set of trajectory points that have been assigned manuall or automatically, but may be unreliable (eg. those from acoustic tracking). 

What it does : 
The current version of the module allows a user to :
1) visualise both *known* and *labelled* points
2) Interactively display a subset of points based on the chosen time range through the user interface
3) Point information is displayed when the user left-clicks on a point
4) Trajectory tag reassignment is done by right-clicking on a *labelled* point. 

What it does not do:
1) Deletion of points
2) Addition of points
3) Trajectory reassignment of *known* points 


TO DO : 
1) Dynamically change point colors according to trajectory tags. Currently this is not possible, but tag numbers are displayed.

