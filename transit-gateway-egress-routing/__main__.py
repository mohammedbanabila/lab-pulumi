"""An AWS Python Pulumi program"""
import pulumi_aws as aws
import pulumi , json 

networks1={
    "hubblock": "81.48.0.0/16",
    "spoke1block1" : "80.16.0.0/16",
    "spoke2block2" : "80.32.0.0/16",
    "traffic_ipv4_any" : "0.0.0.0/0",
    "myips" : "41.79.196.60/32",
    "rangeblock" : "80.0.0.0/8",
    "hub1a": "81.48.16.0/20",
    "hub1b": "81.48.32.0/20",
    "hub1c": "81.48.48.0/20",
    "hub1d": "81.48.64.0/20",
    "spoke1c": "80.16.48.0/20",
    "spoke1d": "80.16.64.0/20",
    "spoke2c": "80.32.48.0/20",
    "spoke2d": "80.32.64.0/20",
    "zone1a" : "us-east-1a",
    "zone1b" : "us-east-1b"
}

insttools={
    "instami" : "ami-0fc5d935ebf8bc3bc",
    "instancetypes" : "t2.micro",
    "keys1" : "keys1lab1",
    "keys2" : "keys2lab2",
}

userdata1="""#!/bin/bash
sudo apt update -y
sudo apt upgrade -y
"""

# create  transit gateway 
tgw1conn1=aws.ec2transitgateway.TransitGateway(
  "tgw1conn1",
   aws.ec2transitgateway.TransitGatewayArgs(
   default_route_table_association="disable",
   default_route_table_propagation="disable",
   multicast_support="disable",
   dns_support="enable",
   vpn_ecmp_support="disable",
   amazon_side_asn=64514,
   auto_accept_shared_attachments="disable",
   tags={
    "Name" :"tgw1conn1"
   }
   )
)
#  create  vpc1 hub 
vpc1=aws.ec2.Vpc(
    "vpc1",
    aws.ec2.VpcArgs(
     cidr_block=networks1["hubblock"],
     tags={
         "Name" :  "vpc1"
     },
)
)

intgw1=aws.ec2.InternetGateway(
    "intgw1",
    aws.ec2.InternetGatewayArgs(
    vpc_id=vpc1.id,
    tags={
        "Name" : "intgw1"
    }
    )
)

public1subnet1=aws.ec2.Subnet(
    "public1subnet1",
    vpc_id=vpc1.id,
    cidr_block=networks1["hub1a"],
    availability_zone=networks1["zone1a"],
    map_public_ip_on_launch=True,
    tags={
        "Name" :  "public1subnet1"
    }
)

public1subnet2=aws.ec2.Subnet(
    "public1subnet2",
    aws.ec2.SubnetArgs(
    vpc_id=vpc1.id,
    cidr_block=networks1["hub1b"],
    availability_zone=networks1["zone1b"],
    map_public_ip_on_launch=True,
    tags={
        "Name" :  "public1subnet2"
    }
    )
)

tgw1subnet1=aws.ec2.Subnet(
    "tgw1subnet1",
        aws.ec2.SubnetArgs(

    vpc_id=vpc1.id,
    cidr_block=networks1["hub1c"],
    availability_zone=networks1["zone1a"],
    tags={
        "Name" : "tgw1subnet1",
  }
        )
)

tgw2subnet1=aws.ec2.Subnet(
    "tgw2subnet1",
        aws.ec2.SubnetArgs(

    vpc_id=vpc1.id,
    cidr_block=networks1["hub1d"],
    availability_zone=networks1["zone1b"],
    tags={
        "Name" : "tgw2subnet1",
  }
        )
)

table1=aws.ec2.RouteTable(
   "table1",
   aws.ec2.RouteTableArgs(
   vpc_id=vpc1.id,
   routes=[
       aws.ec2.RouteTableRouteArgs(
           cidr_block=networks1["traffic_ipv4_any"],
           gateway_id=intgw1.id
        ),
        aws.ec2.RouteTableRouteArgs(
           cidr_block=networks1["rangeblock"],
           transit_gateway_id=tgw1conn1.id
        ),
   ],
   tags={
       "Name" : "table1"
   },
   )
  
)

hublink1a=aws.ec2.RouteTableAssociation(
    "hublink1a",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=public1subnet1.id,
    route_table_id=table1.id
    )
)
hublink1b=aws.ec2.RouteTableAssociation(
    "hublink1b",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=public1subnet2.id,
    route_table_id=table1.id
    )
)

eip1a=aws.ec2.Eip(
    "eip1a",
    aws.ec2.EipArgs(
    domain="vpc",
    tags={
        'Name' :  "eip1a"
    }
    )
)

