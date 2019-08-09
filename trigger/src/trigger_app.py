#*****************************************************
#                                                    *
# Copyright 2019 Amazon.com, Inc. or its affiliates. *
# All Rights Reserved.                               *
#                                                    *
#*****************************************************

# trigger_app.py
# This application acts as an IoT device in the AWS DeepLens Greengrass group.
# It triggers the camera to take a capture which is then published in a topic.
# The device consumes the message from the topic and shows it in the screen.
# The user then decides whether to keep it (pressing the letter 'y'), stop the app
# by pressing 'q', or drop it by pressing any other key

import logging
import queue
import base64
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import numpy as np
import cv2
import time

GREENGRASS_IP = "<your DeepLens's IP address>"

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Queue to receive the pictures from the DeepLens
thumbnail_queue = queue.Queue()

# For certificate based connection
mqttClient = AWSIoTMQTTClient("trigger")
# Configurations
# For TLS mutual authentication
mqttClient.configureEndpoint(GREENGRASS_IP, 8883)
# Make sure your certificates and key names are the same as below
mqttClient.configureCredentials("./certs/rootca.pem", "./certs/private.pem.key", "./certs/certificate.pem.crt")
mqttClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
mqttClient.configureDrainingFrequency(2)  # Draining: 2 Hz
mqttClient.configureConnectDisconnectTimeout(5)  # 5 sec
mqttClient.configureMQTTOperationTimeout(5)  # 5 sec

def main():
    try:
        connected = False
        logger.debug("Connecting")
        mqttClient.connect()
        connected = True
        mqttClient.subscribe('trigger/thumbnail', 0, process_thumbnail)
        logger.debug("Connected!")
    except BaseException as e:
        logger.error("Error in connect!")
        logger.exception(e)

    if connected:
        cv2.namedWindow("Input")

        while True:
            # Notify the camera to take a picture
            mqttClient.publish('trigger/snap', json.dumps({ 'action': 'capture' }), 0)

            # Wait until there is a thumbnail to show
            try:
                payload = thumbnail_queue.get()
            except Exception:
                pass
            
            if payload:
                thumbnail = payload.get('thumbnail')
                pic_id = payload.get('id')

                if thumbnail:
                    # Show the picture and wait for user input
                    pressed_key = str(chr(show_thumbnail(thumbnail) & 255)).lower()
                    if pressed_key == 'y':
                        logger.debug('Telling to store into S3')
                        # Notify the camera to save the picture
                        mqttClient.publish('trigger/snap', json.dumps({ 'action': 'save', 'id': pic_id }), 0)
                    elif pressed_key == 'q':
                        break
            else:
                time.sleep(5)
        cv2.destroyAllWindows()

def show_thumbnail(thumbnail):
    logger.debug(len(thumbnail))
    nparr = np.frombuffer(base64.b64decode(thumbnail), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow('image', img)
    
    return(cv2.waitKey(0))

def process_thumbnail(client, userdata, message):
    payload = json.loads(message.payload.decode())
    logger.debug('New message received: ')
    logger.debug(payload.get('id'))
    logger.debug("from topic: ")
    logger.debug(message.topic)
    logger.debug("--------------\n\n")

    thumbnail_queue.put(payload)

if __name__ == "__main__":
    main()
