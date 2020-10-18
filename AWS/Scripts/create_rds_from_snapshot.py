import boto3
import pprint

rds = boto3.client('rds', region_name='us-east-1')

db_instance_id       = "dr-test-db" # name of the DataBase Instance
snapshot_name        = "awsbackup:job-037811c5-606e-aa46-22d5-010815d758cb" # fill with latest snapshot
db_instance_class    = "db.t3.small" # size of the instance
db_subnet_group_name = "rds_prod_subg" # rds subnet groups
iops                 = 1000  # if the above is set to io1
option_group         = "default:postgres-11" # rds option group
db_parameter_group   = "default.postgres11" # rds parameter group
delete_protection    = False # only for testing
tags                 = [{'Key': 'Name', 'Value': 'test-db'}]  # add more with comma seperation

response = rds.restore_db_instance_from_db_snapshot (
    DBInstanceIdentifier=db_instance_id,
    DBSnapshotIdentifier=snapshot_name,
    DBInstanceClass=db_instance_class,
    DBSubnetGroupName=db_subnet_group_name,
    MultiAZ=True,
    PubliclyAccessible=False,
    AutoMinorVersionUpgrade=True,
    Iops=iops,
    OptionGroupName=option_group,
    Tags=tags,
    StorageType='io1',
    EnableCloudwatchLogsExports=[
        'postgresql',
        'upgrade'
    ],
    DBParameterGroupName=db_parameter_group,
    DeletionProtection=delete_protection
)

print("Creating DB instance")
pprint.pprint(response)
