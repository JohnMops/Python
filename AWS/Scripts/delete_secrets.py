import boto3
import pprint
import os

profile = "iris-research"

client = boto3.session.Session(profile_name=profile, region_name="us-east-1").client('secretsmanager')

def append_to_list(r, s_list):
    for k in range(len(r['SecretList'])):
        s_list.append(r['SecretList'][k]['Name'])

r = client.list_secrets(
    MaxResults=20,
)

s_list = []

append_to_list(r, s_list)

while 'NextToken' in r:
    r = client.list_secrets(
        MaxResults=20,
        NextToken=r['NextToken']
    )
    append_to_list(r, s_list)

print(os.system('aws sts get-caller-identity --profile iris-research'))
pprint.pprint(s_list)
for d in range(len(s_list)):
    client.delete_secret(
        SecretId=s_list[d],
        ForceDeleteWithoutRecovery=True
    )
    print("deleting " + s_list[d])