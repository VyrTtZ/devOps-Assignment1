#TO DO : enhance monitoring.sh, make sure its running, run the upgraeded monitoring.sh on an instace with scp to copy script and execute through ssh, create ami from the ec2 naming convetion in spec ;


import json
import random
import time
from operator import itemgetter
import string
import boto3
import subprocess
import requests


ec2 = boto3.resource("ec2")
s3 = boto3.resource("s3")
vpc = ec2.create_vpc(CidrBlock='172.16.0.0/16')
ssm = boto3.client('ssm')

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
response = ssm.get_parameter(
        Name='/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64'
)
ami_id = response['Parameter']['Value']

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
instance = new_instances[0]

instance.wait_until_running()
instance.reload()

publicIp = instance.public_ip_address

# MAKE THE INDEX FOR THE S3 ---------------------------------------------------------------------
subprocess.run(["touch", "index.html"])
txt = f"""<!DOCTYPE html>
<html>
<img src="img.jpg">
</html>
"""

with open("index.html", "w") as f:
    f.write(txt)


# S3 BUCKET SETUP -------------------------------------------------------------------------------



s3 = boto3.resource("s3")
date_str = time.strftime("%Y-%m-%d")
random_num = random.randint(1000, 9999)
randomString = ""
subprocess.run(["touch", "img.jpg"])
for i in range(6):
    randomString += random.choice(string.ascii_letters)

bucket_name = f"{randomString}-gtarka".lower()

website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
}

try:
    print(bucket_name)
    response = s3.create_bucket(Bucket=bucket_name)
    print(response)
    bucket_website = s3.BucketWebsite(bucket_name)
    response = bucket_website.put(WebsiteConfiguration=website_configuration)
    print("Upload and index.html file to see if it works!")
    subprocess.run(["curl", "http://devops.setudemo.net/logo.jpg",  "--output", "img.jpg"])
    s3.Object(bucket_name, "img.jpg").put(Body=open("img.jpg", "rb"), ContentType="image/jpeg")
    s3.Object(bucket_name, "index.html").put(Body=open("index.html", "rb"), ContentType="text/html")
    s3.meta.client.delete_public_access_block(Bucket=bucket_name)
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }],
    }
    s3.Bucket(bucket_name).Policy().put(Policy=json.dumps(bucket_policy))
except Exception as error:
    print(error)

subprocess.run(["touch", "gtarka-websites.txt"])
s3Url = f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
ec2Url = f"http://{publicIp}"
with open("gtarka-websites.txt", "w") as f:
    f.write(s3Url + "\n")
    f.write(ec2Url + "\n")

# MONITORING --------------------------------------------------------------------------------------
#!/usr/bin/bash
#
# Some basic monitoring functionality; Tested on Amazon Linux 2023.
#
TOKEN=`curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)

echo "Instance ID: $INSTANCE_ID"
echo "Memory utilisation: $MEMORYUSAGE"
echo "No of processes: $PROCESSES"
if [ $HTTPD_PROCESSES -ge 1 ]
then
    echo "Web server is running"
else
    echo "Web server is NOT running"
fi

print(new_instances[0].id)
print(ami_id)


