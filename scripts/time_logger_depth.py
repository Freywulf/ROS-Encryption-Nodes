#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
import pandas as pd
import time

recieved_times = []
sent_times = []
diff = []
sent_time= None
recieved_time = None

def callbackSent(data):
    #global base 
    global sent_times
    recorded_time = rospy.get_time()   
    sent_times.append(recorded_time)

def callbackRecieved(data):
    #global base
    global recieved_times
    global sent_times
    global diff
    
    #data.data = float(data.data)
    recorded_time = rospy.get_time()
    recieved_times.append(recorded_time)
    #delay = recorded_time - data.data
    #diff.append(delay)
    

def printCSV():
    global recieved_times
    global sent_times
    global diff
    
    df = pd.DataFrame(recieved_times) 
    df.to_csv('endtoendtimeRECIEVED.csv', sep=',', encoding='utf-8')
    
    df2 = pd.DataFrame(sent_times) 
    df2.to_csv('endtoendtimeSENT.csv', sep=',', encoding='utf-8')

    i = 0
    for rec_t in recieved_times:
        delay = rec_t - sent_times[i]
        diff.append(delay)
        i = i + 1

    df3 = pd.DataFrame(diff) 
    df3.to_csv('endtoendtimeDIFF.csv', sep=',', encoding='utf-8')

def listener():
    global base
    global recieved_times
    rospy.init_node('time_logger', anonymous=True)
   # base = rospy.Time()
    rospy.Subscriber('/camera/depth/image_raw', Image, callbackSent)
    rospy.Subscriber('newDepthPlain', Image, callbackRecieved)
    rospy.on_shutdown(printCSV)

        
    rospy.spin()

if __name__ == '__main__':
    listener()

