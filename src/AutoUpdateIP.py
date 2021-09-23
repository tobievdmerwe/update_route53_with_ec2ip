# This Lambda updates Route 53 with the DNS name and IP of the EC2.
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Update Route 53
def update_route53(hosted_zone, public_ip, dns_name):

   try:
      client = boto3.client('route53')

      dns_changes = {
          'Changes': [
               {
                   'Action': 'UPSERT',
                   'ResourceRecordSet': {
                       'Name': dns_name,
                       'Type': 'A',
                       'ResourceRecords': [
                           {
                               'Value': public_ip
                           }
                       ],
                       'TTL': 300
                   }
              }
        ]
      }
   
      logger.info('Updating DNS rule')
      response = client.change_resource_record_sets(
         HostedZoneId=hosted_zone,
         ChangeBatch=dns_changes
      )

      logger.info('Response: {}'.format(response))

   except Exception as e:
       logger.error('Failure updating IP: {}'.format(e))
       raise
    
# Search for a value in the dictionary
def search(dicts, search_target):
    for item in dicts:
        if search_target == item['Key']:
            return item['Value']
    return None

# Lambda handler
def lambda_handler(event, context):
    ec2 = boto3.resource('ec2')
    hosted_zone = os.environ.get('Route53HostedZone')   
    logger.info('event info: {}'.format(event))

    try:
        if 'source' in event and event['source'] == 'aws.ec2' and event['detail']['state'] == 'running':
            instance_id = event['detail']['instance-id']
            instance = ec2.Instance(instance_id)
            instance_ip = instance.public_ip_address
            dns_name = search(instance.tags, 'AutoUpdateIP')
            logger.info('DNS name: {}'.format(dns_name))
            if dns_name is not None:
               update_route53(hosted_zone, instance_ip, dns_name)           
            else:
               logger.info('No update done - EC2 is not tagged')          

    except Exception as e:
        logger.error('Could not update Route53 details: {}'.format(e))
        raise