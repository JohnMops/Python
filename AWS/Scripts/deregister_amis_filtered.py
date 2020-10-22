import boto3

import pprint

client = boto3.client('ec2')

filter = ["Lambda" + "*"]

response = client.describe_images(
    Filters=[
        {
            'Name': 'name', 'Values': filter
        }
    ],
    Owners=[
        'self',
    ],
)

image_count = []

if 'Images' in response:
    for img in response['Images']:
        image_count.append(img)

final = []

for i in range(len(image_count)):
    final.append(image_count[i]['ImageId'])

for k in range(len(final)):
    client.deregister_image(
        ImageId = final[k]
    )
