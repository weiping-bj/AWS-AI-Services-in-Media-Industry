import json
import boto3
import os

regionName = os.environ['AWS_REGION']

transcribe_client = boto3.client('transcribe', region_name=regionName)

def lambda_handler(event, context):

    print(event)
    
    transcribe_job_status = transcribe_client.get_transcription_job(TranscriptionJobName=event)
    
    Job_Status = transcribe_job_status['TranscriptionJob']['TranscriptionJobStatus']
    
    print(Job_Status)

    return {
        'Status_Source': 'Transcribe',
        'Job_Status': Job_Status
    }
