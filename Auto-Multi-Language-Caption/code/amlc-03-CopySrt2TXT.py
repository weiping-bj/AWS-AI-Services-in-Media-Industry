import json
import os, logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
tranBucketPath = os.environ['INTER_BUCKET'] 
tableName = os.environ['TABLE_NAME']

Buffer_Bucket = tranBucketPath.split('/')[2]
Buffer_Folder = '/'.join(tranBucketPath.split('/')[3:])

transcribe_client = boto3.client('transcribe', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)
s3_client = boto3.client('s3', region_name=regionName)

def lambda_handler(event, context):
    
    print(event)

    
    transcribe_job_status = transcribe_client.get_transcription_job(TranscriptionJobName=event)
    
    Source_SRT = transcribe_job_status['TranscriptionJob']['Subtitles']['SubtitleFileUris'][0]
    Bucket_Value = Source_SRT.split('/')[3]
    Caption_Key = '/'.join(Source_SRT.split('/')[4:])
    Caption_S3URI = 's3://' + Bucket_Value + '/' + Caption_Key
    
    Transcript_Uri = transcribe_job_status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    Transcript_Key = '/'.join(Transcript_Uri.split('/')[4:])
    Transcript_S3URI = 's3://' + Bucket_Value + '/' + Transcript_Key
    
    prefix = Source_SRT.split('/')[-2]
    Video_Name = (Source_SRT.split('/')[-1]).split('.')[0]
    Video_Lan = transcribe_job_status['TranscriptionJob']['LanguageCode']

    copy_response = s3_client.copy_object(
        Bucket=Buffer_Bucket,
        CopySource={
            'Bucket': Bucket_Value,
            'Key': Caption_Key
        },
        Key=Buffer_Folder + prefix + '/' + Video_Name + '.txt'
    )
    
    Caption_TXT_S3URI = tranBucketPath + prefix + '/' + Video_Name + '.txt'
    
    infoTable = ddb_resource.Table(tableName)

    Caption_Lan = transcribe_job_status['TranscriptionJob']['LanguageCode'].split('-')[0]
    
    try:
        infoTable.update_item(
            Key={
                'TranscribeJobName': transcribe_job_status['TranscriptionJob']['TranscriptionJobName']
            },
            UpdateExpression="set OriginalLanguage=:ol, TranscriptS3Uri=:scriptS3, Caption_" + Caption_Lan + "=:cl",
            ExpressionAttributeValues={
                ':ol': transcribe_job_status['TranscriptionJob']['LanguageCode'],
                ':scriptS3': Transcript_S3URI,
                ':cl': Caption_S3URI
            }
        )
    except Exception as e:
            logger.error("Unable to Update item in ddb table: ")
            logger.error(e)
    
    
    return {
        'Caption_TXT_S3URI': Caption_TXT_S3URI,
        'Source_Lan': Video_Lan
    }
