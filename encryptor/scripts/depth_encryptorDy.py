#!/usr/bin/env python
import rospy
import os
import time
import base64
from sensor_msgs.msg import Image
from std_msgs.msg import String
from Crypto.Cipher import Salsa20
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import psutil

pub = rospy.Publisher('encryptedDepth', Image, queue_size=20)
exchannel = rospy.Publisher('exrequest', String, queue_size=20)
message = Image()

pub_list = []

key = ""

def key_exchange_listener(data):
    global message
    global pub_list
    key = data.data #Assigns the body of the message to the variable 'key'

    pub_list.append(key)
    if psutil.cpu_percent() <= 6:
        message.data = salsaEncypt32(message.data, key) #Calls the salsaEncypt function and assigns the ouput to variable 'plain_str'
    else:
        message.data = salsaEncypt16(message.data, key)

        
    pub_list = []
    pub.publish(message) #Publishs plain_str to topic /encrypted


def salsaEncypt32(message, serial_peer_public_key):
    global pub_list
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend()) #Generates private key
    public_key = private_key.public_key() #Generates public key from private key

    serial_public_key = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo) #Serializes public key so it can be sent as a ROS message 
    peer_public_key = serialization.load_pem_public_key(serial_peer_public_key, backend=default_backend()) #Deserializes the public key from the peer so it can be used to derive shared key
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key) #Shared key generated from local private key and the peer's public key
    

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=None,
        backend=default_backend()).derive(shared_key) #Key to be used to encrypt the data is dericed using HKDF

    pub_list.append(serial_public_key)
    
    cipher = Salsa20.new(key=derived_key) #A new Salsa20 cipher object is created using the derived key
    ciphertext = cipher.encrypt(message)
    msg_nonce=cipher.nonce
    mode = "32"
    return serial_public_key +"SPACE"+ ciphertext + "SPACE" +msg_nonce + "SPACE" + mode#Return public key and encrypted message seperated with 'SPACE'

def salsaEncypt16(message, serial_peer_public_key):
    global pub_list
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend()) #Generates private key
    public_key = private_key.public_key() #Generates public key from private key

    serial_public_key = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo) #Serializes public key so it can be sent as a ROS message 
    peer_public_key = serialization.load_pem_public_key(serial_peer_public_key, backend=default_backend()) #Deserializes the public key from the peer so it can be used to derive shared key
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key) #Shared key generated from local private key and the peer's public key
    

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=16,
        salt=None,
        info=None,
        backend=default_backend()).derive(shared_key) #Key to be used to encrypt the data is dericed using HKDF

    pub_list.append(serial_public_key)
    
    cipher = Salsa20.new(key=derived_key) #A new Salsa20 cipher object is created using the derived key
    ciphertext = cipher.encrypt(message)
    msg_nonce=cipher.nonce
    mode = "16"
    return serial_public_key +"SPACE"+ ciphertext + "SPACE" +msg_nonce+ "SPACE"+ mode#Return public key and encrypted message seperated with 'SPACE'

def depth_talker(data):
    global key
    global message
    rate = rospy.Rate(20) 

  
    message = data # Assigns message body to variable 'message'
    while not  rospy.is_shutdown():
        exchannel.publish("request")#Publishes "request" to topic /exrequest to request recievers public key
        rate.sleep()


def depth_listener():
  rospy.init_node('depth_encryptor', anonymous=True)
  rospy.Subscriber("camera/depth/image_raw", Image, depth_talker)
  rospy.Subscriber('exsent',String, key_exchange_listener)
  rospy.spin()

if __name__ == '__main__':
  depth_listener()
