import os
import boto3
import urllib3
import json

http = urllib3.PoolManager()

def get_cloudflare_ip_list():

    response = http.request('GET','https://api.cloudflare.com/client/v4/ips')
    ips = json.loads(response.data.decode('utf-8'))
    if 'result' in ips and 'ipv4_cidrs' in ips['result']:
        return ips['result']['ipv4_cidrs']

    raise ConnectionError("Error loading IPs from CloudFlare")


def get_aws_security_group(group_id):

    ec2 = boto3.resource('ec2')
    group = ec2.SecurityGroup(os.environ['group_id'])
    if group.group_id == group_id:
        return group

    raise ConnectionError('Failed to retrieve security group from Amazon')


def check_rule_exists(rules, address, port):

    for rule in rules:
        for ip_range in rule['IpRanges']:
            if ip_range['CidrIp'] == address and rule['FromPort'] == port:
                return True
    return False


def add_rule(group, address, port, description):

    permissions = [
        {
            'IpProtocol': 'tcp',
            'FromPort': port,
            'ToPort': port,
            'IpRanges': [
                {
                    'CidrIp': address,
                    'Description': description,
                }
            ],
        }
    ]
    group.authorize_ingress(IpPermissions=permissions)
    print("Added %s : %i  " % (address, port))


def lambda_handler(event, context):

    ports = [80,443]

    security_group = get_aws_security_group(os.environ['group_id'])
    current_rules = security_group.ip_permissions
    ip_addresses = get_cloudflare_ip_list()
    description = "Authorize CloudFlare access"

    for ip_address in ip_addresses:
        for port in ports:
            if not check_rule_exists(current_rules, ip_address, port):
                add_rule(security_group, ip_address, port, description)