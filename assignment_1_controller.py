#!/usr/bin/env python

from __future__ import print_function

import time
import math
from math import  atan2,sqrt,hypot
from datetime import datetime
from sr.robot import *
from statistics import mean
import random
import sys

a_th = 0.1
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

silver = True
""" boolean: variable for letting the robot know if it has to look for a silver or for a golden marker"""

R = Robot()

import os
from datetime import datetime




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
    # else:

    return angle


def drive(speed, seconds):
    
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
   
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def dist_golden():     
    dist=100

    for token in R.see():    
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist


    return dist

def dist_silver():     
    dist=100
    
    for token in R.see():
        
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER :
            dist=token.dist


    return dist

def a_dist_silver():
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER:
            dist=token.dist
            angle=token.rot_y
    if dist==100:
        return -1, -1
    else:
        return angle

def a_dist_golden():
    
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
            angle=token.rot_y
    if dist==100:
        return -1, -1
    else:
        return angle
    

def scan_blocks():
    on_the_right=[]
    on_the_left=[]
    dist=1.5
    min_fov=20
    max_fov=100
   
    for token in R.see():
        
        if token.dist<dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            if in_range(token.rot_y,-max_fov,-min_fov):
                on_the_left.append(token.dist)
            elif in_range(token.rot_y,min_fov, max_fov):
                on_the_right.append(token.dist)
    
    print(f"to the right: {on_the_right} \n to the left:{on_the_left}")

    # print(f"max dist:{max_dist} min dist: {min_dist} max ang: {max_ang} min ang: {min_ang}\n")
    if len(on_the_right)>len(on_the_left):

        return -0.5 #turn left
    
    elif len(on_the_left)>len(on_the_right):

        return 0.5 #turn right
  
    elif on_the_left and on_the_right:

        if mean(on_the_right)>mean(on_the_left):
            print("mean right turn left")
            return 1
        else:
            print("mean left turn right")
            return -1
        
    else:

        return random.uniform(-0.1,0.1)

def compass():
    angle=R.heading*180/math.pi
  
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

        speed = min(error * kp, 90)#cap the speed at 90 to avoid excessive values
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

def check_and_correct_heading(initial_heading,avoid,last_decision):
    if abs(angle_correction(compass()-avoid))<70:

        # check if the last maneuver hasn't taken the bot too far to the left

        print("I'm too close to this heading"+str(avoid))
        if last_decision=="left":
            P_control_angle(initial_heading-45,0.1,1,"absolute")
        elif last_decision=="right":
            P_control_angle(initial_heading+45,0.1,1,"absolute")
        
        P_control_distance(-(0.8-dist_golden()),0.01,90)
        drive(-20,0.5)

    return 1

def motors_on(speed):
    R.motors[0].m0.power=speed
    R.motors[0].m1.power=speed

def brake():
    R.motors[0].m0.power=0
    R.motors[0].m1.power=0

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
        
# create a log file with the current date and time in the name
log_file_path = os.path.join(logs_directory, log_file_name)

def update_log(message):
    with open(log_file_path, 'a') as log:
        print(log_file_path)
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
    # print(f"{x} {y} {goal_x} {goal_y} {Dx} {Dy} {direction}=={math.degrees(direction)} distance {distance} hyp {hypot(Dx,Dy)}")

    P_control_angle(math.degrees(direction),0.01,1,'absolute')
    P_control_distance(distance,0.1,100)


