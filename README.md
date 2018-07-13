# ROS-Encryption-Nodes
## Overview
These ROS packages were developed to capture messages going across the Freenect's "/camera/depth/image_raw", usb_cam's "/usb_cam/image_raw", and talkerplain's (script in encryptor package that merely outputs random strings between 10 and 30 characters long) /plaintext topics to encrypt them and republish them. While these packages were developed for research purposes they may be useful to developers wishing to employ cryptographic systems into their own projects. As of right know Salsa20 is the only algorithm implemented in this package however AES-CBC, AES-GCM, and Chacha20 will all soon be added as well. The Elliptic Curve Diffie-Hellman (ECDH) Key Exchange was chosen as the means to derive the keys to be used for encryption and decryption and was implemented to ensure perfect forward secrecy. 

**Author: [Joshua Thomas], joshthomas660@gmail.com**
