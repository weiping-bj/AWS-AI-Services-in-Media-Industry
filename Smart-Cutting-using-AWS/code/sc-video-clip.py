import json
import boto3
import os
import datetime
import sys

videoPath = sys.argv[1]
facePath = sys.argv[2]
targetPeople = sys.argv[3]
FRAME_RATE = 80

FACES_BUCKET = facePath.split('/')[2]
FACES_OBJECT = '/'.join(facePath.split('/')[3:])

BUCKET_PATH = 's3://'+FACES_BUCKET+'/output/'

s3_client = boto3.client('s3')
s3_client.download_file(FACES_BUCKET, FACES_OBJECT, 'faces.json')
facesJson = open('faces.json', 'r')
facesData = json.load(facesJson)

PEOPLE = targetPeople.split(',')

timeStamps = []
scenesTime = []
    
i = 0
while i < len(facesData['Persons']):
    try:
        for target in PEOPLE:
            if facesData['Persons'][i]['FaceMatches'] == []:
                pass
            elif facesData['Persons'][i]['FaceMatches'][0]['Face']['ExternalImageId'] == target.strip():
                timeStamps.append(facesData['Persons'][i]['Timestamp'])
    except IndexError:
        pass
    i = i+1
    
timeCollection = [[timeStamps[0]]]
i = 1
j = 0
while i < len(timeStamps):
    if timeStamps[i] - timeCollection[j][-1] <= 1000:
        timeCollection[j].append(timeStamps[i])
        i = i+1
    else:
        j = j+1
        timeCollection.append([timeStamps[i]])
            
for collection in timeCollection:
    if collection[-1] - collection[0] >= 1000:
        if collection[0] % 1000 == 0:
            start = datetime.datetime.utcfromtimestamp(collection[0]//1000).strftime("%H:%M:%S") + ':00'
        elif int(collection[0] % 1000 / 1000 * FRAME_RATE) < 10:
            start = datetime.datetime.utcfromtimestamp(collection[0] // 1000).strftime("%H:%M:%S") + ':0' + str(int(collection[0] % 1000 / 1000 * FRAME_RATE))
        else:
            start = datetime.datetime.utcfromtimestamp(collection[0]//1000).strftime("%H:%M:%S") + ':' + str(int(collection[0] % 1000 / 1000 * FRAME_RATE))
        if collection[-1] % 1000 == 0:
            end = datetime.datetime.utcfromtimestamp(collection[-1] // 1000).strftime("%H:%M:%S") + ':00'
        elif int(collection[-1] % 1000 / 1000 * FRAME_RATE) < 10:
            end = datetime.datetime.utcfromtimestamp(collection[-1] // 1000).strftime("%H:%M:%S") + ':0' + str(int(collection[-1] % 1000 / 1000 * FRAME_RATE))
        else:
            end = datetime.datetime.utcfromtimestamp(collection[-1] // 1000).strftime("%H:%M:%S") + ':' + str(int(collection[-1] % 1000 / 1000 * FRAME_RATE))
        scenesTime.append((start,end))
    else:
        pass

finalName = []
for people in PEOPLE:
    finalName.append(people.strip())
    
OUTPUT_NAME = '-'+'-'.join(finalName)

with open('resources/job-template.json', 'r') as r:
    template = json.load(r)
    for scene in scenesTime:
        template['Settings']['Inputs'][0]['InputClippings'].append({'StartTimecode': scene[0], 'EndTimecode': scene[-1]})
    template['Settings']['Inputs'][0]['FileInput'] = videoPath
    template['Settings']['OutputGroups'][0]['Outputs'][0]['NameModifier'] = OUTPUT_NAME
    template['Settings']['OutputGroups'][0]['OutputGroupSettings']['FileGroupSettings']['Destination'] = BUCKET_PATH
    with open('job-all.json', 'w') as w:
        json.dump(template, w, indent=2)
    w.close()
r.close()

mediaconvert_client = boto3.client('mediaconvert')

response = mediaconvert_client.describe_endpoints(Mode='DEFAULT')
    
mediaURL = response['Endpoints'][0]['Url']
    
mediaconvert_client = boto3.client('mediaconvert',endpoint_url=mediaURL)
    
with open("job-all.json", "r") as jsonfile:
    job_object = json.load(jsonfile)
    
mediaconvert_client.create_job(**job_object)

os.remove('faces.json')
os.remove('job-all.json')
    
output = {'videoPath': videoPath,
            'facePath': facePath,
            'targetPerson': targetPeople
}

print(json.dumps(event, indent=2))