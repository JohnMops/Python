import boto3
import datetime

age = 30 # delete snapshots older then this value in days

def days_old(date):
    date_obj = date.replace(tzinfo=None)
    diff = datetime.datetime.now() - date_obj
    return diff.days

client = boto3.client('ec2', region_name='us-east-1')

snapshots = []
response = client.describe_snapshots(
    OwnerIds=[
        'self',
    ],
)

final = []
for ami in response['Snapshots']:
    create_date = ami['StartTime']
    snapshot_id = ami['SnapshotId']
    day_old = days_old(create_date)
    if day_old > age:
        final.append(snapshot_id)

print(len(final)) # checks the amount of snapshots in the list

for i in range(len(final)):
    client.delete_snapshot(
        SnapshotId=final[i]
    )

