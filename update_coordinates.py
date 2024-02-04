import random
import os 

file_path=os.getcwd()+ '/sr/robot/arenas/silver_locations_file.txt'

# these are the original positions of the silver tokens in the 'sunnyside up' arena
original_tuples = [(-8,0),(-6, 3.75),(-2.5, 1.25),(1.5, -0.25),(6, 3.75),(8, 0.0),(-4.0, -4.0)]

# modify the coordinates by adding a random value between +0.5 and -0.5
modified_tuples = [(x + random.uniform(-0.5, 0.5), y + random.uniform(-0.5, 0.5)) for x, y in original_tuples]

# write the modified tuples back to the file
with open(file_path, 'w') as file:
   
    # use repr to convert the list of tuples back to a string with the original structure
    file.write(repr(modified_tuples))