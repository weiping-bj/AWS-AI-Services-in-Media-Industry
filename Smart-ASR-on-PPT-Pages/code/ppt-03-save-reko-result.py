import json
import boto3
import os, sys, logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
rekoBucketPath = os.environ['INTER_BUCKET']
reko_client = boto3.client('rekognition', region_name=regionName)
s3_client = boto3.client('s3', region_name=regionName)

def lambda_handler(event, context):
    
    print(event)
    
    reko_response = reko_client.get_segment_detection(
        JobId=event['Reko_JobId']
    )
    
    fileName = '/tmp/reko.json'
    if len(reko_response['Segments']) < 100:
        with open(fileName, 'w') as w:
            json.dump(reko_response, w, indent=2)
        w.close
        message = 'Rekognition result has been saved'
    else:
        message = "Too many shots"
    
    NAME = event['Job_Name']
    BUCKET = rekoBucketPath.split('/')[2]
    OBJECT = '/'.join(rekoBucketPath.split('/')[3:]) + NAME + "-reko.json"
        
    s3_client.upload_file(fileName, BUCKET, OBJECT)    
        

    return {
        'Rekognition_S3': rekoBucketPath + NAME + "-reko.json",
        'Transcription_S3': event['Transcription_S3'],
        'Job_Name': event['Job_Name']
    }
