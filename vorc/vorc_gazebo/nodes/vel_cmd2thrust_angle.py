#!/usr/bin/env python
# license removed for brevity

import sys
import rospy
import math
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32

class Node():
    def __init__(self, a=3.1, max_thrust=0.15, vel_thust_scale=0.15, vel_angle_scale=0.4,):
        self.thrust_pub = None
        self.angle_pub = None
        self.thrust_msg = None
        self.angle_msg = None
        # a.. distance between baseframe and motor
        self.a = a
        # max_vel.. maximum velocity in %
        self.max_thrust = max_thrust
        # vel_thust_scale.. linear mapping of vel to thrust
        self.vel_thust_scale = vel_thust_scale
        # vel_angle_scale.. linear mapping of vel to angle
        self.vel_angle_scale = vel_angle_scale
    def callback(self,data):
        # data is vel_cmd twist in base_frame
        rospy.logdebug("RX: Twist "+rospy.get_caller_id())
        rospy.logdebug("\tlinear:")
        rospy.logdebug("\t\tx:%f,y:%f,z:%f"%(data.linear.x,
                                            data.linear.y,
                                            data.linear.z))
        rospy.logdebug("\tangular:")
        rospy.logdebug("\t\tx:%f,y:%f,z:%f"%(data.angular.x,
                                            data.angular.y,
                                            data.angular.z))
        
        vx = data.linear.x
        vy = data.linear.y - self.a*data.angular.z
        # get speed heading
        self.angle_msg.data = -math.atan2(-vy,vx)*self.vel_angle_scale
        # get speed magnitude
        self.thrust_msg.data = math.sqrt(math.pow(vx,2) + math.pow(vy,2))*self.vel_thust_scale
        # limit thust
        self.thrust_msg.data = max(min(self.thrust_msg.data, self.max_thrust), -self.max_thrust)
        # get the reverse direction if the desized velocity is in negative vx
        if vx < 0:
            self.thrust_msg.data = -self.thrust_msg.data
            
        rospy.logdebug("TX ")
        rospy.logdebug("\tthrust:%f, angle:%f"%( self.thrust_msg.data ,
                                              self.angle_msg.data))
        print("Thrust = " + str(self.thrust_msg.data) + ", Angle = " + str(self.angle_msg.data*180/math.pi) + " degrees")
        self.thrust_pub.publish(self.thrust_msg)
        self.angle_pub.publish(self.angle_msg)


if __name__ == '__main__':

    rospy.init_node('vel_cmd2thrust_angle', anonymous=True)
    node=Node()

    # Publisher
    node.thrust_pub = rospy.Publisher("main_cmd",Float32,queue_size=10)
    node.angle_pub = rospy.Publisher("main_thrust_angle",Float32,queue_size=10)
    node.thrust_msg = Float32()
    node.angle_msg = Float32()

    # Subscriber
    rospy.Subscriber("cmd_vel",Twist,node.callback)

    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
