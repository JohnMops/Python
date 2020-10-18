# multi az DB instance creation

import boto3

rds = boto3.client('rds', region_name='us-east-1')

db_name = "john_test"  # name of the DataBase
db_instance_id = "dr-test-db"  # name of the DataBase Instance
allocation_storage = 1000  # storage size
db_instance_class = "db.t3.small"  # size of the instance
engine = "postgres"

username = "johnadmin"
password = "johnadmin"

vpc_security_groups = ["sg-24c34050"]
option_group = "default:postgres-11"
db_subnet_group_name = "rds_prod_subg"  # rds subnet groups
engine_version = "11.8"
tags = [{'Key': 'Name', 'Value': 'test-db'}]  # add more with comma seperation
iops = 1000  # if the above is set to io1, do not set if StorageType is not "io1"
storage_type = "io1"
license_model =  "license-included" # Valid values: license-included | bring-your-own-license | general-public-license

preferred_backup_window = "08:00-08:30"
backup_retention = 7
kms_key_id = "aws/rds" # key id for encrypting the DB
storage_encrypted = True
performance_insights_retention_period = 7
enable_cloudwatch_logs_exports = ["postgresql","upgrade"] # see documentation for engine specific

delete_protection=False # only for testing
public_access = False
multi_az = True
preferred_maintenance_indow = "tue:11:08-tue:11:38" # this is the format
enable_performance_insights = True


rds.create_db_instance(
    DBName=db_name,
    DBInstanceIdentifier=db_instance_id,
    AllocatedStorage=allocation_storage,
    DBInstanceClass=db_instance_class,
    Engine=engine,
    MasterUsername=username,
    MasterUserPassword=password,
    VpcSecurityGroupIds=vpc_security_groups,
    DBSubnetGroupName=db_subnet_group_name,
    MultiAZ=multi_az,
    EngineVersion=engine_version,
    PubliclyAccessible=public_access,
    Tags=tags,
    Iops=iops,
    StorageType=storage_type,
    DeletionProtection=delete_protection,
    BackupRetentionPeriod=backup_retention,
    PreferredBackupWindow=preferred_backup_window,
    PreferredMaintenanceWindow=preferred_maintenance_indow,
    LicenseModel=license_model,
    OptionGroupName=option_group,
    StorageEncrypted=storage_encrypted,
    KmsKeyId=kms_key_id,
    EnablePerformanceInsights=enable_performance_insights,
    PerformanceInsightsKMSKeyId=kms_key_id,
    PerformanceInsightsRetentionPeriod=performance_insights_retention_period,
    EnableCloudwatchLogsExports=enable_cloudwatch_logs_exports,
)
