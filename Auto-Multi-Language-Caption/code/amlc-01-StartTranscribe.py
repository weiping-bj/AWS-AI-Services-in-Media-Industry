import json
import time
import os, sys, logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
tranBucketPath = os.environ['INTER_BUCKET']
tableName = os.environ['TABLE_NAME']

transcribe_client = boto3.client('transcribe', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)


def lambda_handler(event, context):

    print(event)
    
    videoPath = event['videoPath']
    
    tranPrefix = str(int(time.time()))
    
    BUCKET = videoPath.split('/')[2]
    OBJECT = '/'.join(videoPath.split('/')[3:])
    VIDEO_NAME = (videoPath.split('/')[-1]).split('.')[0]
    VIDEO_TYPE = videoPath.split('.')[-1]
    
    JOB_NAME = tranPrefix + '-' + VIDEO_NAME
    
    tranBucket = tranBucketPath.split('/')[2]
    tranKey = '/'.join(tranBucketPath.split('/')[3:]) + tranPrefix + '/' + VIDEO_NAME + "-tran.json"
    
    try:
        transcribe_response = transcribe_client.start_transcription_job(
            TranscriptionJobName=JOB_NAME,
            Media={'MediaFileUri': videoPath},
            MediaFormat=VIDEO_TYPE,
            OutputBucketName=tranBucket,
            OutputKey=tranKey,
            Subtitles={'Formats': ['srt']},
            IdentifyLanguage=True
        )
    except Exception as e:
            logger.error("Unable to Start Transcribe Job: ")
            logger.error(e)
    
    infoTable = ddb_resource.Table(tableName)

    try:
        infoTable.put_item(
            Item={
                'TranscribeJobName': transcribe_response['TranscriptionJob']['TranscriptionJobName'],
                'StartTime': transcribe_response['ResponseMetadata']['HTTPHeaders']['date'],
                'MediaS3Uri': transcribe_response['TranscriptionJob']['Media']['MediaFileUri']
            })
    except Exception as e:
        logger.error("Unable to insert data into DynamoDB table. Error messages: ")
        logger.error(e)
    
    

    
    return {
        'Job_Name': transcribe_response['TranscriptionJob']['TranscriptionJobName']
    }
