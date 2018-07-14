# ROS-Encryption-Nodes
## Overview
These ROS packages were developed to capture messages going across the [Freenect's](http://wiki.ros.org/freenect_launch) "/camera/depth/image_raw", [usb_cam's](http://wiki.ros.org/usb_cam) "/usb_cam/image_raw", and talkerplain's (script in encryptor package that merely outputs random strings between 10 and 30 characters long) /plaintext topics to encrypt them and republish them (see figure one for general system model (sans key exchange)). While these packages were developed for research purposes (there's nothing stopping a hacker from merely subscribing to the plaintext topic for example) they may be useful insperation for developers wishing to employ cryptographic systems into their own projects. As of right know Salsa20 is the only algorithm implemented in this package however AES-CBC, AES-GCM, and Chacha20 will all soon be added as well. The Elliptic Curve Diffie-Hellman (ECDH) Key Exchange was chosen as the means to derive the keys to be used for encryption and decryption and was implemented to ensure perfect forward secrecy (general outline shown in figure two).

**Author: [Joshua Thomas], joshthomas660@gmail.com**

Figure One: Overview of Nodes and Topics
![General System Model](https://github.com/Freywulf/ROS-Encryption-Nodes/blob/master/images/System%20Diagram%20Sans%20Key%20Exchange.png)
Figure Two: Outline of ECDH Implementaion
![Key Exchange Outline](https://github.com/Freywulf/ROS-Encryption-Nodes/blob/master/images/Key%20Exchange%20Diagram.png)

## Running the Nodes
Follow the instructions [here](http://wiki.ros.org/ROS/Tutorials/CreatingPackage) to build the package for these scripts. After doing so running them is easy. Simply boot up your master node and depending on script you are running begin running either freenect , usb_cam or whatever text-based data you wish (you may use talkerplain.py if you wish to run text_encryptor.py with dummy data). After launch both the encryptor node(whether it by text_encryptor, depth_encryptor etc.) and decryptor node using the rosrun command and it should work. Below are examples of output from running talkerplain.py, text_encryptor.py and text_decryptor.py. 

Figure Three: Output of /plaintext Topic
![Key Exchange Outline](https://github.com/Freywulf/ROS-Encryption-Nodes/blob/master/images/plaintext.png)
Figure Four: Output of /encrypted Topic
![Key Exchange Outline](https://github.com/Freywulf/ROS-Encryption-Nodes/blob/master/images/encryptedTerminal.png)
Figure Five: Output of /newPlain Topic
![Key Exchange Outline](https://github.com/Freywulf/ROS-Encryption-Nodes/blob/master/images/newPlain.png)

