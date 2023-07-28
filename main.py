import boto3
import botocore
import os

def lambda_handler(event, context):
    vmx1 = os.environ['vmx1']
    vmx2 = os.environ['vmx2']
    routetable = os.environ['routetable']
    region = os.environ['region']
    ec2 = boto3.resource('ec2',region_name=region)
    client = boto3.client('ec2',region_name=region)
    route_table = ec2.RouteTable(routetable)
    
    if event['detail']['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['InstanceId'] == vmx1:
        #Check status of vmx2 to ensure its ok to use if not set to self (used in case both instances are offline and this is the one being brought online)
        try:
            response = client.describe_instance_status(InstanceIds=[vmx2])
            vmx_instance = response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status']
            vmx_system = response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']
            if vmx_instance == 'passed' and vmx_system == 'passed':
                instance = vmx2
            else:
                instance = vmx1
        except:
            instance = vmx1

        #Remove old route
        try:
            response = client.delete_route(
                DestinationCidrBlock='10.0.0.0/8',
                RouteTableId=routetable
            )
        
        except botocore.exceptions.ClientError as error:
            print(error)
        #Add new route
        try:
            route = route_table.create_route(
                DestinationCidrBlock='10.0.0.0/8',
                InstanceId=instance
            )
            print(f'Updated route to use {instance}')
        except botocore.exceptions.ClientError as error:
            print(error)
        
    elif event['detail']['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['InstanceId'] == vmx2:
        #Check status of vmx2 to ensure its ok to use if not set to self (used in case both instances are offline and this is the one being brought online)
        try:
            response = client.describe_instance_status(InstanceIds=[vmx1])
            vmx_instance = response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status']
            vmx_system = response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']
            if vmx_instance == 'passed' and vmx_system == 'passed':
                instance = vmx1
            else:
                instance = vmx2
        except:
            instance = vmx2
        #Remove Old Route
        try:
            response = client.delete_route(
                DestinationCidrBlock='10.0.0.0/8',
                RouteTableId=routetable
            )
        except botocore.exceptions.ClientError as error:
            print(error)

        #Add new route
        try:
            route = route_table.create_route(
                DestinationCidrBlock='10.0.0.0/8',
                InstanceId=instance
            )
            print(f'Updated route to use {instance}')
        except botocore.exceptions.ClientError as error:
            print(error)