#ON STEP 2
#TO DO : Create Security group, Set up az, and an ssh key, Website that displays Instance ID, public ip, ami id, az, and an image; download image from http://devops.setudemo.net/logo.jpg. , 

import boto3
import time
import json
import random
from operator import itemgetter


ec2 = boto3.resource("ec2")
s3 = boto3.resource("s3")
vpc = ec2.create_vpc(CidrBlock='172.16.0.0/16')
subnet = vpc.create_subnet(CidrBlock='172.16.0.0./24')

print(vpc.id)
print(subnet.id)

#FINDS THE NEWEST AMI-------------------------------------------------------------------------
client = boto3.client('ec2')
response = client.describe_images(
    Filters=[
        {
            'Name': 'description',
            'Values': [
                'Amazon Linux AMI*',
            ]
        },
    ],
    Owners=[
        'amazon'
    ]
)
# Sort on Creation date Desc
image_details = sorted(response['Images'],key=itemgetter('CreationDate'),reverse=True)
ami_id = image_details[0]['ImageId']

#CREATE A NEW SECURITY GROUP-------------------------------------------------------------------------

securitygroup = ec2.create_security_group(GroupName='HTTP AND SSH', Description='lets ssh and http to the instance', VpcId=vpc.id)
securitygroup.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
securitygroup.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=-1, ToPort=80)

#CREATES A NEW INSTANCE-------------------------------------------------------------------------

new_instances = ec2.create_instances(
    ImageId=ami_id,
    KeyName="devops1",
    MinCount=1,
    MaxCount=1,
    InstanceType="t2.nano",
    SubnetId="subnet.id",
    SecurityGroupIds=[securitygroup.id],
    UserData="""#!/bin/bash
yum install httpd -y
systemctl enable httpd
systemctl start httpd
"""
)

print (new_instances[0].id)

#REST OF THE BULLSHIT-------------------------------------------------------------------------

#!/usr/bin/env python3
import random
import time
import json
import boto3

s3 = boto3.resource("s3")
date_str = time.strftime("%Y-%m-%d")
random_num = random.randint(1000, 9999)
bucket_name = f"gtarka-{random_num}-{date_str}".lower()

website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
}

try:
    response = s3.create_bucket(Bucket=bucket_name)
    print(response)
    bucket_website = s3.BucketWebsite(bucket_name)
    response = bucket_website.put(WebsiteConfiguration=website_configuration)
    print("Upload and index.html file to see if it works!")

except Exception as error:
    print(error)#!/usr/bin/env python3


#create a security group

[200~response = client.create_security_group(
        Description='string',
            GroupName='string',
                VpcId='string',
                    TagSpecifications=[
                                {
                                                'ResourceType': 'capacity-reservation'|'client-vpn-endpoint'|'customer-gateway'|'carrier-gateway'|'coip-pool'|'declarative-policies-report'|'dedicated-host'|'dhcp-options'|'egress-only-internet-gateway'|'elastic-ip'|'elastic-gpu'|'export-image-task'|'export-instance-task'|'fleet'|'fpga-image'|'host-reservation'|'image'|'image-usage-report'|'import-image-task'|'import-snapshot-task'|'instance'|'instance-event-window'|'internet-gateway'|'ipam'|'ipam-pool'|'ipam-scope'|'ipv4pool-ec2'|'ipv6pool-ec2'|'key-pair'|'launch-template'|'local-gateway'|'local-gateway-route-table'|'local-gateway-virtual-interface'|'local-gateway-virtual-interface-group'|'local-gateway-route-table-vpc-association'|'local-gateway-route-table-virtual-interface-group-association'|'natgateway'|'network-acl'|'network-interface'|'network-insights-analysis'|'network-insights-path'|'network-insights-access-scope'|'network-insights-access-scope-analysis'|'outpost-lag'|'placement-group'|'prefix-list'|'replace-root-volume-task'|'reserved-instances'|'route-table'|'security-group'|'security-group-rule'|'service-link-virtual-interface'|'snapshot'|'spot-fleet-request'|'spot-instances-request'|'subnet'|'subnet-cidr-reservation'|'traffic-mirror-filter'|'traffic-mirror-session'|'traffic-mirror-target'|'transit-gateway'|'transit-gateway-attachment'|'transit-gateway-connect-peer'|'transit-gateway-multicast-domain'|'transit-gateway-policy-table'|'transit-gateway-metering-policy'|'transit-gateway-route-table'|'transit-gateway-route-table-announcement'|'volume'|'vpc'|'vpc-endpoint'|'vpc-endpoint-connection'|'vpc-endpoint-service'|'vpc-endpoint-service-permission'|'vpc-peering-connection'|'vpn-connection'|'vpn-gateway'|'vpc-flow-log'|'capacity-reservation-fleet'|'traffic-mirror-filter-rule'|'vpc-endpoint-connection-device-type'|'verified-access-instance'|'verified-access-group'|'verified-access-endpoint'|'verified-access-policy'|'verified-access-trust-provider'|'vpn-connection-device-type'|'vpc-block-public-access-exclusion'|'vpc-encryption-control'|'route-server'|'route-server-endpoint'|'route-server-peer'|'ipam-resource-discovery'|'ipam-resource-discovery-association'|'instance-connect-endpoint'|'verified-access-endpoint-target'|'ipam-external-resource-verification-token'|'capacity-block'|'mac-modification-task'|'ipam-prefix-list-resolver'|'ipam-policy'|'ipam-prefix-list-resolver-target'|'ipam-internet-registry-association'|'secondary-interface'|'secondary-network'|'secondary-subnet'|'capacity-manager-data-export'|'vpn-concentrator'|'ipam-pool-allocation'|'capacity-reservation-cancellation-quote'|'application-status-check'|'capacity-reservation-modification-quote',
                                                            'Tags': [
                                                                                {
                                                                                                        'Key': 'string',
                                                                                                                            'Value': 'string'
                                                                                                                                            },
                                                                                            ]
                                                                    },
                                    ],
                        DryRun=True|False
                        )
