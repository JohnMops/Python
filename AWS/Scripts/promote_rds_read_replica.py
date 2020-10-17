import boto3



db_us_east_1 = "dr-test-db"
db_us_west_2 = "dr-test-db-readreplica"

choice = int(input('Choose the DB to promote to Master:\n 1. N.California - {}\n 2. Oregon - {}\n\n > '.format(db_us_east_1, db_us_west_2)))

def promotion(choice):
    if choice == 1:
        client = boto3.client('rds', region_name='us-east-1')
        client.promote_read_replica (
            DBInstanceIdentifier = db_us_east_1
        )
    if choice == 2:
        client = boto3.client('rds', region_name='us-west-2')
        client.promote_read_replica (
            DBInstanceIdentifier = db_us_west_2
        )
    else:
        print ('Please choose a valid input')


promotion(choice)



