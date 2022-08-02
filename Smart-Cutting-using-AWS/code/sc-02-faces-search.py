import json
import os
import boto3

regionName = os.environ['AWS_REGION']
snsTopic = os.environ['SNS_TOPIC_ARN']
roleARN = os.environ['ROLE_ARN']
reko_client = boto3.client('rekognition', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)

def lambda_handler(event, context):
#    body = json.loads(event['body'])
    body = event
    collectionId = str(body['collectionId'])
    videoPath = str(body['videoPath'])
    comments = str(body['comments'])
    
    BUCKET = videoPath.split('/')[2]
    OBJECT = '/'.join(videoPath.split('/')[3:])
    
    jobID = reko_client.start_face_search(
        Video={
            'S3Object': {
                'Bucket': BUCKET,
                'Name': OBJECT
            }
        },
        CollectionId=collectionId,
        NotificationChannel={
            'SNSTopicArn': snsTopic,
            'RoleArn': roleARN
        }
        )
    JOBID = jobID['JobId']
    
    collectionTable = ddb_resource.Table(os.environ['COLLECTION_TABLE'])
    people = collectionTable.get_item(
        Key={
            'CollectionId': collectionId
        },
        ProjectionExpression='People'
        )
    People = people['Item']['People']
    
    facesSearchTable = ddb_resource.Table(os.environ['FACE_SEARCH_TABLE'])
    facesSearchTable.put_item(
        Item={
            'jobId': JOBID,
            'VideoPath': videoPath,
            'CollectionId': collectionId,
            'People': People
        })
    
    return {
        'statusCode': 200,
        'body': json.dumps(jobID)
    }