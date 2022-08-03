import json
import boto3
import os, sys, logging
from fnmatch import fnmatchcase as match

logger = logging.getLogger()
logger.setLevel(logging.INFO)

regionName = os.environ['AWS_REGION']
resultBucketPath = os.environ['RESULT_BUCKET']
topicArn = os.environ['TOPIC_ARN']
s3_client = boto3.client('s3', region_name=regionName)
sns_client = boto3.client('sns', region_name=regionName)

Stop_Mark = ['，', '。', '！']

def lambda_handler(event, context):
    
    print(event)
    
    RekoJSON_PATH = event['Rekognition_S3']
    TranJSON_PATH = event['Transcription_S3']
    
    RekoJSON_BUCKET = RekoJSON_PATH.split('/')[2]
    RekoJSON_OBJECT = '/'.join(RekoJSON_PATH.split('/')[3:])
    s3_client.download_file(RekoJSON_BUCKET, RekoJSON_OBJECT, '/tmp/reko.json')
    
    TranJSON_BUCKET = TranJSON_PATH.split('/')[2]
    TranJSON_OBJECT = '/'.join(TranJSON_PATH.split('/')[3:])
    s3_client.download_file(TranJSON_BUCKET, TranJSON_OBJECT, '/tmp/tran.json')
    
    Seg_Obj = open('/tmp/reko.json')
    Seg = json.load(Seg_Obj)
    Seg_Obj.close()
    
    TranSub_Obj = open('/tmp/tran.json')
    TranSub = json.load(TranSub_Obj)
    TranSub_Obj.close()
    
    TranSub_EndTime = []
    i = 0
    
    while i < len(TranSub['results']['items']):
        if ('end_time' in TranSub['results']['items'][i]):
            TranSub_EndTime.append(TranSub['results']['items'][i]['end_time'])
        elif (TranSub['results']['items'][i]['alternatives'][0]['content'] in Stop_Mark):
            TranSub_EndTime.append(TranSub['results']['items'][i]['alternatives'][0]['content'])
        else:
            TranSub_EndTime.append('Mark')
        i = i+1
    
    Scenes = []
    content = {"Segments": Scenes}
    i = 0
    j = 0
    k = 0
    while i<len(Seg['Segments']):
        targetTime = str(Seg['Segments'][i]['EndTimestampMillis'] / 1000).split('.')[0]
        a = [num for num in TranSub_EndTime if match(num, str(targetTime) + ".*")]  # 找出所有符合要求的时间点
        while a == []:
            targetTime = int(targetTime) - 1
            a = [num for num in TranSub_EndTime if match(num, str(targetTime) + ".*")]
        else:
            pass
    
        if ('start_time' in TranSub['results']['items'][j]):
            Start_Time = TranSub['results']['items'][j]['start_time']
        else:
            Start_Time = TranSub['results']['items'][j+1]['start_time']
        StartMil = int(float(Start_Time)*1000)
        print(a)
        End_Time = a[-1]
        EndMil = int(float(End_Time)*1000)
        DurationMil = EndMil - StartMil
        
        j = TranSub_EndTime.index(a[-1]) + 1
        
        msg = ""
        while k<=j:
            msg=msg+TranSub['results']['items'][k]['alternatives'][0]['content']
            k=k+1
    
        Sce_Detail = {
            "Type": "Subtitle_Seg",
            "StartTimestampMillis": StartMil,
            "EndTimestampMillis": EndMil,
            "DurationMillis": DurationMil,
            "Subtitles": msg
        }
        
        Scenes.append(Sce_Detail)
        i = i+1
        
        FILE_FULL_PATH = '/tmp/' + event['Job_Name'] + 'segSub.json'
        
    with open("/tmp/summary.json", 'w') as w:
        json.dump(content, w, indent=2, ensure_ascii=False)
        w.close()
        
    BUCKET = resultBucketPath.split('/')[2]
    OBJECT = '/'.join(resultBucketPath.split('/')[3:]) + event['Job_Name'] + '-segSub.json'
    s3_client.upload_file("/tmp/summary.json", BUCKET, OBJECT)
    
    output = {
        'Message': "Segment Subtitle File has been created, you may download it from below link",
        'S3_Path': resultBucketPath + event['Job_Name'] + '-segSub.json'
    }
    
    sns_client.publish(
        TopicArn=topicArn,
        Subject="Fasce Searching Succeed",
        Message=json.dumps(output))

    return {
        'statusCode': 200,
        'body': json.dumps(output)
    }
