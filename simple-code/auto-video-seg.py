import boto3
import json
import time

# input parameter
videoPath = '视频所在S3路径.mp4'

# Environment
outputPath = 's3://拆条后视频保存路径/'

# Initialization
reko_client = boto3.client('rekognition')
mediaconvert_client = boto3.client('mediaconvert',endpoint_url='当前账户下 mediaconvert 的 url')

# start rekognition job, segments detection
BUCKET = videoPath.split('/')[2]
OBJECT = '/'.join(videoPath.split('/')[3:])
reko_seg_response = reko_client.start_segment_detection(
    Video={
        'S3Object': {
            'Bucket': BUCKET,
            'Name': OBJECT
        }
    },
    SegmentTypes=['SHOT']
)
print(reko_seg_response)

# check rekognition job status
JOB_ID = reko_seg_response['JobId']
reko_job_response = reko_client.get_segment_detection(JobId=JOB_ID)
while reko_job_response['JobStatus'] == "IN_PROGRESS":
    time.sleep(10)
    reko_job_response = reko_client.get_segment_detection(JobId=JOB_ID)

NAME = (videoPath.split('/')[-1]).split('.')[0]
BUCKET_PATH = outputPath + NAME +'/'
# when error
if reko_job_response['JobStatus'] == 'FAILED':
    print("Segment job is failed")
else:
    seg_response = reko_client.get_segment_detection(JobId=JOB_ID)
    i = 0
    for seg in seg_response['Segments']:
        OUTPUT_NAME = NAME + '-' + str(i)
        StartTimeFrame = seg['StartTimecodeSMPTE']
        EndTimeFrame = seg['EndTimecodeSMPTE']
        with open('/tmp/job-template.json', 'r') as r:
            template = json.load(r)
            template['Settings']['Inputs'][0]['InputClippings'].append(
                {'StartTimecode': StartTimeFrame, 'EndTimecode': EndTimeFrame})
            template['Settings']['Inputs'][0]['FileInput'] = videoPath
            template['Settings']['OutputGroups'][0]['Outputs'][0]['NameModifier'] = OUTPUT_NAME
            template['Settings']['OutputGroups'][0]['OutputGroupSettings']['FileGroupSettings'][
                'Destination'] = BUCKET_PATH
            mediaconvert_client.create_job(**template)
        r.close()
        i = i + 1

    print("Video has been devided into: " + str(i))

