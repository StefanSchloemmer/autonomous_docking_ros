#!/usr/bin/env python

import rospy
from std_msgs.msg import Float32

import math
import numpy
import sys
import termios
import time

# keyboard event Listener for better keypress
from pynput import keyboard

instructions = """
Stefan's thrust control Script for single engine boats in VORC Gazebo
#####################################################################
Reading from the keyboard and Publishing Thrust Commands and Angles!
---------------------------
Thrust:
  + increase = w
  - decrease = s
Angle:
  + right = d
  - left  = a
  
to increase/decrease the response for thrust and angle cmd by 10%
Thrust:
  + faster = j
  - slower = m
Angle:
  + faster = h
  - slower = n

CTRL-C to quit
"""

angleBindings = {
    'd': 1.0,
    'a': -1.0,
}

thrustBindings = {
    'w': 1.0,
    's': -1.0,
}

angleSetting = {
    'n': -1.0,
    'h': 1.0,
}

thrustSetting = {
    'm': -1.0,
    'j': 1.0,
}

global_key = ''
key_w = False
key_s = False
key_d = False
key_a = False

def on_press(key):
    global global_key
    
    global key_w
    global key_s
    global key_d
    global key_a
    
    if key == keyboard.Key.up:    key_w = True
    if key == keyboard.Key.down:  key_s = True    
    if key == keyboard.Key.left:  key_a = True    
    if key == keyboard.Key.right: key_d = True  
    try:
        global_key = key.char
    except AttributeError:
        # print('special key {0} pressed'.format(key))
        return

def on_release(key):
    global global_key
    
    global key_w
    global key_s
    global key_d
    global key_a
    
    if key == keyboard.Key.up:    key_w = False
    if key == keyboard.Key.down:  key_s = False    
    if key == keyboard.Key.left:  key_a = False    
    if key == keyboard.Key.right: key_d = False           
    
    global_key = ''
    if key == keyboard.Key.esc:
        # Stop listener
        return False

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()


# Implement getch function, which reads in 1 char from user input.
# Purposely different from teleop_twist_keyboard.py b/c of
# issues outputting to stdout when they both read from the input.
# Reference https://gist.github.com/houtianze/9e623a90bb836aedadc3abea54cf6747

def __gen_ch_getter(echo):
    def __fun():
        fd = sys.stdin.fileno()
        oldattr = termios.tcgetattr(fd)
        newattr = oldattr[:]
        try:
            if echo:
                # disable ctrl character printing, otherwise,
                # backspace will be printed as "^?"
                lflag = ~(termios.ICANON | termios.ECHOCTL)
            else:
                lflag = ~(termios.ICANON | termios.ECHO)
            newattr[3] &= lflag
            termios.tcsetattr(fd, termios.TCSADRAIN, newattr)
            ch = sys.stdin.read(1)
            if echo and ord(ch) == 127:  # backspace
                # emulate backspace erasing
                # https://stackoverflow.com/a/47962872/404271
                sys.stdout.write('\b \b')
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, oldattr)
        return ch

    return __fun


if __name__ == "__main__":
    # Setup getch function
    getch = __gen_ch_getter(False)
    # Setup ros publishers and node
    thrust_angle_pub = rospy.Publisher('main_thrust_angle', Float32, queue_size=1)
    thrust_cmd_pub = rospy.Publisher('main_cmd', Float32, queue_size=1)
    rospy.init_node('key2thrust_and_angle')

    # Initialize current angle and angle speed
    angle_speed = 0.2
    max_angle = rospy.get_param("~max_angle", math.pi / 2)
    curr_angle = 0.0

    thrust_speed = 0.05
    max_thrust = 1
    curr_thrust = 0.0

    num_prints = 0

    try:
        # Output instructions
        print(instructions)
        print('Max Angle: {}'.format(max_angle))
        while (1):
            time.sleep(1/10.0)
            # Read in pressed key
            # key = getch()
            key = global_key
            
            # ---- ANGLE ----
            if key in angleBindings.keys():
                # Increment angle, but clip it between [-max_angle, max_angle]
                curr_angle += angle_speed * angleBindings[key]
                curr_angle = numpy.clip(curr_angle,
                                        -max_angle, max_angle).item()
            elif key_d or key_a:
                curr_angle += angle_speed * (int(key_d) - int(key_a))
                curr_angle = numpy.clip(curr_angle,
                                        -max_angle, max_angle).item()
            else:
                # if no key is pressed, decrease the current angle setting
                curr_angle -= numpy.clip(curr_angle * angle_speed, -max_angle, max_angle).item()
            # angle setting:
            if key in angleSetting.keys():
                # Increment/decrement speed of angle change and print it
                angle_speed += (angleSetting[key] * 0.1 *
                                angle_speed)
                angle_speed = numpy.clip(angle_speed * angle_speed, -max_angle, max_angle).item()
                print('currently:\t'
                      'thruster angle speed {} '.format(angle_speed))

                # Reprint instructions after 14 speed updates
                if num_prints == 14:
                    print(instructions)
                num_prints = (num_prints + 1) % 15

           # ---- THRUST ----
            if key in thrustBindings.keys():
                # Increment thrust, but clip it between [-max_thrust, max_thrust]
                curr_thrust += thrust_speed * thrustBindings[key]
                curr_thrust = numpy.clip(curr_thrust,
                                         -max_thrust, max_thrust).item()
            elif key_w or key_s:
                curr_thrust += thrust_speed * (int(key_w) - int(key_s))
                curr_thrust = numpy.clip(curr_thrust,
                                         -max_thrust, max_thrust).item()
            else:
                # if no key is pressed, decrease the current thrust setting
                curr_thrust -= numpy.clip(curr_thrust * thrust_speed, -max_thrust, max_thrust).item()
                
             # thrust setting:
            if key in thrustSetting.keys():
                # Increment/decrement speed of thrust change and print it
                thrust_speed += (thrustSetting[key] * 0.1 *
                                 thrust_speed)
                thrust_speed = numpy.clip(thrust_speed, -max_thrust, max_thrust).item()
                print('currently:\t'
                      'thruster thrust speed {} '.format(thrust_speed))

                # Reprint instructions after 14 speed updates
                if num_prints == 14:
                    print(instructions)
                num_prints = (num_prints + 1) % 15

            if key == '\x03':
                break

            # Publish angle
            angle_msg = Float32()
            angle_msg.data = curr_angle
            thrust_angle_pub.publish(angle_msg)
            # Publish thrust
            thrust_msg = Float32()
            thrust_msg.data = curr_thrust
            thrust_cmd_pub.publish(thrust_msg)

    except Exception as e:
        print(e)

    finally:
        # Send 0 angle command at end
        angle_msg = Float32()
        angle_msg.data = 0
        thrust_angle_pub.publish(angle_msg)
        thrust_msg = Float32()
        thrust_msg.data = 0
        thrust_cmd_pub.publish(thrust_msg)
