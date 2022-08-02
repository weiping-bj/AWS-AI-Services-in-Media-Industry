import json
import boto3
import os, sys, logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
s3_client = boto3.client('s3', region_name=regionName)
ddb_resource = boto3.resource('dynamodb', region_name=regionName)
reko_client = boto3.client('rekognition', region_name=regionName)

def lambda_handler(event, context):
#    body = json.loads(event['body'])
    body = event
    collectionId = str(body['collectionId'])
    bucketPath = str(body['bucketPath'])
    comments = str(body['comments'])
    
    collections = reko_client.list_collections()
    result = collections['CollectionIds']
    
    while 'NextToken' in collections:
        NEXT_TOKEN = collections['NextToken']
        collections = reko_client.list_collections(NextToken=NEXT_TOKEN)
        result.append(collections['CollectionIds'])
    else:
        pass
    
    if collectionId in result:
        output = {'Result':  "Creation ERROR",
                  'Reason':  "Collection has already been exist, pls choose another collectionId",
                  'CollectionID':   collectionId}
    else:
        output = collectionCreation(collectionId, bucketPath, comments)
    
    return {
        'statusCode': 200,
        'body': json.dumps(output)
    }
    
    
def collectionCreation(collectionid, bucketpath, comments):
    bucketname = bucketpath.split('/')[2]
    bucketprefix = '/'.join(bucketpath.split('/')[3:])
    
    facePics = s3_client.list_objects_v2(
        Bucket=bucketname,
        Prefix=bucketprefix,
        Delimiter="/"
    )
    
    numbers = len(facePics['Contents'])
    people = []
    reko_client.create_collection(CollectionId=collectionid)
    
    i = 0
    while i < len(facePics['Contents']):
        externalId = (facePics['Contents'][i]['Key'].split('/')[-1]).split('.')[0]
        if externalId == '':
            numbers = numbers-1
        else:
            people.append(externalId)
            reko_client.index_faces(
                CollectionId=collectionid,
                Image={
                    'S3Object': {
                        'Bucket': bucketname,
                        'Name': facePics['Contents'][i]['Key']
                    }
                },
                ExternalImageId=externalId
                )
        i = i+1
    
    collectionTable = ddb_resource.Table(os.environ['COLLECTION_TABLE'])
    try:
        collectionTable.put_item(
            Item={
                'CollectionId': collectionid,
                'FacesCount': numbers,
                'PicsPath': "s3://" + bucketname + "/" + bucketprefix,
                'People': people,
                'Comments': comments
            })
    except Exception as e:
        logger.error("Unable to insert data into DynamoDB table"+format(e))
        logger.error(e)
    
    output = {'CollectionId':  collectionid,
              'Faces Counts': numbers,
              'Pics Path':   "s3://" + bucketname + "/" + bucketprefix}

    return json.dumps(output, indent=2)