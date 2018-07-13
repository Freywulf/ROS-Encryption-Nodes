#!/usr/bin/env python

import rospy
import os
import time
import base64
from sensor_msgs.msg import Image
from Crypto.Cipher import Salsa20

pub = rospy.Publisher('encryptedVideo', Image, queue_size=10)


def salsaE(message):

  secret = os.urandom(32)
  
  cipher = Salsa20.new(key=secret, nonce=None)
  
  msg = cipher.encrypt(message)
  
  print(msg)
  return msg


def depth_talker(data):
  data.data = salsaE(data.data)

  pub.publish(data)


def depth_listener():
  rospy.init_node('depth_encryptor', anonymous=True)
  # rospy.Subscriber("/scan", LaserScan,callback)
  rospy.Subscriber("/usb_cam/image_raw", Image, depth_talker)
  rospy.spin()

if __name__ == '__main__':
  depth_listener()
