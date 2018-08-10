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
from bitarray import bitarray
import numpy as np


private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
pub = rospy.Publisher('newDepthPlain', Image, queue_size=20)
pub2 = rospy.Publisher('exsent',String,queue_size=20)
message = Image()

pub_list = []

#Callback function for key exchange requests
count1 = 0
def exchange(request): 
    global private_key
    global pub_list
    global count1

    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend()) #Creates new private key 

    public_key = private_key.public_key() #Creates public key from previously created private key

    serialized_public = public_key.public_bytes( #Serializes public key object so that it can be sent as a ROS message
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)

 #   pub_list.append("REQUESTED: " + serialized_public)
    count1 = count1 + 1
   # print count1
    pub2.publish(serialized_public) #Publishes serialized public key to topic /exsent


    

#This function takes a cipher text message and private key as inputs and returns the decrypted plaintext
def decryptSalsa(message, key):

    message = str(message) #Converts the message's ciphertext to a string
    message = message.split("SPACE") #Splits the message by the word 'SPACE' to seperate the peer public key and ciphertext message

    peer_public_key = message[0] #Assigns the portion before SPACE to variable peer_public_key

    
    loaded_public_key = serialization.load_pem_public_key(peer_public_key, backend=default_backend()) #Unserialized the peer public key so that is usable for decryption
    ciphertext = message[1] #Assigns the portion after SPACE to variable ciphertext
    msg_nonce=message[2]

    mode = message[3]

    shared_key = key.exchange(ec.ECDH(), loaded_public_key) #Generates a shared key using the local private key and the senders public key
  
    if mode == "32":
        derived_key = HKDF( #Derives key to be used for decryption from shared key
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,
            backend=default_backend()).derive(shared_key) 
    if mode == "16":
        derived_key = HKDF( #Derives key to be used for decryption from shared key
            algorithm=hashes.SHA256(),
            length=16,
            salt=None,
            info=None,
            backend=default_backend()).derive(shared_key) 

    cipher = Salsa20.new(key=derived_key, nonce=msg_nonce) #Creates Salsa20 cipher object from derived key and nonce
    result = cipher.decrypt(ciphertext) #decrypts the message using the cipher object and stores result in variable named 'result'

#    pub_list.append(peer_public_key)
   

    return result #returns plaintext message


#Callback function that is triggered when a message is recieved from the /encrypted topic
# talker() takes the message, decrypts it, and republishes it to the topic called /newPlain
count2 = 0
def talker(message):
    global data
    global private_key 
    global pub_list
    global count2

    key = private_key
 
    message.data = decryptSalsa(message.data, private_key) #calls the decryptSalsa function on encrypted message to retrieve plaintext and assigns result to 'plain'

 #   print pub_list
    pub.publish(message) #Publishes plaintext message to topic /newPlain
    count2 = count2 + 1
   # print "count2: " + str(count2)

  #  pub_list = []
      

def listener():
image_sub = message_filters.Subscriber('image', Image)
info_sub = message_filters.Subscriber('camera_info', CameraInfo)






    rospy.init_node('depth_decryptor', anonymous=True)

    request = rospy.Subscriber('exrequest', String, exchange) #Subscribes to /exrequest topic that recieves requests for public keys
    encrypted = rospy.Subscriber('encryptedDepth', Image, talker) #Subsribes to /encrypted topic that recieves encrypted messages from sender 

    ts = message_filters.TimeSynchronizer([request, encrypted], 30)                                                
    rospy.spin() #keeps python from exiting until this node is stopped

if __name__ == '__main__':
    listener()
