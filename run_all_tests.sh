#!/bin/bash

# Define the temporary file for the log file name
temp_file="./temp_log_file.txt"

# Define the log file with a timestamp
log_file_name="Trials_$(date +'%Y_%m_%d_%H%M%S').txt"

# Save the log file name to the temporary file
echo "$log_file_name" > "$temp_file"

for i in {0..45}
do
    # Run the Python script to update silver token coordinates
    python3 update_coordinates.py

    # Run assignment_1_controller.py with the log file as an argument
    echo -e "--------------------------- \n test_${i} assignment_1_controller" >> "./logs/$log_file_name"
    python3 TEST_run.py assignment_1_controller.py &
    sleep 200
    kill -9 $!

    # Run benchmark_controller.py with the log file as an argument
    echo -e "--------------------------- \n test_${i} benchmark_controller" >> "./logs/$log_file_name"
    python3 TEST_run.py benchmark_controller.py &
    sleep 200
    kill -9 $!
done

echo -e "--------------------------- \n" >> "./logs/$log_file_name"

# Remove the temporary file after use
rm "$temp_file"
