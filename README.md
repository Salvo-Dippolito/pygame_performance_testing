Python Robotics Simulator Performance Testing
==============================================

This repository is a modified version of the (repository)[] developed for the first assignment of the Research Track 1 course.

#### Changes made:

  - modified the run.py script to use slightly modified libraries to accomodate randomization of the test map layout.

  - added update_coordinates.py script and a silver_locations_file.txt.
  The update_coordinates script is called at the start of every trial to randomize the positions of the silver tokens in the 'sunny side up' arena where the controllers are bein tested, new coordinates are written in the file silver_locations_file.txt that has been placed in the 'arenas' folder.

  - added the benchmark_cntroller.py script that runs the controller with which we're comparing the assignment_1_controller.py that was developed for the first assignment of the Research Track 1 course.

  - added code in the two controllers to save performance data in the 'logs' folder of this repository

  - the results of the perforance analysis of the two controllers are presented in the 'Notebook' folder

#### How to run

After cloning this repo move to its base folder and run the run_all_tests.sh bash script. This script will perform 45 trials for each controller. At the start of each trial the trial map is 
