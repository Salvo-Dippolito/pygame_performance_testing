#!/bin/bash

# define the temporary file for the log file name
temp_file="./temp_log_file.txt"

# define the log file with a timestamp
log_file_name="Trials_$(date +'%Y_%m_%d_%H%M%S').txt"

# save the log file name to the temporary file
echo "$log_file_name" > "$temp_file"

for i in {0..1}
do
    # run the Python script to update silver token coordinates
    python3 update_coordinates.py

    # run assignment_1_controller.py with the log file as an argument
    echo -e "--------------------------- \n test_${i} assignment_1_controller" >> "./logs/$log_file_name"
    python3 TEST_run.py assignment_1_controller.py &
    sleep 200
    pkill -9 -f assignment_1_controller.py

    # run benchmark_controller.py with the log file as an argument
    echo -e "--------------------------- \n test_${i} benchmark_controller" >> "./logs/$log_file_name"
    python3 TEST_run.py benchmark_controller.py &
    sleep 200
    pkill -9 -f benchmark_controller.py
done

echo -e "--------------------------- \n" >> "./logs/$log_file_name"

# remove the temporary file after use
rm "$temp_file"