eip1b=aws.ec2.Eip(
    "eip1b",
        aws.ec2.EipArgs(

    domain="vpc",
    tags={
        'Name' :  "eip1b"
    }
        )
)

nat1a=aws.ec2.NatGateway(
  "nat1a",
  aws.ec2.NatGatewayArgs(
  allocation_id=eip1a.allocation_id,
  subnet_id=public1subnet1.id,
  connectivity_type="public",
  tags={
      "Name"  : "nat1a"
  }
  )
)

nat1b=aws.ec2.NatGateway(
  "nat1b",
  aws.ec2.NatGatewayArgs(

  allocation_id=eip1b.allocation_id,
  subnet_id=public1subnet2.id,
  connectivity_type="public",
  tags={
      "Name"  : "nat1b"
  }
  )
)

nacls1=aws.ec2.NetworkAcl(
    "nacls1",
    aws.ec2.NetworkAclArgs(
    vpc_id=vpc1.id,
    ingress=[
        aws.ec2.NetworkAclIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_block=networks1["myips"],
            icmp_code=1,
            icmp_type=1,
            rule_no=100,
            action="allow"
        ),
         aws.ec2.NetworkAclIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_block=networks1["rangeblock"],
            icmp_code=1,
            icmp_type=1,
            rule_no=101,
            action="allow"
        ),
         aws.ec2.NetworkAclIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=102,
            action="deny"
        ),
         aws.ec2.NetworkAclIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=200,
            action="allow"
        ),
          aws.ec2.NetworkAclIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=300,
            action="allow"
        ),
          aws.ec2.NetworkAclIngressArgs(
            from_port=32000,
            to_port=65535,
            protocol="tcp",
            cidr_block=networks1["rangeblock"],
            icmp_code=1,
            icmp_type=1,
            rule_no=400,
            action="allow"
        ),
          aws.ec2.NetworkAclIngressArgs(
            from_port=0,
            to_port=0,
            protocol="icmp",
            cidr_block=networks1["rangeblock"],
            icmp_code=1,
            icmp_type=1,
            rule_no=500,
            action="allow"
        ),
          aws.ec2.NetworkAclIngressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=600,
            action="allow"
        ),

    ],
    egress=[
            aws.ec2.NetworkAclIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_block=networks1["myips"],
            icmp_code=1,
            icmp_type=1,
            rule_no=100,
            action="allow"
        ),
         aws.ec2.NetworkAclIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_block=networks1["rangeblock"],
            icmp_code=1,
            icmp_type=1,
            rule_no=101,
            action="allow"
        ),
         aws.ec2.NetworkAclIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=102,
            action="deny"
        ),
         aws.ec2.NetworkAclIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=200,
            action="allow"
        ),
          aws.ec2.NetworkAclIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=300,
            action="allow"
        ),
          aws.ec2.NetworkAclIngressArgs(
            from_port=32000,
            to_port=65535,
            protocol="tcp",
            cidr_block=networks1["rangeblock"],
            icmp_code=1,
            icmp_type=1,
            rule_no=400,
            action="allow"
        ),
          aws.ec2.NetworkAclIngressArgs(
            from_port=0,
            to_port=0,
            protocol="icmp",
            cidr_block=networks1["rangeblock"],
            icmp_code=1,
            icmp_type=1,
            rule_no=500,
            action="allow"
        ),
          aws.ec2.NetworkAclEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_block=networks1["traffic_ipv4_any"],
            icmp_code=1,
            icmp_type=1,
            rule_no=600,
            action="allow"
        ),
    ],
    tags={
        "Name" :  "nacls1"
    }
    )
)
hub1nacls1link1=aws.ec2.NetworkAclAssociation(
    "hub1nacls1link1",
    aws.ec2.NetworkAclAssociationArgs(
    subnet_id=public1subnet1.id,
    network_acl_id=nacls1.id
    )
)
hub1nacls1link2=aws.ec2.NetworkAclAssociation(
    "hub1nacls1link2",
    aws.ec2.NetworkAclAssociationArgs(
    subnet_id=public1subnet2.id,
    network_acl_id=nacls1.id
    )
)

