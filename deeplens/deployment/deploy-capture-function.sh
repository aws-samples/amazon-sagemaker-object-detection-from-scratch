#!/bin/bash

# This script installs the dependencies for the Lambda for capturing and saving pictures function that will run on Greengrass,
# then, it packages the dependencies together with the Lambda function code and deploys it to AWS with AWS CloudFormation.
# It must be executed from the 'deployment' directory and receives two arguments: --bucket and --stack-name
# Usage: ./deploy-capture-function.sh --bucket <bucketname> --stack-name <stackname>

HELP="You must include --bucket (S3 bucket name) and --stack-name (CloudFormation stack name)"

for i in "$@"
do
    case $i in
    --bucket|-b|--bucket-name)
        BUCKETNAME="${2}"
        ;;
    --stack-name|-s|--stack)
        STACKNAME="${1}"
        ;;
    -h|--help)
        echo ${HELP}
        shift # past argument
        ;;
    *)    # unknown option
        POSITIONAL+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
    shift
done

if [ -z "$BUCKETNAME" -o -z "$STACKNAME" ]; then
    echo ${HELP}
else
    # Package the Lambda function
    if sam build -t capture-template.yaml; then
        # Transform the SAM template to an AWS CloudFormation template
        if sam package --s3-bucket "${BUCKETNAME}" --output-template-file packaged-template.yaml; then
            # Deploy the CloudFormation template
            sam deploy --template-file ./packaged-template.yaml --stack-name "${STACKNAME}" --capabilities CAPABILITY_NAMED_IAM;

            # Remove the intermediate template
            rm ./packaged-template.yaml;
        fi
    fi
fi