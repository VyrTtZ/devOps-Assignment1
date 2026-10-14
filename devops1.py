#TO DO : Website that displays Instance ID, public ip, ami id, az, and an image, ;


import json
import random
import time
from operator import itemgetter

import boto3

ec2 = boto3.resource("ec2")
s3 = boto3.resource("s3")
vpc = ec2.create_vpc(CidrBlock='172.16.0.0/16')


subnet = vpc.create_subnet(CidrBlock='172.16.0.0/24', AvailabilityZone='us-east-1b')
subnet.meta.client.modify_subnet_attribute(
    SubnetId=subnet.id, MapPublicIpOnLaunch={"Value": True}
)

print(vpc.id)
print(subnet.id)

# CREATES AND SETS THE INTERNET GATEWAY AND ROUTE TABLES -------------------------------------
internet_gateway = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)

route_table = vpc.create_route_table()
route_table.create_route(
    DestinationCidrBlock="0.0.0.0/0", GatewayId=internet_gateway.id
)
route_table.associate_with_subnet(SubnetId=subnet.id)
# FINDS THE NEWEST AMI-------------------------------------------------------------------------
client = boto3.client("ec2")
response = client.describe_images(
    Filters=[
        {
            "Name": "description",
            "Values": [
                "Amazon Linux AMI*",
            ],
        },
    ],
    Owners=["amazon"],
)
# Sort on Creation date Desc
image_details = sorted(
    response["Images"], key=itemgetter("CreationDate"), reverse=True
)
ami_id = image_details[0]["ImageId"]

# CREATE A NEW SECURITY GROUP-------------------------------------------------------------------------

securitygroup = ec2.create_security_group(
    GroupName="HTTP AND SSH",
    Description="lets ssh and http to the instance",
    VpcId=vpc.id,
)
securitygroup.authorize_ingress(
    CidrIp="0.0.0.0/0", IpProtocol="tcp", FromPort=22, ToPort=22
)
securitygroup.authorize_ingress(
    CidrIp="0.0.0.0/0", IpProtocol="tcp", FromPort=80, ToPort=80
)

# CREATES A NEW INSTANCE-------------------------------------------------------------------------

new_instances = ec2.create_instances(
    ImageId=ami_id,
    KeyName="devops1",
    MinCount=1,
    MaxCount=1,
    InstanceType="t2.nano",
    SubnetId=subnet.id,
    SecurityGroupIds=[securitygroup.id],
    UserData=f"""#!/bin/bash
yum install httpd -y
systemctl enable httpd
systemctl start httpd
touch /var/www/html/index.html
PT=/var/www/html/index.html
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")


curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id >> $PT
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 >> $PT
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/ami-id >> $PT 
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone >> $PT
echo '<img src="http://devops.setudemo.net/logo.jpg">' >> /var/www/html/index.html

""",
)
# S3 BUCKET SETUP -------------------------------------------------------------------------------
s3 = boto3.resource("s3")
date_str = time.strftime("%Y-%m-%d")
random_num = random.randint(1000, 9999)
randomString = ""

for i in range 6:
    randomString += random.choice(string.ascii_letters)

bucket_name = f"{randomString}-gtarka".lower()

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
    print(error)
print(new_instances[0].id)
print(ami_id)

