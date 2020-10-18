import boto3
import pprint

source_db_id    = "arn:aws:rds:us-east-1:161933537528:db:dr-test-db"  # name of the DataBase if in same region, ARN if not
db_instance_id  = "dr-test-db-readreplica"  # name of the DataBase Instance
tags            = [{'Key': 'Name', 'Value': 'test-db'}]  # add more with comma seperation
iops            = 1000  # if the above is set to io1
source_region   = "us-east-1"
storage_type    = "io1"
kms_id          = "arn:aws:kms:us-west-2:161933537528:key/db3e1068-a7c0-4620-afa3-849ff1f14dc2" # created prior, if you
#want to change, create a new key
multi_az        = True
public_access   = False
db_subnet_group = "db replica sg"

choice = int(input("1. Create read replica\n2. Update SSM Parameter\n>"))
# Because you cant describe and get the endpoint of a DB right after creation state,
# run this script after the replica is ready and choose the second option

if choice == 1:
    rds = boto3.client('rds', region_name='us-west-2')
    response = rds.create_db_instance_read_replica(
        DBInstanceIdentifier=db_instance_id,
        SourceDBInstanceIdentifier=source_db_id,
        MultiAZ=multi_az,
        Iops=iops,
        PubliclyAccessible=public_access,
        Tags=tags,
        StorageType=storage_type,
        SourceRegion=source_region,
        KmsKeyId=kms_id,
        DBSubnetGroupName=db_subnet_group
    )
    print("Creating Database Instance")
    pprint.pprint(response)
elif choice == 2:
    rds = boto3.client('rds', region_name='us-west-2')
    info = rds.describe_db_instances(
        DBInstanceIdentifier=db_instance_id
    )
    ssm = boto3.client('ssm', region_name='us-west-2')
    param = ssm.put_parameter(
        Name="/ec/DB_HOST",
        Value=info["DBInstances"][0]["Endpoint"]["Address"],
        Type='String',
        Overwrite=True,
    )
    print("Updating the SSM Parameter")
    pprint.pprint(param)
else:
    print("Choose a valid option")