nacls2=aws.ec2.NetworkAcl(
    "nacls2",
    aws.ec2.NetworkAclArgs(

    vpc_id=vpc1.id,
    ingress=[
      aws.ec2.NetworkAclIngressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_block=networks1["myips"],
          icmp_code=1,
          icmp_type=1,
          rule_no=100,
          action="allow"
      ),
       aws.ec2.NetworkAclIngressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_block=networks1["rangeblock"],
          icmp_code=1,
          icmp_type=1,
          rule_no=101,
          action="allow"
      ),
        aws.ec2.NetworkAclIngressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=102,
          action="allow"
      ),
       aws.ec2.NetworkAclIngressArgs(
          from_port=80,
          to_port=80,
          protocol="tcp",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=200,
          action="allow"
      ),
       aws.ec2.NetworkAclIngressArgs(
          from_port=443,
          to_port=443,
          protocol="tcp",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=300,
          action="allow"
      ),
       aws.ec2.NetworkAclIngressArgs(
          from_port=0,
          to_port=0,
          protocol="icmp",
          cidr_block=networks1["rangeblock"],
          icmp_code=1,
          icmp_type=1,
          rule_no=400,
          action="allow"
      ),
       aws.ec2.NetworkAclIngressArgs(
          from_port=32000,
          to_port=65535,
          protocol="tcp",
          cidr_block=networks1["rangeblock"],
          icmp_code=1,
          icmp_type=1,
          rule_no=500,
          action="allow"
      ),
       aws.ec2.NetworkAclIngressArgs(
          from_port=0,
          to_port=0,
          protocol="-1",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=600,
          action="allow"
      ),
    ],
    egress=[
        aws.ec2.NetworkAclEgressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_block=networks1["myips"],
          icmp_code=1,
          icmp_type=1,
          rule_no=100,
          action="allow"
      ),
       aws.ec2.NetworkAclEgressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_block=networks1["rangeblock"],
          icmp_code=1,
          icmp_type=1,
          rule_no=101,
          action="allow"
      ),
        aws.ec2.NetworkAclEgressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=102,
          action="allow"
      ),
       aws.ec2.NetworkAclEgressArgs(
          from_port=80,
          to_port=80,
          protocol="tcp",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=200,
          action="allow"
      ),
       aws.ec2.NetworkAclEgressArgs(
          from_port=443,
          to_port=443,
          protocol="tcp",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=300,
          action="allow"
      ),
       aws.ec2.NetworkAclEgressArgs(
          from_port=0,
          to_port=0,
          protocol="icmp",
          cidr_block=networks1["rangeblock"],
          icmp_code=1,
          icmp_type=1,
          rule_no=400,
          action="allow"
      ),
       aws.ec2.NetworkAclEgressArgs(
          from_port=32000,
          to_port=65535,
          protocol="tcp",
          cidr_block=networks1["rangeblock"],
          icmp_code=1,
          icmp_type=1,
          rule_no=500,
          action="allow"
      ),
       aws.ec2.NetworkAclEgressArgs(
          from_port=0,
          to_port=0,
          protocol="-1",
          cidr_block=networks1["traffic_ipv4_any"],
          icmp_code=1,
          icmp_type=1,
          rule_no=600,
          action="allow"
      ),   
    ],
    tags={
        "Name" :  "nacls2"
    }
    )
)
nacls2link1=aws.ec2.NetworkAclAssociation(
    "nacls2link1",
        aws.ec2.NetworkAclAssociationArgs(

    subnet_id=tgw1subnet1.id,
    network_acl_id=nacls2.id
        )
)
nacls2link2=aws.ec2.NetworkAclAssociation(
    "nacls2link2",
        aws.ec2.NetworkAclAssociationArgs(

    subnet_id=tgw2subnet1.id,
    network_acl_id=nacls2.id
        )
)

security1grp1=aws.ec2.SecurityGroup(
     "security1grp1",
     aws.ec2.SecurityGroupArgs(
     vpc_id=vpc1.id,
     name="hub1secure1",
     ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=[networks1["myips"] , networks1["rangeblock"]]
         ),
         aws.ec2.SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=[networks1["traffic_ipv4_any"]]
         ),
         aws.ec2.SecurityGroupIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=[networks1["traffic_ipv4_any"]]
         ),
          aws.ec2.SecurityGroupIngressArgs(
            from_port=0,
            to_port=0,
            protocol="icmp",
            cidr_blocks=[networks1["rangeblock"]]
         ),
     ],
     egress=[
         aws.ec2.SecurityGroupEgressArgs(
             from_port=0,
             to_port=0,
             protocol="-1",
             cidr_blocks=[networks1["traffic_ipv4_any"]]
         )
     ],
     tags={
         "Name" : "security1grp1"
     }
     )
)


table2a=aws.ec2.RouteTable(
  "table2a",
  aws.ec2.RouteTableArgs(
  vpc_id=vpc1.id,
  routes=[
    aws.ec2.RouteTableRouteArgs(
        cidr_block=networks1["traffic_ipv4_any"],
        nat_gateway_id=nat1a.id
    ),
  ],
  tags={
      "Name": "table2a"
  }
  )
)

link2a=aws.ec2.RouteTableAssociation(
    "link2a",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=tgw1subnet1.id,
    route_table_id=table2a.id
    )
)

table2b=aws.ec2.RouteTable(
  "table2b",
  aws.ec2.RouteTableArgs(
  vpc_id=vpc1.id,
  routes=[
       aws.ec2.RouteTableRouteArgs(
        cidr_block=networks1["traffic_ipv4_any"],
       nat_gateway_id=nat1b.id
    ),
  ],
  tags={
      "Name": "table2b"
  }
  )
)
 
