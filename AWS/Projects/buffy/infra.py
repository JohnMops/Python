import pprint
import boto3
import os
import sys
from termcolor import colored
from more_itertools import unique_everseen
import kubernetes

### divide to classes to run separate parts
### check target group port vs istio service nodePort and print port



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
    try:
        cluster_info = client.describe_cluster(
            name=cluster_name
        )
        return cluster_info
    except:
        print(colored(f"[WARNING] No cluster {cluster_name} found", "red"))
        sys.exit()


def cluster_public_subnets(public_subnets):
    client = session.client('ec2')
    elb_tag = []
    cluster_tag = []
    elb_tag.append(client.describe_subnets(
        Filters=[
            {
                'Name': f'tag:kubernetes.io/role/elb',
                'Values': ['1']
            },
        ],
        SubnetIds=public_subnets,
    ))
    elb_tag_ids = []
    for sub in range(len(elb_tag[0]['Subnets'])):
        elb_tag_ids.append(elb_tag[0]['Subnets'][sub]['SubnetId'])
    for sub in range(len(public_subnets)):
        if public_subnets[sub] not in elb_tag_ids:
            print(colored(f"[WARNING] {public_subnets[sub]} is missing [kubernetes.io/role/elb]:[1] Tag ", "red"))

    cluster_tag.append(client.describe_subnets(
        Filters=[
            {
                'Name': f'tag:kubernetes.io/cluster/{cluster_name}',
                'Values': ['shared']
            },
        ],
        SubnetIds=public_subnets,
    ))
    cluster_tag_ids = []
    for sub in range(len(cluster_tag[0]['Subnets'])):
        cluster_tag_ids.append(cluster_tag[0]['Subnets'][sub]['SubnetId'])
    for sub in range(len(public_subnets)):
        if public_subnets[sub] not in cluster_tag_ids:
            print(colored(f"[WARNING] {public_subnets[sub]} is missing [kubernetes.io/cluster/{cluster_name}]:['shared'] Tag ", "red"))

    if not elb_tag_ids:
        print(colored("[WARNING] No Public Subnets related to Public LB with [kubernetes.io/role/elb]:[1] Tag detected", "red"))
    if not cluster_tag_ids:
        print(colored("[WARNING] No Public Subnets related to Public LB with [kubernetes.io/cluster/{cluster_name}]:['shared'] Tag detected", "red"))

    sub_list = []
    for sub in range(len(elb_tag[0]['Subnets'])):
        free_ips = elb_tag[0]['Subnets'][sub]["AvailableIpAddressCount"]
        if free_ips < 500:
            print(f'  [*] {elb_tag[0]["Subnets"][sub]["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "red"))
        else:
            print(f'  [*] {elb_tag[0]["Subnets"][sub]["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "green"))
        sub_list.append(elb_tag[0]["Subnets"][sub]["SubnetId"])
    return sub_list

def cluster_private_subnets(private_subnets):
    client = session.client('ec2')
    elb_tag = []
    cluster_tag = []
    elb_tag.append(client.describe_subnets(
        Filters=[
            {
                'Name': f'tag:kubernetes.io/role/internal-elb',
                'Values': ['1']
            },
        ],
        SubnetIds=private_subnets,
    ))
    elb_tag_ids = []
    for sub in range(len(elb_tag[0]['Subnets'])):
        elb_tag_ids.append(elb_tag[0]['Subnets'][sub]['SubnetId'])
    for sub in range(len(private_subnets)):
        if private_subnets[sub] not in elb_tag_ids:
            print(colored(f"[WARNING] {private_subnets[sub]} is missing [kubernetes.io/role/internal-elb]:[1] Tag ", "red"))

    cluster_tag.append(client.describe_subnets(
        Filters=[
            {
                'Name': f'tag:kubernetes.io/cluster/{cluster_name}',
                'Values': ['shared']
            },
        ],
        SubnetIds=private_subnets,
    ))
    cluster_tag_ids = []
    for sub in range(len(cluster_tag[0]['Subnets'])):
        cluster_tag_ids.append(cluster_tag[0]['Subnets'][sub]['SubnetId'])
    for sub in range(len(private_subnets)):
        if private_subnets[sub] not in cluster_tag_ids:
            print(colored(f"[WARNING] {private_subnets[sub]} is missing [kubernetes.io/cluster/{cluster_name}]:['shared'] Tag ", "red"))

    if not elb_tag_ids:
        print(colored("[WARNING] No Private Subnets with [kubernetes.io/role/internal-elb]:[1] Tag detected", "red"))
    if not cluster_tag_ids:
        print(colored("[WARNING] No Private Subnets with [kubernetes.io/cluster/{cluster_name}]:['shared'] Tag detected", "red"))

    sub_list = []
    for sub in range(len(elb_tag[0]['Subnets'])):
        free_ips = elb_tag[0]['Subnets'][sub]["AvailableIpAddressCount"]
        if free_ips < 500:
            print(f'  [*] {elb_tag[0]["Subnets"][sub]["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "red"))
        else:
            print(f'  [*] {elb_tag[0]["Subnets"][sub]["SubnetId"]}')
            print(colored(f"      [*] Available IPs: {free_ips}", "green"))
        sub_list.append(elb_tag[0]["Subnets"][sub]["SubnetId"])
    return sub_list


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
        print(colored("[WARNING] No LB Public Subnets related to Public LB detected", "red"))

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
        print(colored("[WARNING] No LB Public Subnets to examine", "red"))

def list_load_balancers_internal():
    client = session.client('elbv2')
    lb_list_internal = []
    print(colored("[SYSTEM] Getting Private Load Balancers...", "yellow"))
    for lb in client.describe_load_balancers()['LoadBalancers']:
        if lb['Scheme'] == 'internal':
            lb_list_internal.append(lb)
    if not lb_list_internal:
        print(colored("[WARNING] No Load Balancers detected", "red"))
    for lb in lb_list_internal:
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
    return lb_list_internal

def list_load_balancers_internal_subnets():
    client = session.client('elbv2')
    lb_list_external = []
    for lb in client.describe_load_balancers()['LoadBalancers']:
        if lb['Scheme'] == 'internal':
            lb_list_external.append(lb)
    if not lb_list_external:
        print(colored("[WARNING] No Private Load Balancers detected", "red"))
    sub_list = []
    for i in lb_list_external:
        for k in i['AvailabilityZones']:
            sub_list.append(k['SubnetId'])
    return list(unique_everseen(sub_list))

def list_load_balancers_external():
    client = session.client('elbv2')
    lb_list_external = []
    print(colored("[SYSTEM] Getting Public Load Balancers...", "yellow"))
    for lb in client.describe_load_balancers()['LoadBalancers']:
        if lb['Scheme'] == 'internet-facing':
            lb_list_external.append(lb)
    if not lb_list_external:
        print(colored("[WARNING] No Public Load Balancers detected", "red"))
    for lb in lb_list_external:
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
    return lb_list_external

def list_load_balancers_external_subnets():
    client = session.client('elbv2')
    lb_list_external = []
    for lb in client.describe_load_balancers()['LoadBalancers']:
        if lb['Scheme'] == 'internet-facing':
            lb_list_external.append(lb)
    if not lb_list_external:
        print(colored("[WARNING] No Public Load Balancers detected", "red"))
    sub_list = []
    for i in lb_list_external:
        for k in i['AvailabilityZones']:
            sub_list.append(k['SubnetId'])
    return list(unique_everseen(sub_list))

def private_load_balancer_info(list_lb_private):
    client = session.client('elbv2')
    tags_list = []
    print(colored('[SYSTEM] Getting Private Load Balancer Tags...', 'yellow'))
    dict_list = []
    if list_lb_private:
        for i in range(len(list_lb_private)):
            tags_list.append((client.describe_tags(
                ResourceArns=[list_lb_private[i]['LoadBalancerArn']]
            )))
        for o in range(len(tags_list)):
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
    else:
        print(colored("[WARNING] No Load Balancers detected", "red"))


def public_load_balancer_info(list_lb_public):
    client = session.client('elbv2')
    tags_list = []
    print(colored('[SYSTEM] Getting Public Load Balancer Tags...', 'yellow'))
    dict_list = []
    for i in range(len(list_lb_public)):
        tags_list.append((client.describe_tags(
            ResourceArns=[list_lb_public[i]['LoadBalancerArn']]
        )))
    for o in range(len(tags_list)):
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

def attached_sg(sg_list):
    client = session.client('ec2')
    print(colored('[SYSTEM] Checking Cluster Security Group for [0.0.0.0/0] open rules...', 'yellow'))
    attached = client.describe_security_groups(
        GroupIds=sg_list,
    )
    if attached:
        for g in range(len(attached['SecurityGroups'])):
            for p in range(len(attached['SecurityGroups'][g]['IpPermissions'])):
                for i in range(len(attached['SecurityGroups'][g]['IpPermissions'][p]['IpRanges'])):
                    if attached['SecurityGroups'][g]['IpPermissions'][p]['IpRanges'][i]['CidrIp'] == '0.0.0.0/0':
                        print(colored(f"[WARNING] {attached['SecurityGroups'][g]['GroupId']} open:", "red"))
                        try:
                            print(colored(f"  [*] {attached['SecurityGroups'][g]['IpPermissions'][p]['IpRanges'][i]['CidrIp']}", "yellow"))
                            print(colored(f"  [*] Description: {attached['SecurityGroups'][g]['IpPermissions'][p]['IpRanges'][i]['Description']}", "yellow"))
                            print(colored(f"  [*] Protocol: {attached['SecurityGroups'][g]['IpPermissions'][p]['IpProtocol']}", "yellow"))
                        except:
                            continue
    else:
        print(colored(f"[SYSTEM] No Cluster Related Security group found", "yellow"))

def cluster_instances():
    client = session.client('ec2')
    print(colored('[SYSTEM] Getting a list of Security groups attached to Cluster Nodes...', 'yellow'))
    instance_iterator = client.describe_instances(
        Filters=[
            {
                'Name': f'tag:kubernetes.io/cluster/{cluster_name}',
                'Values': ['owned'],
            }
          ]
    )
    sg_list = []
    for reservation in instance_iterator['Reservations']:
        for instance in reservation['Instances']:
            for group in instance['SecurityGroups']:
                sg_list.append(group['GroupId'])
    attached = client.describe_security_groups(
        GroupIds=list(unique_everseen(sg_list)),
    )
    for group in range(len(attached['SecurityGroups'])):
        print(colored(f"  [*] {attached['SecurityGroups'][group]['GroupId']}:"))
        print(colored(f"      [*] Description: {attached['SecurityGroups'][group]['Description']}", "yellow"))
    return list(unique_everseen(sg_list))





print(colored('[SYSTEM] Checking EKS subnets...', 'yellow'))
cluster_subnets = get_cluster_info(cluster_name=cluster_name)
print(f"  [*] Cluster subnets are: {cluster_subnets['cluster']['resourcesVpcConfig']['subnetIds']}")
print(colored('[SYSTEM] Checking EKS VPC...', 'yellow'))
cluster_vpc = cluster_subnets['cluster']['resourcesVpcConfig']['vpcId']
print(f"  [*] Cluster VPC is: {cluster_vpc}")
list_lb_private = list_load_balancers_internal()
list_lb_public = list_load_balancers_external()
private_load_balancer_info(list_lb_private=list_lb_private)
public_load_balancer_info(list_lb_public=list_lb_public)
lb_public_subnets = list_load_balancers_external_subnets()
lb_private_subnets = list_load_balancers_internal_subnets()
print(colored('[SYSTEM] Checking Public LB Subnets...', 'yellow'))
public_subnets = cluster_public_subnets(lb_public_subnets)
get_public_route_tables(lb_public_subnets)
print(colored('[SYSTEM] Checking Private LB Subnets...', 'yellow'))
private_subnets = cluster_private_subnets(lb_private_subnets)
sg_list = cluster_instances()
attached_sg(sg_list)
print(colored('[SYSTEM] Checking Route53 Hosted Zones...', 'yellow'))
zone_ids = route53_list()
print(colored('[SYSTEM] Getting Hosted Zones Information...', 'yellow'))
route53_info(zone_ids)





