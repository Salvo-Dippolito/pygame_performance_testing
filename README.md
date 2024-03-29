Python Robotics Simulator Performance Testing
==============================================

This repository is a modified version of [this repository](https://github.com/Salvo-Dippolito/Research-Track-1) that was developed for the first assignment of the Research Track 1 course.

#### Changes made:

  - modified the run.py script to use slightly modified libraries to accomodate randomization of the test map layout.

  - added update_coordinates.py script and a silver_locations_file.txt.
  The update_coordinates script is called at the start of every trial to randomize the positions of the silver tokens in the 'sunny side up' arena where the controllers are being tested, new coordinates are written in the file silver_locations_file.txt that has been placed in the 'arenas' folder.

  - added the benchmark_controller.py script that runs the controller with which we're comparing the assignment_1_controller.py that was developed for the first assignment of the Research Track 1 course.

  - added code in the two controllers to save performance data in the [logs](https://github.com/Salvo-Dippolito/pygame_performance_testing/tree/main/logs) folder of this repository

  - the results of the performance analysis of the two controllers are presented in the [trial_results_notebook](https://github.com/Salvo-Dippolito/pygame_performance_testing/tree/main/trial_results_notebook) folder

#### How to run

After cloning this repo, move to its base folder and run the run_all_tests.sh bash script. 
This script will perform 46 trials for each controller, so 92 trials in total. At the start of each trial the 'sunny side up arena' map,  where the controllers' performances are being tested, gets loaded with all of its silver tokens placed in newly randomized positions and both controllers get tested on the same newly randomized map. Each trial lasts 200 seconds, so the total execution time needed to have a complete log file with the results of all the prescribed trials is a little over 5 hours. 


Of course the run_all_tests.sh bash script can be easily modified to perform more trials, trial logs can also be merged together by copy pasting them in a single txt file than can be fed to the [data processing notebook](https://github.com/Salvo-Dippolito/pygame_performance_testing/tree/main/trial_results_notebook) like any other log file.