link2b=aws.ec2.RouteTableAssociation(
    "link2b",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=tgw2subnet1.id,
    route_table_id=table2b.id
    )
)

instance1=aws.ec2.Instance(
  "instance1",
  aws.ec2.InstanceArgs(
  ami=insttools["instami"],
  instance_type=insttools["instancetypes"],
  key_name=insttools["keys1"],
  vpc_security_group_ids=[security1grp1.id],
  ebs_block_devices=[
      aws.ec2.InstanceEbsBlockDeviceArgs(
          device_name="/dev/sdj",
          volume_size=8,
          volume_type="gp2",
          encrypted="false",
          delete_on_termination=True
      )
  ],
  user_data=userdata1,
  tags={
    "Name" :"instance1"
  },
  subnet_id=public1subnet1.id,
  availability_zone=networks1["zone1a"]
  )
)

instance2=aws.ec2.Instance(
  "instance2",
  aws.ec2.InstanceArgs(
  ami=insttools["instami"],
  instance_type=insttools["instancetypes"],
  key_name=insttools["keys1"],
  vpc_security_group_ids=[security1grp1.id],
  ebs_block_devices=[
      aws.ec2.InstanceEbsBlockDeviceArgs(
          device_name="/dev/sdh",
          volume_size=8,
          volume_type="gp2",
          encrypted="false",
          delete_on_termination=True
      )
  ],
  user_data=userdata1,
  tags={
    "Name" :"instance2"
  },
  subnet_id=public1subnet2.id,
  availability_zone=networks1["zone1b"]
  )
)

# for spoke2 vpc2

vpc2=aws.ec2.Vpc(
    "vpc2",
    aws.ec2.VpcArgs(
     cidr_block=networks1["spoke1block1"],
     tags={
         "Name" : "vpc2"
     },
    )
)

inst1subnet2=aws.ec2.Subnet(
    "inst1subnet2",
    aws.ec2.SubnetArgs(
    vpc_id=vpc2.id,
    cidr_block=networks1["spoke1c"],
    availability_zone=networks1["zone1a"],
    tags={
        "Name" : "inst1subnet2",
  }
    )
)

inst2subnet2=aws.ec2.Subnet(
    "inst2subnet2",
    aws.ec2.SubnetArgs(
    vpc_id=vpc2.id,
    cidr_block=networks1["spoke1d"],
    availability_zone=networks1["zone1b"],
    tags={
        "Name" : "inst2subnet2",
  }
    )
)
nacls2spoke1=aws.ec2.NetworkAcl(
    "nacls2spoke1",
    aws.ec2.NetworkAclArgs(
    vpc_id=vpc2.id,
      ingress=[
          aws.ec2.NetworkAclIngressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["myips"],
              icmp_code=1,
              icmp_type=1,
              rule_no=100,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=101,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=102,
              action="deny"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=80,
              to_port=80,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=200,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=443,
              to_port=443,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=300,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=0,
              to_port=0,
              protocol="icmp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=400,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=32000,
              to_port=65535,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=500,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=0,
              to_port=0,
              protocol="-1",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=600,
              action="allow"
          ),
      ],
      egress=[
          aws.ec2.NetworkAclEgressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["myips"],
              icmp_code=1,
              icmp_type=1,
              rule_no=100,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=101,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=102,
              action="deny"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=80,
              to_port=80,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=200,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=443,
              to_port=443,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=300,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=0,
              to_port=0,
              protocol="icmp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=400,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=32000,
              to_port=65535,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=500,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=0,
              to_port=0,
              protocol="-1",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=600,
              action="allow"
          ),
      ],
    tags={
        "Name" :  "nacls2spoke1"
    }
    )
)
inst1spoke1link1=aws.ec2.NetworkAclAssociation(
    "inst1spoke1link1",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=inst1subnet2.id,
    network_acl_id=nacls2spoke1.id
    )
)
inst2spoke1link2=aws.ec2.NetworkAclAssociation(
    "inst2spoke1link2",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=inst2subnet2.id,
    network_acl_id=nacls2spoke1.id
    )
)

