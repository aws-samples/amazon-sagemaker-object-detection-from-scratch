## Amazon Sagemaker Object Detection From Scratch <!-- omit in toc -->

Build a Custom Object Detection Model from Scratch with Amazon SageMaker and Deploy it at the Edge with AWS DeepLens. This workshop explains how you can leverage DeepLens to capture data at the edge and build a training data set with Amazon SageMaker Ground Truth. Then, train an object detection model with Amazon SageMaker and deploy it to AWS DeepLens.

This repository contains the code used during the namesake webinar broadcasted at the [AI & ML Web Day in July 11th 2019](https://pages.awscloud.com/EMEA-field-OE-ai-ml-web-day-2019-reg-event.html).


## Table of Contents <!-- omit in toc -->
- [Directory structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [How to deploy the Lambda functions](#how-to-deploy-the-lambda-functions)
  - [Mac/Linux users](#maclinux-users)
  - [Windows users](#windows-users)
- [How to run the trigger application](#how-to-run-the-trigger-application)
  - [Download the Greengrass Group CA certificate](#download-the-greengrass-group-ca-certificate)
  - [Run the trigger application](#run-the-trigger-application)
- [License](#license)

## Directory structure
```
.
├── LICENSE
├── README.md
├── deeplens                                # Contains the resources for functions to run on the AWS DeepLens device
│   ├── deployment                          # Deployment templates and scripts
│   │   ├── capture-template.yaml           # SAM template to deploy the picture capturing function
│   │   ├── deploy-capture-function.sh      # Bash script to automate the deployment of the picture capturing function to AWS Lambda
│   │   ├── deploy-inference-function.sh    # Bash script to automate the deployment of the inference function to AWS Lambda
│   │   └── inference-template.yaml         # SAM template to deploy the picture inference function
│   └── src                                 # Source code of the functions
│       ├── capture
|       |   ├── capture.py                  # Source code for the picture capturing function
|       |   └── requirements.txt            # Dependencies for the picture capturing function
│       └── inference
|           └── inference.py                # Source code for the inference function
|           └── requirements.txt            # Dependencies for the inference function
├── notebook
│   └── finger_counting.ipynb               # Jupyter notebook to train and deploy the object detection model
└── trigger                                 # Contains the resources for the application that triggers the picture capture and validation
    ├── certs                               # Directory to place the certificates for the AWS IoT Thing that represents the trigger
    └── src                                 # Source code for the trigger application
        ├── get_gg_ca_cert.py               # Utility to download the root CA certificate of the Greengrass Group the DeepLens device belongs to
        └── trigger_app.py                  # Source code for the trigger application
```
## Prerequisites
In order to run this solution you need:
 - Python 3.x
 - The [AWS CLI](https://aws.amazon.com/cli/) installed and configured with permissions to:
   - Create CloudFormation stacks.
   - Create an S3 bucket.
   - Create/update Lambda functions.
   - Attach an IAM policy to the DeepLensGreengrassGroupRole role.
   - List and get Greengrass groups certificate authorities.
 - [AWS SAM CLI installed](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
 - An Amazon S3 bucket to which you have write access.
  
## How to deploy the Lambda functions
Clone or download this Git repository to a local directory and follow the instructions below.

### Mac/Linux users
1. Give execution permissions to the .sh files in the ./deeplens/deployment directory
```
chmod +x ./deeplens/deployment/*.sh
```
2. Run the following commands from the **deeplens/deployment** directory (substitute the arguments between <> with appropriate ones):

```./deploy-capture-function.sh --bucket <your-s3-bucket-name> --stack-name <your-stack-name>```
```./deploy-inference-function.sh --bucket <your-s3-bucket-name> --stack-name <your-stack-name>```


### Windows users

1. Open a terminal window
   1. Press windows key + r
   2. Introduce cmd and press enter
2. Go to the **deeplens/deployment** folder and run the following commands:
   1. ```sam build -t capture-template.yaml```
   2. ```sam package --region us-east-1 --s3-bucket <your-s3-bucket> --output-template-file packaged-template.yaml;``` (substitute  ```<your-s3-bucket>``` with the S3 bucket name where SAM can upload the package)
   3. ```sam deploy --region us-east-1 --template-file ./packaged-template.yaml --stack-name <your-stack-name> --capabilities CAPABILITY_NAMED_IAM;``` (substitute ```<your-stack-name>``` with an appropriate name for your CloudFormation Stack)

## How to run the trigger application

This application requires the following Python packages:
 - OpenCV (```pip install python-opencv```)
 - AWS IoT Device SDK for Python (```pip install awsiotpythonsdk```)
 - Numpy (```pip install numpy```)

Once you have registered an AWS IoT Thing, download the private key and the certificate and place them in the **trigger/certs** folder.
Rename the private key file to ```private.pem.key``` and the certificate file to ```certificate.pem.crt```.

You also need the certificate of the root CA in the Greengrass group of your DeepLens.

### Download the Greengrass Group CA certificate

1. Go to the Greengrass Console and click on Groups. Click on the DeepLens group and then on Settings.
2. Copy the Group ID.
3. Open the *get_gg_ca_cert.py* file in your favorite text editor and substitute ```<YOUR_GREENGRASS_GROUP_ID>``` with the Group Id you copied.
4. Go to the **trigger** directory and run ```python src/get_gg_ca_cert.py```

### Run the trigger application

1. Go to the **trigger** directory and run ```python src/trigger_app.py```
2. The application will open a new window that may be hidden, so switch applications (alt+tab) and you'll see a Python application.
3. Once in that window, click *'y'* to save a picture, *'q'* to quit the application, or any other key to ignore the current picture and request a new one.

## License

This library is licensed under the Apache 2.0 License. 