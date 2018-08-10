import rospy, rostopic

bw = rostopic.ROSTopicBandwidth(-1)
rospy.sleep(1)
bw.print_hz(['/plaintext'])


def listener():

    rospy.init_node('topic_bandwidth', anonymous=True)
    s = rospy.Subscriber('/plaintext', String, bw.callback_bw, callback_args='/plaintext')                                   
    rospy.spin() #keeps python from exiting until this node is stopped

if __name__ == '__main__':
    listener()
