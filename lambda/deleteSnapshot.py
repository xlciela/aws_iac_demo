import boto3
import os
from logging import getLogger, INFO
from time import sleep
from botocore.exceptions import ClientError

logger = getLogger()
logger.setLevel(INFO)
client = boto3.client('ec2')

def lambda_handler(event, context):
    imageID = event['detail']['requestParameters']['imageId']

    response = client.describe_snapshots(
        OwnerIds=[os.environ['AWS_ACCOUNT']],
        Filters=[
            {
                'Name': 'description',
                'Values': ['*'+imageID+'*']
            }
        ]
    )
    for snapshot in response['Snapshots']:
        logger.info(imageID)
        logger.info("delete snapshot: " + snapshot['SnapshotId'])
        print("delete snapshot: " + snapshot['SnapshotId'])
        _delete_snapshot(snapshot['SnapshotId'])


def _delete_snapshot(snapshotid):
    try:
        return client.delete_snapshot(SnapshotId=snapshotid)
    except ClientError as e:
        logger.exception("Received error: %s", e)
    sleep(2)