security1grp2=aws.ec2.SecurityGroup(
     "security1grp2",
     aws.ec2.SecurityGroupArgs(
     vpc_id=vpc2.id,
     name="spoke1secure2",
     ingress=[
        aws.ec2.SecurityGroupIngressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_blocks=[networks1["myips"] , networks1["hubblock"]]
        ),
         aws.ec2.SecurityGroupIngressArgs(
          from_port=80,
          to_port=80,
          protocol="tcp",
          cidr_blocks=[networks1["traffic_ipv4_any"]]
        ),
          aws.ec2.SecurityGroupIngressArgs(
          from_port=443,
          to_port=443,
          protocol="tcp",
          cidr_blocks=[networks1["traffic_ipv4_any"]]
        ),
          aws.ec2.SecurityGroupIngressArgs(
          from_port=0,
          to_port=0,
          protocol="icmp",
          cidr_blocks=[networks1["hubblock"]]
        ),
     ],
     egress=[
         aws.ec2.SecurityGroupEgressArgs(
             from_port=0,
             to_port=0,
             protocol="-1",
             cidr_blocks=[networks1["traffic_ipv4_any"]]
         )
     ],
     tags={
         "Name" : "security1grp2"
     }
     )
)

spoke2instance1=aws.ec2.Instance(
  "spoke2instance1",
  aws.ec2.InstanceArgs(
  ami=insttools["instami"],
  instance_type=insttools["instancetypes"],
  key_name=insttools["keys2"],
  vpc_security_group_ids=[security1grp2.id],
  ebs_block_devices=[
      aws.ec2.InstanceEbsBlockDeviceArgs(
          device_name="/dev/sdi",
          volume_size=8,
          volume_type="gp2",
          encrypted="false",
          delete_on_termination=True
      )
  ],
  user_data=userdata1,
  tags={
    "Name" :"spoke2instance1"
  },
  subnet_id=inst1subnet2.id,
  availability_zone=networks1["zone1a"]
  )
)

spoke2instance2=aws.ec2.Instance(
  "spoke2instance2",
  aws.ec2.InstanceArgs(
  ami=insttools["instami"],
  instance_type=insttools["instancetypes"],
  key_name=insttools["keys2"],
  vpc_security_group_ids=[security1grp2.id],
  ebs_block_devices=[
      aws.ec2.InstanceEbsBlockDeviceArgs(
          device_name="/dev/sdy",
          volume_size=8,
          volume_type="gp2",
          encrypted="false",
          delete_on_termination=True
      )
  ],
  user_data=userdata1,
  tags={
    "Name" :"spoke2instance2"
  },
  subnet_id=inst2subnet2.id,
  availability_zone=networks1["zone1b"]
  )
)

# for spoke3 vpc3

vpc3=aws.ec2.Vpc(
    "vpc3",
    aws.ec2.VpcArgs(
     cidr_block=networks1["spoke2block2"],
     tags={
         "Name" :  "vpc3"
     },
    )
)

inst1subnet3=aws.ec2.Subnet(
    "inst1subnet3",
    aws.ec2.SubnetArgs(
    vpc_id=vpc3.id,
    cidr_block=networks1["spoke2c"],
    availability_zone=networks1["zone1a"],
    tags={
        "Name" : "inst1subnet3",
  }
    )
)

inst2subnet3=aws.ec2.Subnet(
    "inst2subnet3",
    aws.ec2.SubnetArgs(
    vpc_id=vpc3.id,
    cidr_block=networks1["spoke2d"],
    availability_zone=networks1["zone1b"],
    tags={
        "Name" : "inst2subnet3",
  }
    )
)

nacls4spoke3=aws.ec2.NetworkAcl(
    "nacls4spoke3",
    aws.ec2.NetworkAclArgs(
    vpc_id=vpc3.id,
        ingress=[
          aws.ec2.NetworkAclIngressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["myips"],
              icmp_code=1,
              icmp_type=1,
              rule_no=100,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=101,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=102,
              action="deny"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=80,
              to_port=80,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=200,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=443,
              to_port=443,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=300,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=0,
              to_port=0,
              protocol="icmp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=400,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=32000,
              to_port=65535,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=500,
              action="allow"
          ),
          aws.ec2.NetworkAclIngressArgs(
              from_port=0,
              to_port=0,
              protocol="-1",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=600,
              action="allow"
          ),
      ],
      egress=[
          
            aws.ec2.NetworkAclEgressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["myips"],
              icmp_code=1,
              icmp_type=1,
              rule_no=100,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=101,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=22,
              to_port=22,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=102,
              action="deny"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=80,
              to_port=80,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=200,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=443,
              to_port=443,
              protocol="tcp",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=300,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=0,
              to_port=0,
              protocol="icmp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=400,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=32000,
              to_port=65535,
              protocol="tcp",
              cidr_block=networks1["hubblock"],
              icmp_code=1,
              icmp_type=1,
              rule_no=500,
              action="allow"
          ),
          aws.ec2.NetworkAclEgressArgs(
              from_port=0,
              to_port=0,
              protocol="-1",
              cidr_block=networks1["traffic_ipv4_any"],
              icmp_code=1,
              icmp_type=1,
              rule_no=600,
              action="allow"
          ),

      ],
    tags={
        "Name" :  "nacls4spoke3"
    }
    )
)
nacls4link1=aws.ec2.NetworkAclAssociation(
    "nacls4link1",
    aws.ec2.NetworkAclAssociationArgs(
    subnet_id=inst1subnet3.id,
    network_acl_id=nacls4spoke3.id
    )
)
nacls4link2=aws.ec2.NetworkAclAssociation(
    "nacls4link2",
    aws.ec2.NetworkAclAssociationArgs(
    subnet_id=inst2subnet3.id,
    network_acl_id=nacls4spoke3.id
    )
)

