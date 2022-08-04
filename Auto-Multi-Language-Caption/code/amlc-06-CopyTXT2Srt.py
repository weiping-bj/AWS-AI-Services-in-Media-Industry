import json
import os, logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
S3Uri_OUTPUT = os.environ['INTER_BUCKET']
tableName = os.environ['TABLE_NAME']
Topic_Arn = os.environ['TOPIC_ARN']

translate_client = boto3.client('translate', region_name=regionName)
s3_client = boto3.client('s3', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)
sns_client = boto3.client('sns', region_name=regionName)

def lambda_handler(event, context):

    print(event)
    
    Job_IDs = event['StartTranslate']['Translate_Job_Ids']
    videoPath = event['videoPath']
    Job_Name = event['StartTranscribe']['Job_Name']
    
    VIDEO_NAME = (videoPath.split('/')[-1]).split('.')[0]
    
    infoTable = ddb_resource.Table(tableName)
    
    i = 0

    Translation_TXT_Output = []
    Translation_SRT_Output = []
    
    for job in Job_IDs:
        i = i + 1
        job_response = translate_client.describe_text_translation_job(JobId=job)
        Source_Lan = job_response['TextTranslationJobProperties']['SourceLanguageCode']
        Target_Lan = job_response['TextTranslationJobProperties']['TargetLanguageCodes'][0]
        Cap_TXT = job_response['TextTranslationJobProperties']['OutputDataConfig']['S3Uri'] + Target_Lan + '.' + VIDEO_NAME + '.txt'
        Job_txt_Output = {'TargetLanguageCode': Target_Lan, 'CapSrtS3Path': Cap_TXT}
        Translation_TXT_Output.append(Job_txt_Output)
    
        Bucket = job_response['TextTranslationJobProperties']['OutputDataConfig']['S3Uri'].split('/')[2]
        Source_Key = '/'.join(job_response['TextTranslationJobProperties']['OutputDataConfig']['S3Uri'].split('/')[3:]) + Target_Lan + '.' + VIDEO_NAME + '-tran.txt'
        print("Source Key is: " + Source_Key)
        Destination_Key = '/'.join(job_response['TextTranslationJobProperties']['OutputDataConfig']['S3Uri'].split('/')[3:5]) + '/' + Target_Lan + '.' + VIDEO_NAME + '-tran.srt'
        print("Destination Key is: " + Destination_Key)
    
        copy_response = s3_client.copy_object(
            Bucket=Bucket,
            CopySource={
                'Bucket': Bucket,
                'Key': Source_Key
            },
            Key=Destination_Key
        )
    
        try:            # copy 并改写文件格式之后，update ddb table
            infoTable.update_item(
                Key={
                    'TranscribeJobName': Job_Name
                },
                UpdateExpression="set Caption_" + Target_Lan + "=:tl",
                ExpressionAttributeValues={
                    ':tl': 's3://' + Bucket + '/' + Destination_Key
                }
            )
        except Exception as e:
            logger.error("Unable to Update item in ddb table: ")
            logger.error(e)
    
        SRT_Info = {'TargetLanguageCode': Target_Lan, 'CapSrtS3Path': 's3://' + Bucket + '/' + Destination_Key}
        Translation_SRT_Output.append(SRT_Info)
    
    Job_Output_Summary = {'TranslatedCaptionInformation': {'InputVideoS3Path': videoPath, 'SourceLanguageCode': Source_Lan, 'TranslatedCaptionCount': i, 'TranslatedOutput': Translation_SRT_Output}}
    
    sns_client.publish(
        TopicArn=Topic_Arn,
        Subject="ClippingFinished",
        Message=json.dumps(Job_Output_Summary, indent=2))
    
    return {
        'statusCode': 200,
        'body': json.dumps(Job_Output_Summary, indent=2)
    }
    