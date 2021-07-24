import pprint
import boto3
import os
from datetime import date
from datetime import datetime, timedelta
import time
from more_itertools import unique_everseen

import initiator.session as ses
import aws_module.functions as aws


profile = os.environ.get('AWS_PROFILE')
cluster_name = os.environ.get('CLUSTER_NAME')
region = os.environ.get('AWS_REGION')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

session = ses.Session(profile, region, aws_access_key_id, aws_secret_access_key)
session = session.start_session()

aws = aws.Funcs(session, cluster_name)

public_subnets = aws.list_load_balancers_external_subnets()
private_subnets = aws.list_load_balancers_internal_subnets()

aws.get_cluster_info()
aws.cluster_public_subnets(public_subnets)
aws.cluster_private_subnets(private_subnets)

list_lb_public = aws.list_load_balancers_external()
list_lb_private = aws.list_load_balancers_internal()

aws.public_load_balancer_info(list_lb_public)
aws.private_load_balancer_info(list_lb_private)
aws.get_public_route_tables(public_subnets)

sg_list = aws.cluster_instances()

aws.attached_sg(sg_list)

zone_ids = aws.route53_list()

aws.route53_info(zone_ids)
aws.last_used_keys()