security1grp3=aws.ec2.SecurityGroup(
     "security1grp3",
     aws.ec2.SecurityGroupArgs(
     vpc_id=vpc3.id,
     name="spoke3secure3",
       ingress=[
         aws.ec2.SecurityGroupIngressArgs(
          from_port=22,
          to_port=22,
          protocol="tcp",
          cidr_blocks=[networks1["myips"], networks1["hubblock"]]
        ),
         aws.ec2.SecurityGroupIngressArgs(
          from_port=80,
          to_port=80,
          protocol="tcp",
          cidr_blocks=[networks1["traffic_ipv4_any"]]
        ),
          aws.ec2.SecurityGroupIngressArgs(
          from_port=443,
          to_port=443,
          protocol="tcp",
          cidr_blocks=[networks1["traffic_ipv4_any"]]
        ),
          aws.ec2.SecurityGroupIngressArgs(
          from_port=0,
          to_port=0,
          protocol="icmp",
          cidr_blocks=[networks1["hubblock"]]
        ),
     ],
     egress=[
         aws.ec2.SecurityGroupEgressArgs(
             from_port=0,
             to_port=0,
             protocol="-1",
             cidr_blocks=[networks1["traffic_ipv4_any"]]
         )
     ],
     tags={
         "Name" : "security1grp3"
     }
     )
)

spoke3instance1=aws.ec2.Instance(
  "spoke3instance1",
  aws.ec2.InstanceArgs(
  ami=insttools["instami"],
  instance_type=insttools["instancetypes"],
  key_name=insttools["keys2"],
  vpc_security_group_ids=[security1grp3.id],
  ebs_block_devices=[
      aws.ec2.InstanceEbsBlockDeviceArgs(
          device_name="/dev/sdl",
          volume_size=8,
          volume_type="gp2",
          encrypted="false",
          delete_on_termination=True
      )
  ],
  user_data=userdata1,
  tags={
    "Name" :"spoke3instance1"
  },
  subnet_id=inst1subnet3.id,
  availability_zone=networks1["zone1a"]
  )
)

spoke3instance2=aws.ec2.Instance(
  "spoke3instance2",
  aws.ec2.InstanceArgs(
  ami=insttools["instami"],
  instance_type=insttools["instancetypes"],
  key_name=insttools["keys2"],
  vpc_security_group_ids=[security1grp3.id],
  ebs_block_devices=[
      aws.ec2.InstanceEbsBlockDeviceArgs(
          device_name="/dev/sdk",
          volume_size=8,
          volume_type="gp2",
          encrypted="false",
          delete_on_termination=True
      )
  ],
  user_data=userdata1,
  tags={
    "Name" :"spoke3instance2"
  },
  subnet_id=inst2subnet3.id,
  availability_zone=networks1["zone1b"]
  )
)

#  transit gateway attachment hub , spoke2 , spoke3 

vpc1attach1=aws.ec2transitgateway.VpcAttachment(
 "vpc1attach1",
 aws.ec2transitgateway.VpcAttachmentArgs(
 subnet_ids=[tgw1subnet1.id , tgw2subnet1.id],
 vpc_id=vpc1.id,
 appliance_mode_support="enable",
 ipv6_support="disable",
 transit_gateway_default_route_table_association=False,
 transit_gateway_default_route_table_propagation=False,
 transit_gateway_id=tgw1conn1.id,
 tags={
     "Name" :  "vpc1attach1"
 },
  dns_support="enable"
 )

)

vpc2attach2=aws.ec2transitgateway.VpcAttachment(
 "vpc2attach2",
 aws.ec2transitgateway.VpcAttachmentArgs(
 subnet_ids=[inst1subnet2.id,inst2subnet2.id],
 vpc_id=vpc2.id,
 appliance_mode_support="enable",
 ipv6_support="disable",
 transit_gateway_default_route_table_association=False,
 transit_gateway_default_route_table_propagation=False,
 transit_gateway_id=tgw1conn1.id,
 tags={
     "Name" :  "vpc2attach2"
 },
  dns_support="enable"
 )

) 
vpc3attach3=aws.ec2transitgateway.VpcAttachment(
 "vpc3attach3",
 aws.ec2transitgateway.VpcAttachmentArgs(
 subnet_ids=[inst1subnet3.id,inst2subnet3.id],
 vpc_id=vpc3.id,
 appliance_mode_support="enable",
 ipv6_support="disable",
 transit_gateway_default_route_table_association=False,
 transit_gateway_default_route_table_propagation=False,
 transit_gateway_id=tgw1conn1.id,
 tags={
     "Name" :  "vpc3attach3"
 },
 dns_support="enable"
 )
)

