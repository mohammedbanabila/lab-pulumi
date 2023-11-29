# lab-pulumi

Steps:
1.	We create 3 vpc with their cidrblock ranges:
Vpc1=81.48.0.0/16 
Vpc2=80.16.0.0/16
Vpc3=80.32.0.0/16


2.	In vpc1 have only connection to internet through Internet gateway so for outbound connection will use multiple Nat gateway per Az in vpc for high availability.
3.	In vpc1 create 4 subnets for 2 Azs and those subnets: 
Publicsubnet1=81.48.16.0/20
Publicsubnet2=81.48.32.0/20
Tgw1subnet1=81.48.48.0/20
Tgw2subnet2=81.48.64.0/20

Note: 
Those subnet of tgw1subnet1 and tgw2subnet will be associate with transit gateway vpc attachment.
Those subnet of publicsubnet1 and publicsubnet2 will have 2 instance acts as jump host to connect other instances in vpc2 and vpc3 act as spoke vpcs. only way to connect to internet by passing through transit gateway to egress vpc whose have access internet by using Nat gateway as Outbound connection.


4.	In vpc2 and vpc3 has 2 subnets per Az
Inst1subnet2=80.16.48.0/20
Inst2subnet2=80.16.64.0/20
Inst1subnet=80.32.48.0/20
Inst2subnet=8032.64.0/20
Those subnets of vpc2 and vpc3 will be associate it with their transit gateway vpc attachment.
5.	In vpc1, we will use summarize range 80.0.0.0/8 that let egress vpc to communicate with their spoke vpc through transit gateway to reduce size of route table. with security group and network access control list to access spoke vpc with ssh port 22 and from spoke vpc can ping to internet
6.	In vpc2 and vpc3 connect to egress vpc through transit gateway to reach to internet but will not let both vpcs connect each other using blackhole 80.0.0.0/8 indicate to not communicate each other at their transit gateway route table
7.	Create   transit gateway in region us-east-1
    1.default route table association and default route table propagation are both disable
    2. disable multicast support
    3. disable vpn ecmp  
    4. enable dns support 
    5. support only ipv4
    6. amazon ASN 64514
8. create 3 transit gateway vpc attachment for vpc1, vpc2, vpc3
     Note:  enable appliance mode support so that the traffic flow will not drop at each vpc attachment

8.	Create 3 vpc flow log for vpc1, vpc2, vpc3 with their cloud watch log group attach it by using iam role with service vpc-flow-logs.amazonaws.co to allow collect all logs events of each vpc with their log group 

9.	For transit gateway vpc attachment

Vpc1attach1=belong to vpc1=81.48.0.0/16
Vpc2attach2=belong to vpc2=80.16.0.0/16
Vpc3attach3=belong to vpc3=80.32.0.0/16

10.	Create 2   transit gateway route table for vpc2attach2 and vpc3attach3
           Tgw1routetable1 has associate with transit gateway 
         1.   For transit gateway route for tgw1routetable1 
                      Transit gateway vpc attachment=vpc1attach1
                       Transit gateway route table= tgw1routetable1
                        Destination cidr block   0.0.0.0/0 [to let us to reach to internet through transit gateway]
        2. for transit gateway route for tgw1routetable1
                      Transit gateway route table=tgw1routetable1
                      Blackhole=true [ indicate will not both vpc2 and vpc3 communicate each other]
                      Destination cidr block 80.0.0.0/8

       3. associate transit gateway route table=tgw1routetable1 with vpc2attach2 and vpc3attach3   
       4. propagate the vpc1attach1 to transit gateway route table=tgw1routetable1
          

11.	 Create transit gateway route table for vpc1attach1 = tgw2routetable2
This transit gateway route table associate with transit gateway

12.	 Create transit gateway route for vpc1attach1 to associate it with tgw2routetable2
    
 Transit gateway route 
      Transit gateway vpc attachment =vpc2attach2 
      Transit gateway route table = tgw2routetable2 
      Destination cidr block = 80.16.0.0/16
Transit gateway route
      Transit gateway vpc attachment =vpc3attach3
      Transit gateway route table = tgw2routetable2 
      Destination cidr block = 80.32.0.0/16

1.associate transit gateway routes to transit gateway route table =tgw2routetable2 along with vpc1attach1
2.propagate vpc2attach2 and vpc3attach3 to transit gateway route table=tgw2routetable2 


13.	at vpc2 and vpc3, manually add route 0.0.0.0/0 that attach it to transit gateway on their route table  
14.	those route table associate with their subnets that let instances can passing to internet at vpc2 and vpc3
15.	in vpc1, add manually route 0.0.0.0/0 in 2 route table that attach to multiple Nat gateway per Az and those route tables are attach to tgw1subnet1 and tgw2subnet1 so the traffic flow come from transit gateway route of    vpc2attach2 and vpc3attach to reach to internet.
16.	in vpc1, add route 80.0.0.0/8 [summarize route for vpc2 and vpc3] attach with transit gateway along with route 0.0.0.0/0 attach to internet gateway


    Notes:
1.	will be cost in data transfer between vpcs 
2.	will be cost in data transfer nat gateway 
3.	will be cost in no, of vpc attachment per transit gateway 
those factor depend in which region you are deploying the resources

