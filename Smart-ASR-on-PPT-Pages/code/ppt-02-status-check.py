import json
import boto3
import os, sys, logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
reko_client = boto3.client('rekognition', region_name=regionName)
tran_client = boto3.client('transcribe', region_name=regionName)

def lambda_handler(event, context):
    
    print(event)
    
    reko_response = reko_client.get_segment_detection(
        JobId=event['Reko_JobId']
    )
    
    tran_response = tran_client.get_transcription_job(
        TranscriptionJobName=event['Transcribe_JobName']
    )
    
    if reko_response['JobStatus'] == "SUCCEEDED" and tran_response['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        STATUS = "FINISHED"
    else:
        STATUS = "IN_PROGRESS"
    
    return {
        'Job_Status': STATUS,
        'Reko_JobId': event['Reko_JobId'],
        'Transcription_S3': event['Transcription_S3'],
        'Job_Name': event['Job_Name']
    }
