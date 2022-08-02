import json
import boto3
import os

regionName = os.environ['AWS_REGION']
topicArn = os.environ['TOPIC_ARN']
BUCKET_PATH = os.environ['BUCKET_PATH']
s3_client = boto3.client('s3', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)
reko_client = boto3.client('rekognition', region_name=regionName)
sns_client = boto3.client('sns', region_name=regionName)

def lambda_handler(event, context):
    jobIDMessage = json.loads(event['Records'][0]['Sns']['Message'])
    jobID = jobIDMessage['JobId']
    response = reko_client.get_face_search(
        JobId=jobID
    )

    result = response

    while "NextToken" in response:
        NEXT_TOKEN = response['NextToken']
        response = reko_client.get_face_search(
            JobId=jobID,
            NextToken=NEXT_TOKEN
        )
        i = 0
        while i < len(response['Persons']):
            result['Persons'].append(response['Persons'][i])
            i = i+1
    else:
        pass

    with open('/tmp/summary.json', 'w') as w:
        json.dump(result, w, indent=2)
        w.close()
    
    facesSearchTable = ddb_resource.Table(os.environ['FACE_SEARCH_TABLE'])
    getItem = facesSearchTable.get_item(
        Key={
            'jobId': jobID
        },
        ProjectionExpression='VideoPath, People'
        )
        
    People = getItem['Item']['People']
    externalID = (getItem['Item']['VideoPath'].split('/')[-1]).split('.')[0]
    BUCKET = BUCKET_PATH.split('/')[2]
    OBJECT = '/'.join(BUCKET_PATH.split('/')[3:])+externalID+".json"
    
    s3_client.upload_file("/tmp/summary.json", BUCKET, OBJECT)
    
    facesSearchTable.update_item(
        Key={
            'jobId': jobID
        },
        UpdateExpression="set ResultPath = :r",
        ExpressionAttributeValues={
            ':r': "s3://" + BUCKET + '/' + OBJECT
            }
        )
    
    output = {'JobId':  jobID,
              'VideoPath': getItem['Item']['VideoPath'],
              'ResultPath':   "s3://" + BUCKET + '/' + OBJECT,
              'People': People}
    
    sns_client.publish(
        TopicArn=topicArn,
        Subject="Fasce Searching Succeed",
        Message=json.dumps(output, indent=2))
        
    return {
        'statusCode': 200,
        'body': json.dumps(output, indent=2)
    }