tgw1routetable1=aws.ec2transitgateway.RouteTable(
    "tgw1routetable1",
    aws.ec2transitgateway.RouteTableArgs(
     transit_gateway_id=tgw1conn1.id,
     tags={
         "Name" :  "tgw1routetable1"
     }
    )
)

tgw1route1=aws.ec2transitgateway.Route(
    "tgw1route1",
    aws.ec2transitgateway.RouteArgs(
     transit_gateway_attachment_id=vpc1attach1.id,
     transit_gateway_route_table_id=tgw1routetable1.id,
     destination_cidr_block=networks1["traffic_ipv4_any"]
    )
)
tgw1route2=aws.ec2transitgateway.Route(
    "tgw1route2",
        aws.ec2transitgateway.RouteArgs(

     transit_gateway_route_table_id=tgw1routetable1.id,
     destination_cidr_block=networks1["rangeblock"],
     blackhole=True
        )
)


tgw1link1=aws.ec2transitgateway.RouteTableAssociation(
    "tgw1link1",
    aws.ec2transitgateway.RouteTableAssociationArgs(
    transit_gateway_attachment_id=vpc2attach2.id,
    transit_gateway_route_table_id=tgw1routetable1.id
    )
)
tgw1link2=aws.ec2transitgateway.RouteTableAssociation(
    "tgw1link2",
        aws.ec2transitgateway.RouteTableAssociationArgs(

    transit_gateway_attachment_id=vpc3attach3.id,
    transit_gateway_route_table_id=tgw1routetable1.id
        )
)
tgw1prp1=aws.ec2transitgateway.RouteTablePropagation(
    "tgw1prp1",
    aws.ec2transitgateway.RouteTablePropagationArgs(
    transit_gateway_attachment_id=vpc1attach1.id,
    transit_gateway_route_table_id=tgw1routetable1.id
    )
)


tgw2routetable2=aws.ec2transitgateway.RouteTable(
    "tgw2routetable2",
    aws.ec2transitgateway.RouteTableArgs(
     transit_gateway_id=tgw1conn1.id,
     tags={
         "Name" :  "tgw2routetable2"
     }
    )
)


tgw2route1=aws.ec2transitgateway.Route(
    "tgw2route1",
    aws.ec2transitgateway.RouteArgs(
     transit_gateway_attachment_id=vpc2attach2.id,
     transit_gateway_route_table_id=tgw2routetable2.id,
     destination_cidr_block=networks1["spoke1block1"]
    )
)
tgw2route2=aws.ec2transitgateway.Route(
    "tgw2route2",
    aws.ec2transitgateway.RouteArgs(
    transit_gateway_attachment_id=vpc3attach3.id,
    transit_gateway_route_table_id=tgw2routetable2.id,
    destination_cidr_block=networks1["spoke2block2"]
    )
)

tgw2link1=aws.ec2transitgateway.RouteTableAssociation(
    "tgw2link1",
    aws.ec2transitgateway.RouteTableAssociationArgs(
    transit_gateway_attachment_id=vpc1attach1.id,
    transit_gateway_route_table_id=tgw2routetable2.id
    )
)
tgw2prp1=aws.ec2transitgateway.RouteTablePropagation(
    "tgw2prp1",
    aws.ec2transitgateway.RouteTablePropagationArgs(
    transit_gateway_attachment_id=vpc2attach2.id,
    transit_gateway_route_table_id=tgw2routetable2.id
    )
)

tgw2prp2=aws.ec2transitgateway.RouteTablePropagation(
    "tgw2prp2",
    aws.ec2transitgateway.RouteTablePropagationArgs(
    transit_gateway_attachment_id=vpc3attach3.id,
    transit_gateway_route_table_id=tgw2routetable2.id
    )
)

routetable_spoke2=aws.ec2.RouteTable(
    "routetable_spoke2",
    aws.ec2.RouteTableArgs(
    vpc_id=vpc2.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block=networks1["traffic_ipv4_any"],
            transit_gateway_id=tgw1conn1.id
        ) 
    ],
    tags={
        "Name" :  "routetable_spoke2"
    }
    )
)

routetable_spoke3=aws.ec2.RouteTable(
   "routetable_spoke3",
   aws.ec2.RouteTableArgs(
    vpc_id=vpc3.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block=networks1["traffic_ipv4_any"],
            transit_gateway_id=tgw1conn1.id
        )
    ],
    tags={
        "Name" :  "routetable_spoke3"
    }
   )
)

