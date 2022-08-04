import json
import os
import boto3

regionName = os.environ['AWS_REGION']

translate_client = boto3.client('translate', region_name=regionName)

def lambda_handler(event, context):

    print(event)
    
    Job_IDs = event
    Job_Status = []
    
    
    for id in Job_IDs:
        job_response = translate_client.describe_text_translation_job(JobId=id)
        Job_Status.append(job_response['TextTranslationJobProperties']['JobStatus'])
    
    for status in Job_Status:
        if status!='COMPLETED':
            TaskResult = 'IN_PROGRESS'
            break
        else:
            TaskResult = 'COMPLETED'
    
    return {
        'Status_Source': 'Translate',
        'Job_Status': TaskResult
    }
