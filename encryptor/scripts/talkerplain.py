#!/usr/bin/env python
import rospy
from Crypto.Cipher import AES
from std_msgs.msg import String
import base64
import os
import random
import string
import random


def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))

def talker():
    pub = rospy.Publisher('plaintext', String, queue_size=1)
    exchannel = rospy.Publisher('exrequest', String, queue_size=1)

    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(1) 

    while not rospy.is_shutdown():

        choice = random.randint(10,30)
        message = random_char(choice) 

        pub.publish(message)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

