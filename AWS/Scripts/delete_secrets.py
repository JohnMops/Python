import boto3
import pprint
import os

profile = "iris-acceptance"

client = boto3.session.Session(profile_name=profile, region_name="us-east-1").client('secretsmanager')


r = client.list_secrets(
    MaxResults=1,
)

s_list = []

for i in range(len(r['SecretList'])):
    s_list.append(r['SecretList'][i]['Name'])

while 'NextToken' in r:
    r = client.list_secrets(
        MaxResults=1,
        NextToken=r['NextToken']
    )
    for k in range(len(r['SecretList'])):
        s_list.append(r['SecretList'][k]['Name'])


for d in range(len(s_list)):
    client.delete_secret(
        SecretId=s_list[d],
        ForceDeleteWithoutRecovery=True
    )
    print("deleting " + s_list[k])