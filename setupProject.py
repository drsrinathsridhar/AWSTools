import os, sys, argparse, json, ipaddress, random, time
import boto3
from botocore.exceptions import ClientError
import utils

Parser = argparse.ArgumentParser(description='Initial AWS setup for a deep learning project.')

# --------------------
# Required Arguments
# --------------------
Parser.add_argument('--project-name', help='Provide a name for this deep learning project.', required=True)
Parser.add_argument('--efs-name', help='Provide a name for an existing deep learning EFS where custom directories will be created.', required=True)
Parser.add_argument('--key-name', help='Provide an SSH key name to be used for creating instances.', required=True)
Parser.add_argument('--key-path', help='Provide path to private SSH key corresponding to key-name.', required=True)

if __name__ == '__main__':
    if 'linux' not in str(sys.platform):
        raise RuntimeError('Unsupported OS. Only Linux is supported.')

    Args = Parser.parse_args()
    if len(sys.argv) == 1:
        Parser.print_help()
        exit()

    EC2Client = boto3.client('ec2')
    SSMClient = boto3.client('ssm')

    try:
        print('[ INFO ]: Creating temporary instance...')
        InstanceID = utils.createEC2(EC2Client, Args.key_name, utils.AMI_FREETIER, utils.INSTANCE_TYPE_FREETIER,
                                     MaxCount=1, DryRun=False)
        utils.printEC2Status(EC2Client)
        Timeout = 100
        print('[ INFO ]: Waiting maximum of {} seconds for instance to start.'.format(Timeout))
        utils.waitForEC2(EC2Client, InstanceID, TargetState='running', TimeOut=Timeout)
        PublicIP = utils.getEC2InfoByToken(EC2Client, InstanceID)
        print('[ INFO ]: New instance has PublicIp - ', PublicIP)

        ProjectDir = '~/efs/{}'.format(Args.project_name)
        CommandList = ['sudo apt-get -y install nfs-common',
                       'mkdir -p efs',
                       'sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport {}.efs.us-east-2.amazonaws.com:/ efs'.format(
                           Args.efs_name)
                       ]

        utils.runCommandEC2(Args.key_path, Commands=CommandList, InstancePublicIp=PublicIP, Verbose=1)


        ProjectDirExists = utils.existsRemotePath('ubuntu', str(PublicIP), ProjectDir, KeyPath=Args.key_path)

        print('ProjectDirExists:', ProjectDirExists)

        if ProjectDirExists:
            print('[ INFO ]: Project director already exists at', ProjectDir)
        else:
            CommandList = ['sudo mkdir -p {}'.format(ProjectDir), 'ls -l efs']

            utils.runCommandEC2(Args.key_path, Commands=CommandList, InstancePublicIp=PublicIP, Verbose=1)
    except Exception as e:
        print('[ ERR ]: Failed to run commands:', e)

    utils.runCommandEC2(Args.key_path, Commands=['sudo umount efs'], InstancePublicIp=PublicIP, Verbose=1)
    utils.terminateEC2(EC2Client, [InstanceID], Yes=True, DryRun=False)


## OLD BUT USEFUL CODE
    # # Let's get VPC details
    # Output = utils.runCommand(BaseEC2Call + 'describe-vpcs')
    #
    # VPCJSON = json.loads(Output)
    # if Args.vpc_id == 'None':
    #     VPCID = VPCJSON['Vpcs'][0]['VpcId'] # First VPC
    #     VPCCIDR = VPCJSON['Vpcs'][0]['CidrBlock']
    # else:
    #     # Make sure requested VPC exists
    #     if Args.vpc_id not in str(Output):
    #         raise RuntimeError('[ ERR ]: VPC ' + Args.vpc_id + ' not found.')
    #
    #     VPCID = Args.vpc_id
    #     for VPC in VPCJSON['Vpcs']:
    #         if VPC['VpcId'] == VPCID:
    #             VPCCIDR = VPC['CidrBlock']
    #             break
    #
    # # Calculate maximum possible IP addresses in VPC
    # VPCCIDR_ip = ipaddress.IPv4Network(VPCCIDR)
    # VPC_IPRange = []
    # for Addr in VPCCIDR_ip:
    #     VPC_IPRange.append(Addr)
    # VPCMaxAddr = len(VPC_IPRange)
    #
    # # Let's get subnet details
    # Output = utils.runCommand(BaseEC2Call + 'describe-subnets')
    #
    # AllSubnets = VPCCIDR_ip.subnets(prefixlen_diff=4)
    # UsedSubnetsJSON = json.loads(Output)
    # UsedSubnets = []
    # for SN in UsedSubnetsJSON['Subnets']:
    #     UsedSubnets.append(SN['CidrBlock'])
    # ValidSubnets = []
    # for SN in AllSubnets:
    #     if str(SN) not in UsedSubnets:
    #         ValidSubnets.append(SN)
    #     # else:
    #     #     print('[ INFO ]: Excluding pre-existing subnet', str(SN))
    #
    # if len(ValidSubnets) <= 0:
    #     raise RuntimeError('Ran out of subnets, please check your AWS VPC console.')
    #
    # # Create a subnet to use for this project in the VPC
    # Command = BaseEC2Call + 'create-subnet --vpc-id ' + VPCID + ' --cidr-block ' + str(ValidSubnets[0])
    # Output = utils.runCommand(Command)
    # SubnetJSON = json.loads(Output)
    # SubnetID = SubnetJSON['Subnet']['SubnetId']
    #
    # print('----------------------------------------------------------------------------')
    # print('[ INFO ]: Project name', Args.project_name)
    # print('[ INFO ]: Using VPC', VPCID, 'CIDR', VPCCIDR)
    # print('[ INFO ]: Created subnet', SubnetID, 'with CIDR', ValidSubnets[0])
    # print('----------------------------------------------------------------------------')