def main():
    # os.system('clear')
    golden_counter=0
    turn_counter=0
    master_speed=100
    last_decision="right"
    d_th=0.8

    # turn(-20,1.5) #turn left
    # turn(20,5) #turn right

    start_x= -8
    start_y= -3

    finish_x= -6
    finish_y= -4
   
    loop_counter=0
    timer_flag=0

    going_forward=1
    failed_grabs,succesful_grabs= 0,0

    while 1:

        print("-------------------------------------------------------------------")

        x, y = R.location
        heading=compass()
        
        # check if the robot is in the start zone and the lap timer hasn't been started yet
        if x<finish_x and y>start_y and timer_flag==0:
            timer_flag,start_time=start_timer()
            print(f"STARTING TIMER timer flag is {timer_flag}\n")
            update_log(f"")
        
        # check if the robot has atually finished a lap or if it turned backwards 
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

        d_silver=dist_silver() 
        d_golden=dist_golden()  
    
        # drive straight until the robot gets close to a block
        motors_on(master_speed)
        while (d_golden>d_th and d_silver>d_th):
            time.sleep(0.0001)
            golden_counter=0
            
            #update distances
            d_silver=dist_silver() 
            d_golden=dist_golden()   
        brake()
        
        a_golden=a_dist_golden()        
        a_silver=a_dist_silver()

        if d_golden>=d_silver:
            
            print("SILVER is closer")

            golden_counter=0 #reset golden counter

            if in_range(a_silver,-90,90):
                

                P_control_angle(a_silver,0.5,1,"relative")
 
                P_control_distance(d_silver-0.3,0.05,100)             

                if R.grab()==1 :

                    succesful_grabs += 1
                    time.sleep(0.5)

                    P_control_angle(-180,0.1,1,"relative")          
                
                    R.release()
                    P_control_distance(-0.35,0.2,90)
                    P_control_angle(180,0.1,1,"relative")
                    time.sleep(0.5)
                else:
                    print("failed_grab\n")
                    failed_grabs += 1
 

            else:

                if not in_range(a_golden,-50,50): # if the robot doesn't have a golden block right behind it

                    # silver is closer than the closest golden but not in front of the robot
                    # and the closest golden is not in front of the robot
                    print("Silver token is behind me, I'll go on\n")
                    drive(master_speed,0.3)  

                elif in_range(a_silver,-180,-175) or in_range(a_silver,175,180) :

                    # silver is closer than golden but right behind the robot
                    # there are also gold blocks on the front sides of the robot
                    # the robot will try to push it back a bit and goback to whereit started the maneuver
                    print("I'll try to get some space by backing up \n and getting closer to a golden token")
                    
                    backup_distance=d_silver+0.1
                    # P_control_distance(-backup_distance,0.01,90)
                    # P_control_distance(backup_distance,0.01,90)
                    drive(-master_speed,0.2)
                    drive(master_speed,0.35)                    

                else:
                    # silver is in any other angle at the back of the robot

                    P_control_distance(0.1,0.01,100)
 
        else:

            print("GOLDEN is closer")

            if golden_counter==0 :
                
                # if it's the first time the robot has to deal with a gold token after having encountered a silver token 
                # or after having driven staight for  while, the robot saves its initial heading and makes sure to 
                # stop its  maneuvers if the new heading it has reached is pointing the robot back from where it came
                turn_counter=0
                first_decision=""
                initial_heading=compass()
                print(f"initial heading is:{initial_heading}\n")
                avoid=angle_correction(initial_heading+180)
                print(f"avoid angle is : {avoid}")
                max_avoid=angle_correction(avoid+70)
                min_avoid=angle_correction(avoid-70)
                if(min_avoid>max_avoid):
                    #this is here to write  reasonable interval
                    temp=min_avoid
                    min_avoid=max_avoid
                    max_avoid=temp
                print("I will avoid going between "+str(min_avoid)+" and "+str(max_avoid)+"\n")

            # print(str(avoid))

            golden_counter += 1

            dist=d_golden
            ang=a_golden

            if in_range(ang,-90,90):

                # closest gold token is "in sight" of the bot
                if in_range(ang,-45,45) and dist>0.7:
                    drive(master_speed,0.003)
                else:
                    
                    # scan_blocks() decides wether to turn left or right
                    turn_speed=scan_blocks()*master_speed
                    turn(turn_speed,0.008)
                    turn_counter +=1
                    print(f"CONSECUTIVE TURNS= {turn_counter}\n")
                    
                    if turn_speed<0:
                        last_decision="left"
                    else:
                        last_decision="right"
                    
                    if turn_counter==1:
                        first_decision=last_decision
                        first_heading=compass()
                    
                
                check_and_correct_heading(initial_heading,avoid,last_decision)   

                # if no clear decision has been tken in a while change heading drastically based on the first bad decision taken
                if turn_counter>300:
                    turn_counter=0
                    print("CAN'T FIND A WAY\n")

                    if first_decision=="right":

                        drive(-20,0.1)
                        print(f"was going at {first_heading} now pointing at {angle_correction(first_heading-55)}\n")
                        P_control_angle(first_heading-55,0.1,1,"absolute")

                    else:
                        
                        drive(-20,0.1)
                        P_control_angle(first_heading+55,0.1,1,"absolute")
                        print(f"was going at {first_heading} now pointing at {angle_correction(first_heading+55)}\n")
                        


                if (dist<=0.5 and in_range(ang,-30,30)):

                    # the bot got wound up in a logic loop and has gotten too close to the walls 

                    print("[EMERGENCY MANEUVER]")
                    print("Backing up from the closest golden block")
                    P_control_angle(ang,0.2,1,'relative')
                    drive(-master_speed,0.5)

                    if last_decision=="right":

                        P_control_angle(initial_heading+random.uniform(1,30),0.1,1,"absolute")
                   
                    elif last_decision=="left":

                        P_control_angle(initial_heading-random.uniform(1,30),0.1,1,"absolute")

            else:
                
            # there's a gold token close by but it's not in the way of the robot
         
                print("driving straight")
                drive(master_speed,0.1)
                if abs(angle_correction(compass()-avoid))>110:
                    golden_counter=0
                

main()