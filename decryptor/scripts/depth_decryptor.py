#!/usr/bin/env python
import rospy
from Crypto.Cipher import Salsa20
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from std_msgs.msg import String
from cryptography.hazmat.primitives import serialization
from bitarray import bitarray




private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
pub = rospy.Publisher('newDepthPlain', String, queue_size=1)
pub2 = rospy.Publisher('exsent',String,queue_size=1)
message = ""


#Callback function for key exchange requests
def exchange(request): 
    global private_key

    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend()) #Creates new private key 


    public_key = private_key.public_key() #Creates public key from previously created private key



    serialized_public = public_key.public_bytes( #Serializes public key object so that it can be sent as a ROS message
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)







    pub2.publish(serialized_public) #Publishes serialized public key to topic /exsent

#This function takes a cipher text message and private key as inputs and returns the decrypted plaintext
def decryptSalsa(message, key):

    message = str(message.data) #Converts the message's ciphertext to a string
    message = message.split("SPACE") #Splits the message by the word 'SPACE' to seperate the peer public key and ciphertext message


    peer_public_key = message[0] #Assigns the portion before SPACE to variable peer_public_key

    loaded_public_key = serialization.load_pem_public_key(peer_public_key, backend=default_backend()) #Unserialized the peer public key so that is usable for decryption

    ciphertext = message[1] #Assigns the portion after SPACE to variable ciphertext
 


ros services
    shared_key = key.exchange(ec.ECDH(), loaded_public_key) #Generates a shared key using the local private key and the senders public key

    derived_key = HKDF( #Derives key to be used for decryption from shared key
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=None,
        backend=default_backend()
    ).derive(shared_key) 
     



    msg_nonce = ciphertext[:8] #Seperates the nonce from the ciphertext
    cipher_text = ciphertext[8:] #Seperates the cipher text from the nonce



    cipher = Salsa20.new(key=derived_key, nonce= msg_nonce) #Creates Salsa20 cipher object from derived key and nonce
    result = cipher.decrypt(cipher_text) #decrypts the message using the cipher object and stores result in variable named 'result'


    return result #returns plaintext message


#Callback function that is triggered when a message is recieved from the /encrypted topic
# talker() takes the message, decrypts it, and republishes it to the topic called /newPlain
def talker(message):
    global data
    global private_key 
 

    
    plain = decryptSalsa(message, private_key) #calls the decryptSalsa function on encrypted message to retrieve plaintext and assigns result to 'plain'

    pub.publish(plain) #Publishes plaintext message to topic /newPlain
      

def listener():

    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber('exrequest', String, exchange) #Subscribes to /exrequest topic that recieves requests for public keys


    rospy.Subscriber('depthEncrypted', String, talker) #Subsribes to /encrypted topic that recieves encrypted messages from sender
                                                           
    rospy.spin() #keeps python from exiting until this node is stopped




if __name__ == '__main__':
    listener()
