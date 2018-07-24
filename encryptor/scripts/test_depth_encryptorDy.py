#!/usr/bin/env python
import rospy
import time
from sensor_msgs.msg import Image
from std_msgs.msg import String
from Crypto.Cipher import Salsa20
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import psutil

####GLOBAL VARIABLES#####

private_key = None
shared_key = None
derived_key = None
message = None
count = 1
mode = None
cipher = None

####PUBLISHERS####
pub = rospy.Publisher('encryptedDepth', Image, queue_size=20)
request = rospy.Publisher('exrequest', String, queue_size=20)

def key_exchange_talker():
    global private_key
    
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend()) #Generates private key
    public_key = private_key.public_key() #Generates public key from private key

    serialized_public = public_key.public_bytes( #Serializes public key object so that it can be sent
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)

    request.publish(serialized_public)
    print "change!"
    break

def key_exchange_listener(peer_public_key):
    global private_key
    global derived_key
    global cipher

    loaded_public_key = serialization.load_pem_public_key(peer_public_key, backend=default_backend())
    shared_key = private_key.exchange(ec.ECDH(), loaded_public_key) #Generates a shared key using the local
    if psutil.cpu_percent() =< 6:
        derived_key = HKDF( #Derives key to be used for decryption from shared key
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None, backend=default_backend()).derive(shared_key) 
        mode = "32"
    else:
        derived_key = HKDF( #Derives key to be used for decryption from shared key
            algorithm=hashes.SHA256(),
            length=16,
            salt=None,
            info=None,
            backend=default_backend()).derive(shared_key) 
        mode = "16"
    cipher = Salsa20.new(key=derived_key) #A new Salsa20 cipher object is created using the derived key

def salsaEncypt32(message):
    ciphertext = cipher.encrypt(message)
    msg_nonce=cipher.nonce

    return  ciphertext + "SPACE" +msg_nonce + "SPACE" + mode#Return public key and encrypted message seperated with 'SPACE'
        
def depth_talker(message):
    global cipher
    global mode
    global count
    msg_nonce = cipher.nonce
    message.data = cipher.encrypt(message.data) +"SPACE"+ msg_nonce + "SPACE" + mode
    pub.publish(message)
    if (count % 10) == 0:
        key_exchange_talker()
    print count
    
def depth_listener():
  rospy.init_node('depth_encryptor', anonymous=True)
  rospy.Subscriber("camera/depth/image_raw", Image, depth_talker)
  rospy.Subscriber('exsent',String, key_exchange_listener)
  rospy.spin()

if __name__ == '__main__':
  key_exchange_talker()
  depth_listener()