spoke1link2a=aws.ec2.RouteTableAssociation(
    "spoke1link2a",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=inst1subnet2.id,
    route_table_id=routetable_spoke2.id
    )
)


spoke1link2b=aws.ec2.RouteTableAssociation(
    "spoke1link2b",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=inst2subnet2.id,
    route_table_id=routetable_spoke2.id
    )
)

spoke3link3a=aws.ec2.RouteTableAssociation(
    "spoke3link3a",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=inst1subnet3.id,
    route_table_id=routetable_spoke3.id
    )
)

spoke3link3b=aws.ec2.RouteTableAssociation(
    "spoke3link3b",
    aws.ec2.RouteTableAssociationArgs(
    subnet_id=inst2subnet3.id,
    route_table_id=routetable_spoke3.id
    )
)


myservices={
    "service1" : "vpc-flow-logs.amazonaws.com",
    "assumepolicy" : "sts:AssumeRole"
}

hublogs=aws.cloudwatch.LogGroup(
    "hublogs",
    aws.cloudwatch.LogGroupArgs(
    name="hubgrps",
    tags={
        "Name" :  "hublogs"
    }
    )
)

spoke2logs=aws.cloudwatch.LogGroup(
    "spoke2logs",
    aws.cloudwatch.LogGroupArgs(

    name="spoke2grps",
    tags={
        "Name" :  "spoke2logs"
    }
    )
)

spoke3logs=aws.cloudwatch.LogGroup(
    "spoke3logs",
        aws.cloudwatch.LogGroupArgs(

    name="spoke3grps",
    tags={
        "Name" :  "spoke3logs"
    }
        )
)

flowrole=aws.iam.Role(
  "flowrole",
  aws.iam.RoleArgs(
  name="flowauth",
  assume_role_policy=json.dumps({
      
     "Version" : "2012-10-17",
     "Statement" : [{
          "Effect" : "Allow",
          "Action" : myservices["assumepolicy"],
          "Principal" : {
              "Service" : myservices["service1"]
          }
     }]
  })
  )
)

logspolicy=aws.iam.Policy(
    "logspolicy",
    aws.iam.PolicyArgs(
    policy=json.dumps({
      "Version" :  "2012-10-17",
      "Statement" :[{
          "Effect" : "Allow",
             "Action": [
             "logs:CreateLogStream",
             "logs:DescribeLogGroups",
             "logs:DescribeLogStreams",
             "logs:GetLogEvents",
             "logs:PutLogEvents"
           ],
          "Resource":["arn:aws:logs:us-east-1:11733766600:log-group:hubgrps:*",
                "arn:aws:logs:us-east-1:11733766600:log-group:spoke2grps:*", 
                "arn:aws:logs:us-east-1:11733766600:log-group:spoke3grps:*" ],
      }]
    })
    )
)

attach1logs=aws.iam.RolePolicyAttachment(
    "attach1logs",
    aws.iam.RolePolicyAttachmentArgs(
    role=flowrole.name,
    policy_arn=logspolicy.arn
    )
)

hubflow=aws.ec2.FlowLog(
  "hubflow",
  aws.ec2.FlowLogArgs(
  vpc_id=vpc1.id,
  log_destination_type="cloud-watch-logs",
  log_destination=hublogs.arn,
  traffic_type="ALL",
  tags={
      "Name": "hubflow"
  },
  iam_role_arn=flowrole.arn
  )
)

spoke2flow=aws.ec2.FlowLog(
  "spoke2flow",
  aws.ec2.FlowLogArgs(
  vpc_id=vpc2.id,
  log_destination_type="cloud-watch-logs",
  log_destination=spoke2logs.arn,
  traffic_type="ALL",
  tags={
      "Name": "spoke2flow"
  },
  iam_role_arn=flowrole.arn
  )
)

spoke3flow3=aws.ec2.FlowLog(
  "spke3flow3",
  aws.ec2.FlowLogArgs(
  vpc_id=vpc3.id,
  log_destination_type="cloud-watch-logs",
  log_destination=spoke3logs.arn,
  traffic_type="ALL",
  tags={
      "Name": "spoke3flow3"
  },
  iam_role_arn=flowrole.arn
  )
)


pulumi.export( "Instance1" ,  value=instance1.public_ip)
pulumi.export( "Instance2" ,  value=instance2.public_ip)
pulumi.export( "spoke2inst1" ,  value=spoke2instance1.private_ip)
pulumi.export( "spoke2inst2" ,  value=spoke2instance2.private_ip)
pulumi.export( "spoke3inst1" ,  value=spoke3instance1.private_ip)
pulumi.export( "spoke3inst2" ,  value=spoke3instance2.private_ip)