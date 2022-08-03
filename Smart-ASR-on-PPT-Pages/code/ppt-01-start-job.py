import json
import boto3
import os, sys, logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
tranBucketPath = os.environ['INTER_BUCKET']
reko_client = boto3.client('rekognition', region_name=regionName)
tran_client = boto3.client('transcribe', region_name=regionName)

def lambda_handler(event, context):
    
    videoPath = str(event['videoPath'])
    print(videoPath)
    
    BUCKET = videoPath.split('/')[2]
    OBJECT = '/'.join(videoPath.split('/')[3:])
    NAME = (videoPath.split('/')[-1]).split('.')[0]
    
    
    reko_response = reko_client.start_segment_detection(
        Video={
            'S3Object': {
                'Bucket': BUCKET,
                'Name': OBJECT
            }
        },
        ClientRequestToken=NAME,
        SegmentTypes=['SHOT']
    )
    
    tranBucket = tranBucketPath.split('/')[2]
    tranKey = '/'.join(tranBucketPath.split('/')[3:]) + NAME + "-tran.json"
    
    tran_response = tran_client.start_transcription_job(
        TranscriptionJobName=NAME,
        Media={'MediaFileUri': videoPath},
        MediaFormat='mp4',
        LanguageCode='zh-CN',
        OutputBucketName=tranBucket,
        OutputKey=tranKey
    )

    
    return {
        'Reko_JobId': reko_response['JobId'],
        'Transcribe_JobName': tran_response['TranscriptionJob']['TranscriptionJobName'],
        'Transcription_S3': tranBucketPath + NAME + "-tran.json",
        'Job_Name': NAME
    }
