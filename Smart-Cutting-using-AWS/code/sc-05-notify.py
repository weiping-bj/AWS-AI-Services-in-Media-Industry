import json
import os
import boto3

regionName = os.environ['AWS_REGION']
TOPIC_ARN = os.environ['TOPIC_ARN']
CF_URL = os.environ['CF_URL']
sns_client = boto3.client('sns', region_name=regionName)

def lambda_handler(event, context):
    
    object = event['Records'][0]['s3']['object']['key']
    fileName = object.split('/')[-1]
    requesterName = fileName.split('-')[1]
    downloadURL = "https://" + CF_URL + "/" + fileName
    
    output = {'requesterName': requesterName,
              'downloadURL': downloadURL}
    
    sns_client.publish(
        TopicArn=TOPIC_ARN,
        Subject="ClippingFinished",
        Message=json.dumps(output, indent=2))
    
    
    
    return json.dumps(output, indent=2)