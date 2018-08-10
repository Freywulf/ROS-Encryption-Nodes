#!/usr/bin/env python
import rospy
from Crypto.Cipher import Salsa20
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cryptography.hazmat.primitives import serialization
import pandas as pd

import time

####GLOBAL VARIABLES####
private_key = None
shared_key = None
derived_key = None
message = None
count = 0
mode = None 

cipher = None
time_diff = []
batch_modulo = 200

switch = False
####PUBLISHERS####
pub = rospy.Publisher('newTextPlain', String, queue_size=30)
pub2 = rospy.Publisher('sent',String,queue_size=20)

#def printCSV():
    #global time_diff

##    i = 0
##    for rec_t in recieved_times:
##        delay = rec_t - sent_times[i]
##        diff.append(delay)
##        i = i + 1
    
    
   # df = pd.DataFrame(time_diff) 
    #df.to_csv('endtoendtimeDIFF.csv', sep=',', encoding='utf-8')

def key_exchange_listener(key_message):
    global private_key
    global derived_key

    key_message = str(key_message.data)
    key_message = key_message.split("SPACE")

    
    mode = key_message[0]
    peer_public_key = key_message[1]

    loaded_public_key = serialization.load_pem_public_key(peer_public_key, backend=default_backend())

    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend()) #Creates new private key 

    shared_key = private_key.exchange(ec.ECDH(), loaded_public_key) #Generates a shared key using the local
    if mode == "32":
        derived_key = HKDF( #Derives key to be used for decryption from shared key
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,
            backend=default_backend()).derive(shared_key) 
    else:
        derived_key = HKDF( #Derives key to be used for decryption from shared key
            algorithm=hashes.SHA256(),
            length=16,
            salt=None,
            info=None,
            backend=default_backend()).derive(shared_key) 

    public_key = private_key.public_key() #Creates public key from previously created private key

    serialized_public = public_key.public_bytes( 
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)


    pub2.publish(serialized_public)



def generate_cipher(key ,msg_nonce):
    global cipher
    global switch



    cipher = Salsa20.new(key=key, nonce=msg_nonce)
    switch = False

def talker(message):
    global count
    global derived_key
    global cipher
    global switch
    global batch_modulo
    global time_diff

   # rate = rospy.Rate(20)

    content = str(message.data)
    content = content.split("SPACE")

    ciphertext = content[0]
    nonce = content[1] 

    if (count % batch_modulo) == 0:
        switch = True
    if switch == True:
        generate_cipher(derived_key ,nonce)
        
    

    message.data = cipher.decrypt(ciphertext)

     
    pub.publish(message.data)

  #  message.data = float(message.data)
   # recorded_time = rospy.get_time()
   # delay = recorded_time - message.data
   # time_diff.append(delay) 


    count = count + 1

   # rate.sleep()



def listener():

    rospy.init_node('test_text_de', anonymous=True)
    rospy.Subscriber('request', String, key_exchange_listener) #Subscribes to /exrequest topic that recieves requests for public keys
    rospy.Subscriber('encryptedText', String, talker) #Subsribes to /encrypted topic that recieves encrypted messages from sender     
    #rospy.on_shutdown(printCSV)                                            
    rospy.spin() #keeps python from exiting until this node is stopped

if __name__ == '__main__':
    listener()


    




