import json
import os, logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
S3Uri_OUTPUT = os.environ['INTER_BUCKET']
tableName = os.environ['TABLE_NAME']
roleARN = os.environ['ROLE_ARN']

translate_client = boto3.client('translate', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)

def lambda_handler(event, context):

    print(event)
    
    Source_TXT = event['CopySrt2TXT']['Caption_TXT_S3URI']
    Source_Lan = event['CopySrt2TXT']['Source_Lan']        
    Target_Lan = event['targetLanguageCodes']
    Transcribe_Job_Name = event['StartTranscribe']['Job_Name']
    
    S3Uri_INPUT = '/'.join(Source_TXT.split('/')[0:-1])
    prefix = Source_TXT.split('/')[-2]
    JOB_NAME = '-'.join([Source_TXT.split('/')[-2], (Source_TXT.split('/')[-1]).split('.')[0]])
    
    Job_IDs = []
    Job_IDs_DDB = []
    
    for language in Target_Lan:
        LanguageCode = [language]
        try:
            translate_response = translate_client.start_text_translation_job(
                JobName=JOB_NAME + '-' + language,
                InputDataConfig={
                    'S3Uri': S3Uri_INPUT,
                    'ContentType': 'text/plain'
                },
                OutputDataConfig={
                    'S3Uri': S3Uri_OUTPUT + prefix
                },
                DataAccessRoleArn=roleARN,
                SourceLanguageCode=Source_Lan,
                TargetLanguageCodes=LanguageCode
            )
        except Exception as e:
                logger.error("Unable to Start Translate Job: ")
                logger.error(e)
        Job_IDs.append(translate_response['JobId'])
        Item_Attr = {language: translate_response['JobId']}
        Job_IDs_DDB.append(Item_Attr)
    
    infoTable = ddb_resource.Table(tableName)

    try:
        infoTable.update_item(
            Key={
                'TranscribeJobName': Transcribe_Job_Name
            },
            UpdateExpression="set TranslationJobIds=:tjid",
            ExpressionAttributeValues={
                ':tjid': Job_IDs_DDB
            }
        )
    except Exception as e:
            logger.error("Unable to Update item in ddb table: ")
            logger.error(e)
    

    return {
        'Translate_Job_Ids': Job_IDs
    }
