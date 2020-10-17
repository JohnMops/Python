import boto3

region = 'us-east-1'
transfer_region = 'us-west-2'
parameters_final = []

def get_resources_from(ssm_details):
    results = ssm_details['Parameters']
    resources = [result for result in results]
    next_token = ssm_details.get('NextToken', None)
    return resources, next_token

def main():
    config = boto3.client('ssm', region_name=region)
    next_token = ' '
    resources = []
    while next_token is not None:
        ssm_details = config.describe_parameters(MaxResults=50, NextToken=next_token)
        current_batch, next_token = get_resources_from(ssm_details)
        resources += current_batch
    return resources



def get_parameter_with_values(parameters, region, parameters_final):
    client = boto3.client('ssm', region_name=region)
    for i in  range (len(parameters)):
        params = parameters[i]
        p = client.get_parameters(
            Names = [params['Name']]
        )
        parameters_final.append(p)
    return parameters_final

def upload_parameters(final_list, transfer_region):
    client = boto3.client('ssm', region_name=transfer_region)
    for i in range (len(final_list)):
        client.put_parameter(
            Name = final_list[i]['Parameters'][0]['Name'],
            Value = final_list[i]['Parameters'][0]['Value'],
            Type = final_list[i]['Parameters'][0]['Type'],
            Overwrite = True,
        )

def lambda_handler(event, context):
    parameters = main()
    final_list = get_parameter_with_values(parameters, region, parameters_final)
    upload_parameters(final_list, transfer_region)

