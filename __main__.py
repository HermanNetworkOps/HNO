import pulumi
import pulumi_aws as aws
from pulumi_aws import ec2
subnets = 3
# Create an AWS resource 
vpc = ec2.Vpc("vpc", cidr_block="10.0.0.0/16")
priv_subnets = []
pub_subnets = []
for i in range(0, subnets):
    priv_subnet = ec2.Subnet(f"subnet-{i}-priv",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{i + 1}.0/24")
    pub_subnet = ec2.Subnet(f"subnet-{i}-pub",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{i + 11}.0/24")
    priv_subnets.append(priv_subnet)
    pub_subnets.append(pub_subnet)


igw = aws.ec2.InternetGateway(
	"HNO-igw",
	vpc_id =vpc.id
)
route_table = aws.ec2.RouteTable(
	"HNO-route-table-public",
	vpc_id=vpc.id,
	routes=[
		{
			"cidr_block": "0.0.0.0/0",
			"gateway_id": igw.id
		}
	]
)
rt_assoc = aws.ec2.RouteTableAssociation(
	"HNO-rta-public",
	route_table_id= "HNO-route-table-public",
	subnet_id = [subnet.id for subnet in pub_subnets] # do an operation on subnet, then the for loop for subnet in subnets
)

ngw = aws.ec2.NatGateway
"HNO-ngw"
vpc_id = vpc.id

route_table = aws.ec2.RouteTable(
	"HNO-route-table-private",
	vpc_id=vpc.id,
	routes=[
		{
			"cidr_block": "0.0.0.0/0",
			"gateway_id": ngw.id
		}
	]
)


sg = aws.ec2.SecurityGroup(
	"HNO-http-sg",
	description="Allow http traffic to ec2 instance",
	ingress=[{
		"protocol": "tcp",
		"from_port": 80,
		"to_port": 80,
		"cidr_blocks": ["0.0.0.0/0"],
	}],
    vpc_id= vpc.id,
)
ami = aws.ec2.get_ami(
	most_recent="true",
	owners=["amazon"],
	filters=[{"name": "name", "values": ["amzn-ami-hvm-*"]}]
)

user_data = """
#!/bin/bash
echo "Hello, world!" > index.html
nohup python -m SimpleHTTPServer 80 &
"""

ec2_instance = aws.ec2.Instance(
	"HNO-tutorial",
	instance_type="t2.micro",
	vpc_security_group_ids=[sg.id],
	ami = ami.id,
	user_data=user_data,
      subnet_id=pub_subnets.id,
      associate_public_ip_address=True,
)

# Export the name of the bucket
pulumi.export ("ec2-public-ip", ec2_instance.public_ip)




