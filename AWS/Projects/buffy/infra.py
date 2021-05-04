import pprint
import boto3
import os
from termcolor import colored
import kubernetes

### divide to classes to run separate parts
### get tf state from s3 per env
### sync with terraform state - Pizdez!
### check target group port vs istio service nodePort and print port

### show all deployments and the revision


profile = os.environ.get('AWS_PROFILE')
cluster_name = os.environ.get('CLUSTER_NAME')
region = os.environ.get('AWS_REGION')

if profile is not 'None':
    session = boto3.session.Session(profile_name=profile, region_name=region)
else:
    session = boto3.session.Session(region_name=region,
                                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

def get_cluster_info(cluster_name):
    client = session.client('eks')
    cluster_info = client.describe_cluster(
        name=cluster_name
    )
    return cluster_info

def cluster_public_subnets(vpc):
    client = session.client('ec2')
    public_subnets = client.describe_subnets(
        Filters=[
            {
                'Name': f'tag:kubernetes.io/cluster/{cluster_name}',
                'Values': ['shared']
            },
            {
                'Name': f'tag:kubernetes.io/role/elb',
                'Values': ['1']
            }
        ]
    )
    ### add what tags are missing

    if not public_subnets['Subnets']:
        print(colored("[WARNING] No Public Subnets with appropriate tags detected", "red"))
    sub_list = []
    for sub in public_subnets['Subnets']:
        free_ips = sub["AvailableIpAddressCount"]
        if free_ips < 500:
            print(f'  [*] {sub["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "red"))
        else:
            print(f'  [*] {sub["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "green"))
        sub_list.append(sub["SubnetId"])
    return sub_list

def cluster_private_subnets(vpc):
    client = session.client('ec2')
    public_subnets = client.describe_subnets(
        Filters=[
            {
                'Name': f'tag:kubernetes.io/cluster/{cluster_name}',
                'Values': ['shared']
            },
            {
                'Name': f'tag:kubernetes.io/role/internal-elb',
                'Values': ['1']
            }
        ]
    )
    list = []
    for sub in public_subnets['Subnets']:
        free_ips = sub["AvailableIpAddressCount"]
        if free_ips < 500:
            print(f'  [*] {sub["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "red"))
        else:
            print(f'  [*] {sub["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "green"))
        list.append(sub["SubnetId"])
    return list

def get_public_route_tables(pub_subnets):
    print(colored("[SYSTEM] Checking Public Subnets for IGW Route Table...", "yellow"))
    client = session.client('ec2')
    is_public = False
    try:
        route_table_info = client.describe_route_tables(
            Filters=[
                {
                    'Name': 'association.subnet-id',
                    'Values': [
                        pub_subnets[0]
                    ]
                }
            ]
        )
    except IndexError as e:
        print(colored("[WARNING] No Appropriate Public Subnets detected", "red"))

    try:
        for route in route_table_info["RouteTables"][0]["Routes"]:
            if 'GatewayId' in route:
                if route["GatewayId"].startswith('igw-'):
                    is_public = True
        if is_public:
            print(colored('[CHECK] Public Subnets Detected', "green"))
        else:
            print(colored('[WARNING] No Public Subnets with route to IGW', 'red'))
    except:
        print(colored("[WARNING] No Appropriate Public Subnets to examine ", "red"))

def list_load_balancers():
    client = session.client('elbv2')
    lb_list = []
    print(colored("[SYSTEM] Getting Load Balancers...", "yellow"))
    for lb in client.describe_load_balancers()['LoadBalancers']:
        lb_list.append(lb)
    for lb in lb_list:
        print(f"  [*] {lb['LoadBalancerArn']}")
        if lb['State']['Code'] != 'active':
            print(colored(f"      [*] Status: {lb['State']['Code']}", "red"))
            print(f"      [*] Type: {lb['Type']}")
            print(f"      [*] Scheme: {lb['Scheme']}")
            print(f"      [*] Host Name: {lb['DNSName']}")
            print(f"      [*] Hosted Zone: {lb['CanonicalHostedZoneId']}")
        else:
            print(colored(f"      [*] Status: {lb['State']['Code']}", "green"))
            print(f"      [*] Type: {lb['Type']}")
            print(f"      [*] Scheme: {lb['Scheme']}")
            print(f"      [*] Host Name: {lb['DNSName']}")
            print(f"      [*] Hosted Zone: {lb['CanonicalHostedZoneId']}")
    return lb_list

def load_balancer_info(lb_list):
    client = session.client('elbv2')
    tags_list = []
    print(colored('[SYSTEM] Getting Load Balancer Tags...', 'yellow'))
    dict_list = []
    for i in range(len(lb_list)):
        tags_list.append((client.describe_tags(
            ResourceArns=[lb_list[i]['LoadBalancerArn']]
        )))
    for o in range(len(tags_list)):
        # if not any(d['Key'] == f'kubernetes.io/cluster/{cluster_name}' for d in tags_list[o]['TagDescriptions'][0]['Tags']):
        #     print(colored(f"[WARNING] Non-Cluster Load Balancer Detected", "red"))
        #     print(f"  [*] {tags_list[o]['TagDescriptions'][0]['ResourceArn']}")
        #     print(f"      [*] {tags_list[o]['TagDescriptions'][0]['Tags']}")
        if any(d['Key'] == f'kubernetes.io/cluster/{cluster_name}' for d in tags_list[o]['TagDescriptions'][0]['Tags']):
            if any(d['Value'].startswith("istio-") for d in tags_list[o]['TagDescriptions'][0]['Tags']):
                print(colored(f"  [*] {tags_list[o]['TagDescriptions'][0]['ResourceArn']} - Istio LB", "yellow"))
                print(f"      [*] {tags_list[o]['TagDescriptions'][0]['Tags']}")
            else:
                print(f"  [*] {tags_list[o]['TagDescriptions'][0]['ResourceArn']}")
                print(f"      [*] {tags_list[o]['TagDescriptions'][0]['Tags']}")
    for h in range(len(tags_list)):
        if not any(d['Key'] == f'kubernetes.io/cluster/{cluster_name}' for d in tags_list[h]['TagDescriptions'][0]['Tags']):
            print(colored(f"[WARNING] Non-Cluster Load Balancer Detected", "red"))
            print(f"  [*] {tags_list[h]['TagDescriptions'][0]['ResourceArn']}")
            print(f"      [*] {tags_list[h]['TagDescriptions'][0]['Tags']}")

def route53_list():
    client = session.client('route53')
    zone_list = client.list_hosted_zones()
    zone_ids = []
    for i in zone_list['HostedZones']:
        zone_ids.append(i['Id'])
        print(f"  [*] {i['Name']}")
    return zone_ids

def route53_info(zone_names):
    client = session.client('route53')
    for i in zone_names:
        r = client.get_hosted_zone(
            Id=i
        )
        pprint.pprint(f" [*] {r['HostedZone']['Name']}")
        if r['HostedZone']['Config']['PrivateZone']:
            print(colored(f"      [*] Private Zone", "green"))
            print(f"      [*] Zone ID: {r['HostedZone']['Id'].strip('/hostedzone/')}")
        else:
            print(colored(f"      [*] Public Zone", "yellow"))
            print(f"      [*] Zone ID: {r['HostedZone']['Id'].strip('/hostedzone/')}")


print(colored('[SYSTEM] Checking EKS subnets...', 'yellow'))
cluster_subnets = get_cluster_info(cluster_name=cluster_name)
print(f"  [*] Cluster subnets are: {cluster_subnets['cluster']['resourcesVpcConfig']['subnetIds']}")
print(colored('[SYSTEM] Checking EKS VPC...', 'yellow'))
cluster_vpc = cluster_subnets['cluster']['resourcesVpcConfig']['vpcId']
print(f"  [*] Cluster VPC is: {cluster_vpc}")
print(colored('[SYSTEM] Checking Public Subnets...', 'yellow'))
pub_subnets = cluster_public_subnets(cluster_vpc)
get_public_route_tables(pub_subnets)
print(colored('[SYSTEM] Checking Private Subnets...', 'yellow'))
private_subnets = cluster_private_subnets(cluster_vpc)
list_lb = list_load_balancers()
load_balancer_info(lb_list=list_lb)
print(colored('[SYSTEM] Checking Route53 Hosted Zones...', 'yellow'))
zone_ids = route53_list()
print(colored('[SYSTEM] Getting Hosted Zones Information...', 'yellow'))
route53_info(zone_ids)


