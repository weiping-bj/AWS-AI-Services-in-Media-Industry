import boto3
import datetime
import json
import os, sys, logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
BUCKET_PATH = os.environ['BUCKET_PATH']
templatePath = os.environ['TEMPLATE_PATH']
s3_client = boto3.client('s3', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)

def lambda_handler(event, context):
    VIDEO_PATH = event['videoPath']
    requesterName = event['requesterName']
    
    NOW_TIME = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    OUTPUT_NAME = '-' + requesterName + '-' + NOW_TIME
    
    JOB_BUCKET = templatePath.split('/')[2]
    JOB_OBJECT = '/'.join(templatePath.split('/')[3:])
    s3_client.download_file(JOB_BUCKET, JOB_OBJECT, '/tmp/job-template.json')
    
    scenesTime = []
    for time in event['timeSlot']:
        start = time['StartTime'] + ":00"
        end = time['EndTime'] + ":00"
        scenesTime.append((start,end))
    
    with open('/tmp/job-template.json', 'r') as r:
        template = json.load(r)
        for scene in scenesTime:
            template['Settings']['Inputs'][0]['InputClippings'].append(
                {'StartTimecode': scene[0], 'EndTimecode': scene[-1]})
        template['Settings']['Inputs'][0]['FileInput'] = VIDEO_PATH
        template['Settings']['OutputGroups'][0]['Outputs'][0]['NameModifier'] = OUTPUT_NAME
        template['Settings']['OutputGroups'][0]['OutputGroupSettings']['FileGroupSettings']['Destination'] = BUCKET_PATH
        with open('/tmp/job-all.json', 'w') as w:
            json.dump(template, w, indent=2)
        w.close()
    r.close()
    
    mediaconvert_client = boto3.client('mediaconvert',endpoint_url='https://q25wbt2lc.mediaconvert.us-east-1.amazonaws.com')
    
    with open("/tmp/job-all.json", "r") as jsonfile:
        job_object = json.load(jsonfile)
    
    response = mediaconvert_client.create_job(**job_object)
    
    ddbTable = ddb_resource.Table(os.environ['DDB_TABLE'])
    dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        ddbTable.put_item(
            Item={
                'DateTime': dateTime,
                'RequesterName': requesterName,
                'VideoPath': VIDEO_PATH,
                'TimeSlots': event['timeSlot'],
                'JobId': response['Job']['Id'],
                'JobTemplate': templatePath
            })
    except Exception as e:
        logger.error("Unable to insert data into DynamoDB table"+format(e))
        logger.error(e)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
