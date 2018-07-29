import rospy
from Crypto.Cipher import AES
from std_msgs.msg import String
import base64
import os
from std_msgs.msg import String
import time
import pandas as pd
sent_times = []
recieved_times = []

def callbackSent(data):
    recorded_time = time.time()
    sent_times.append(recorded_time)
def callbackRecieved(data):
    recorded_time = time.time()
    recieved_times.append(recorded_time)

def listener():
    rospy.init_node('time_logger', anonymous=True)

    rospy.Subscriber('plaintext', String, callbackSent)
    rospy.Subscriber('newplaintext', String, callbackRecieved)
    while not rospy.is_shutdown():
        df = pd.DataFrame({'Messages Sent':sent_times,'Messages Recieved':recieved_times}) #Create dataframe
        
    rospy.spin()

if __name__ == '__main__':
    listener()
