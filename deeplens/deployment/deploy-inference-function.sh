#!/bin/bash

# This script installs the inference function for use within DeepLens.
# Usage: ./deploy-inference-function.sh --bucket <bucketname> --stack-name <stackname>
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
        if sam package --region us-east-1 --template-file ./inference-template.yaml --s3-bucket "${BUCKETNAME}" --output-template-file packaged-template.yaml; then
            # Deploy the CloudFormation template
            sam deploy --region us-east-1 --template-file ./packaged-template.yaml --stack-name "${STACKNAME}" --capabilities CAPABILITY_NAMED_IAM;

            # Remove the intermediate template
            rm ./packaged-template.yaml;
        fi
    fi
fi