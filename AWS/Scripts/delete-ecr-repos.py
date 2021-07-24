import boto3

word = "eyeextend"

client = boto3.client('ecr')


response = client.describe_repositories(
    registryId='591607213837',
    maxResults=123
)

repo_list = []

for item in range(len(response['repositories'])):
    if response['repositories'][item]['repositoryName'].startswith(word):
        repo_list.append(response['repositories'][item]['repositoryName'])


for i in repo_list:
    client.delete_repository(
        registryId='591607213837',
        repositoryName=i,
        force=True
    )
    print(f"{i} Deleted")





