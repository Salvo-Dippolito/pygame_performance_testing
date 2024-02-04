
from __future__ import print_function

import time
import math
from math import  atan2,sqrt,hypot
from datetime import datetime
from sr.robot import *
from statistics import mean
import random
import sys

a_th = 2
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

silver = True
""" boolean: variable for letting the robot know if it has to look for a silver or for a golden marker"""

R = Robot()

import os
from datetime import datetime

d_th = 0.4

def drive_rot(speed, seconds):
    """
    Function for setting a linear velocity and an angular velocity
    """
    R.motors[0].m0.power = speed*2
    R.motors[0].m1.power = 0
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def drive(speed, seconds):
    """
    Function for setting a linear velocity

    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
    

def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def find_silver_token():
    """
    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER and token.rot_y<30.0 and token.rot_y>-30.0:
            dist=token.dist
            rot_y=token.rot_y
    if dist==100:
        return 100, -1
    else:
        return dist, rot_y

def find_golden_token():
    """
    Function to find the closest golden token

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if token.info.marker_type is MARKER_TOKEN_GOLD and ((token.dist < dist and token.rot_y<25 and token.rot_y>-25) or (token.dist < 0.5 and token.rot_y<90.0 and token.rot_y>-90.0)):
            dist=token.dist
            rot_y=token.rot_y
    
    if dist==100:
        return 100, -1
    else:
        return dist, rot_y
   	
def check_right_side():
    dist = 100
    #print (R.see())
    for token in R.see():
         if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD and token.rot_y<90.0 and token.rot_y>60.0:
             dist=token.dist
             #print(token.rot_y)
    if dist==100:
        return 100
    else:
        return dist
   	
def check_left_side():
    dist = 100
    #print (R.see())
    for token in R.see():
         if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD and token.rot_y>-90.0 and token.rot_y<-60.0:
             dist=token.dist
             #print(token.rot_y)
    if dist==100:
        return 100
    else:
        return dist
    
# Functions added to automate testing
#========================================================================================================
def compass():
    angle=R.heading*180/math.pi
  
    return angle
def in_range(variable,minimum,maximum):
    
    if minimum<=variable<=maximum :
        return 1
    else:
        return 0

def angle_correction(angle):

    if -180>angle>=-360:
        angle=angle+360
    elif 180<angle<=360:
        angle=angle-360

    return angle


def P_control_angle(angle, precision, kp, use):
    
    if use == "relative":
        target_angle = angle_correction(compass() + angle)
    else:
        target_angle = angle_correction(angle)

    while True:
        current_angle = angle_correction(compass())
        error = target_angle - current_angle

        if -precision <= error <= precision:
            break

        speed = min(error * kp, 90)  # Cap the speed at 90 to avoid excessive values
        R.motors[0].m0.power = speed
        R.motors[0].m1.power = -speed
        time.sleep(0.003)

    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def P_control_distance(distance,precision,kp):
    error=1
    x_initial,y_initial = R.location

    while error<=-precision or error >=precision:
        x,y = R.location
        distance_travelled= math.sqrt((x-x_initial)**2+(y-y_initial)**2)
        
        if distance>0:
            error=distance-distance_travelled
        elif distance<0:
            error=distance+distance_travelled
        speed = error*kp
        R.motors[0].m0.power = speed
        R.motors[0].m1.power = speed
        time.sleep(0.006)

    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

    return 1

def update_log(message):
    with open(log_file_path, 'a') as log:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{current_time}] {message}\n"
        log.write(log_message)

def go_to(waypoint):
    goal_x,goal_y=waypoint
    x, y = R.location
    Dy=goal_y - y
    Dx=goal_x - x
    direction = atan2(Dy,Dx )
    distance=sqrt(Dx**2+Dy**2)

    P_control_angle(math.degrees(direction),0.01,1,'absolute')
    P_control_distance(distance,0.1,100)

def start_timer():
    start_time = time.time()
    return 1,start_time

def stop_timer(start_time):
    stop_time = time.time()
    elapsed_time = stop_time - start_time
    return 0,elapsed_time

# create a 'logs' directory if it doesn't exist
logs_directory = "logs"
os.makedirs(logs_directory, exist_ok=True)
temp_file_path='./temp_log_file.txt'

# check if the temporary file exists
if os.path.isfile(temp_file_path):
    with open(temp_file_path, 'r') as file:
        log_file_name = file.read().strip()
else:
    # if the temporary file doesn't exist, create a new log file with time and date in the name
    log_file_name = f"Trials_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.txt"
    
    # save the log file name to the temporary file
    with open(temp_file_path, 'a') as file:
        file.write(log_file_name)

# Create a log file with the current date and time in the name
log_file_path = os.path.join(logs_directory, log_file_name)


start_x= -8
start_y= -3

finish_x= -6
finish_y= -4

loop_counter=0
timer_flag=0

going_forward=1
failed_grabs,succesful_grabs= 0,0


#========================================================================================================

while 1:
    dist, rot_y = find_silver_token()
    go = True

    x, y = R.location
    heading=compass()
    
    # check if the robot is in the start zone and the lap timer hasn't been started yet
    if x<finish_x and y>start_y and timer_flag==0:
        timer_flag,start_time=start_timer()
        print(f"STARTING TIMER timer flag is {timer_flag}\n")
        update_log(f"")
    
    #check if the robot has atually finished a lap or if it turned backwards 
    elif x<finish_x and 0>y>start_y and timer_flag==1:
        
        if  in_range(heading, 0,180):
            going_forward=1
            print("GOING FORWARD\n")
        else:
            going_forward=0
            print("NOT GOING FORWARD\n")        

    # update log with new lap times and grab statistics only if the robot has actually done a full lap
    elif x<finish_x and y<start_y and timer_flag==1 and going_forward==1 :
        
        loop_counter +=1
        timer_flag, elapsed_time= stop_timer(start_time)
        print(f"STOPPING TIMER timer flag is {timer_flag} elapsed time is: {elapsed_time}\n")
        update_log(f"loop {loop_counter} - seconds {elapsed_time} -succesful grabs {succesful_grabs} - failed grabs {failed_grabs} - missed grabs {7-succesful_grabs}")
        failed_grabs,succesful_grabs= 0,0

    elif x<finish_x and y<start_y and timer_flag==1 and going_forward==0 :
        timer_flag,_=stop_timer(start_time)


    if dist < 2.0:
        
        go = False
        dist2, rot2_y = find_golden_token()
        
        if dist2 > 0.0 and dist2 < 0.8:
            go = True
            
        if dist == -1:  # if no token is detected, we make the robot turn 
            pass
        elif dist < d_th:  # if we are close to the token, we try to grab it.
            print("Found it!")
            
            if R.grab():  # if we grab the token, we move the robot forward and on the right, we release the token, and we go back to the initial position
                print("Gotcha!")
                succesful_grabs += 1
                turn(30, 2)
                # drive(20,2)
                R.release()
                # drive(-20,2)
                turn(-30, 2)
            else:
                print("Aww, I'm not close enough.")
                failed_grabs += 1

        elif -a_th <= rot_y <= a_th:  # if the robot is well aligned with the token, we go forward
            print("Ah, that'll do.")
            drive(50, 0.5)
        elif rot_y < -a_th:  # if the robot is not well aligned with the token, we move it on the left
            print("Left a bit...")
            turn(-2, 0.5)
        elif rot_y > a_th:
            print("Right a bit...")
            turn(2, 0.5)

    if (go):    
        drive(50,.05) #we move the robot forward
        dist, rot_y = find_golden_token()
        init=True
        left=True
        if dist > 0.0 and dist <0.8:
    	    while True:
                if(init):
                    dist_r=check_right_side()
                    dist_l=check_left_side() 
                    print(dist_r)
                    print(dist_l)
                    if(dist_r>dist_l):
                        left=True
                    else:
                        left=False
                    init=False
                
                if(left):
                    turn(10,0.1)
                else:
                    turn(-10,0.1)
                dist, rot_y = find_golden_token()
                if dist>2.0:
                    break
         
        

	
