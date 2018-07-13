#!/usr/bin/env python

import rospy
from Crypto.Cipher import AES
from Crypto.Cipher import Salsa20
from std_msgs.msg import String
import base64
import os
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


pub = rospy.Publisher('encrypted', String, queue_size=1)
exchannel = rospy.Publisher('request', String, queue_size=1)

message = "" #Will be assigned to plaintext message from /plaintext
key = "" #Will be assigned to the public key of the peer

def key_exchange_listener(data):
    global key
    global message
    key = data.data #Assigns the body of the message to the variable 'key'
    cipher_str = salsaEncypt(message, key) #Calls the salsaEncypt function and assigns the ouput to variable 'plain_str'
    pub.publish(cipher_str) #Publishs plain_str to topic /encrypted   

##Function that derives key from ECDH key exchange and encrypts ROS message
#Inputs: ROS Message, Reciever public key
#Outputs: Public key for the reciever and Encrypted ROS Message
def salsaEncypt(message, serial_peer_public_key):
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
    

    cipher = Salsa20.new(key=derived_key) #A new Salsa20 cipher object is created using the derived key
    msg = cipher.nonce + cipher.encrypt(message) #The ROS message is encrypted and the cipher's nonce is added to the beginning of the message

    return serial_public_key +"SPACE"+ msg #Return public key and encrypted message seperated with 'SPACE'

##Callback Function that is called when message from topic /chatter is recieved. It takes in message data and sends request for key to reciever
def talker(data):
    global key
    global message
    message = data.data # Assigns message body to variable 'message'
    exchannel.publish("request")#Publishes "request" to topic /exrequest to request recievers public key

def listener():
     
   rospy.init_node('text_encryptor', anonymous=True)
   rospy.Subscriber('publickey',String, key_exchange_listener)
   rospy.Subscriber('plaintext', String, talker)
   rospy.spin()

if __name__ == '__main__':
    listener()
