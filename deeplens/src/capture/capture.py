# -*- coding: utf-8 -*-
#*****************************************************
#                                                    *
# Copyright 2019 Amazon.com, Inc. or its affiliates. *
# All Rights Reserved.                               *
#                                                    *
#*****************************************************

# capture.py
# This Lambda function, when receiving a "capture" message, takes a picture using the DeepLens camera,
# does some preprocessing, stores it in the /tmp directory with a unique id, and publishes it as a base64 encoded blob alongside its id.
# If it receives a "save" message with a valid unique id, it uploads the file from the /tmp directory to an S3 bucket configured as an environment variable.

# This Lambda function requires the AWS Greengrass SDK to run on Greengrass devices. This can be found on the AWS IoT Console.
# Additionally, this Lambda function needs the boto3 package to access S3.

from threading import Thread, Event
import os
import json
import cv2
import greengrasssdk
import boto3
import base64
import time
import random
import uuid
import traceback

# Create a greengrass core sdk client
iotclient = greengrasssdk.client('iot-data')

# Get an object for the S3 bucket
bucket_name = os.environ['BUCKET_NAME']
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)

# List of valid resolutions
RESOLUTION = {'1080p' : (1920, 1080), '720p' : (1280, 720), '480p' : (858, 480), 'training': (300, 300)}

def function_handler(event, context):
    # The event can have two actions: capture or save
    if event.get('action') == 'capture':
        capture()
    elif event.get('action') == 'save':
        pic_id = event.get('id')
        if pic_id:
            key = save_jpeg_to_s3(pic_id)
            iotclient.publish(
                topic='snap/keys',
                qos = 0,
                payload = json.dumps({ 'key': key }).encode())
    
def capture():
    thumbnail_topic = 'trigger/thumbnail'
    response = {}

    cam = cv2.VideoCapture('/opt/awscam/out/ch2_out.mjpeg')

    try:
        ret, frame = cam.read()
    except Exception as e:
        response['message'] = repr(e)

    if ret:
        try:
            pic_id = str(uuid.uuid4())
            frame = crop_frame_square(frame)
            jpeg = convert_to_jpg(frame, RESOLUTION['training'])
            save_jpeg_to_temp(jpeg, pic_id)
            response = {
                'id': pic_id,
                'thumbnail': base64.b64encode(bytearray(get_thumbnail(frame)))
            }
        except Exception:
            response['message'] = traceback.format_exc()
    else:
        response['message'] = 'No picture :('

    cam.release()

    return iotclient.publish(
        topic = thumbnail_topic,
        qos = 0,
        payload = json.dumps(response).encode()
    )

# This function crops the frame to a square, as the training algorithm uses squared pictures
# It does the crop from the center of the picture, taking the smaller side, which is the height
def crop_frame_square(frame):
    width = frame.shape[1]
    height = frame.shape[0]

    centre_x = int(width / 2)

    xmin = centre_x - int(height / 2)
    xmax = centre_x + int(height / 2)

    cropped = frame[0:height, xmin:xmax]

    return cropped

def get_thumbnail(frame):
    return(cv2.imencode('.jpg', cv2.resize(frame, RESOLUTION['training']))[1])
    
def convert_to_jpg(frame, resolution):
    """ Converts the captured frame to the desired resolution
    """
    ret, jpeg = cv2.imencode('.jpg', cv2.resize(frame, resolution))
    if not ret:
        raise Exception('Failed to set frame data')
    return jpeg

def save_jpeg_to_temp(jpeg, pic_id):
    file_name = '/tmp/{}'.format(pic_id)
    with open(file_name, 'wb') as f:
        f.write(jpeg)

def save_jpeg_to_s3(pic_id):
    file_name = '/tmp/{}'.format(pic_id)
    key = str(time.strftime("raw/%Y_%m_%d_%H_%M_%S.jpg")).format(random.randint(0, 999))

    with open(file_name, 'rb') as data:
        bucket.upload_fileobj(
            Fileobj=data,
            Key = key,
            ExtraArgs = {
                'ContentType': 'image/jpeg',
                'ACL': 'bucket-owner-full-control'
            })

    return key