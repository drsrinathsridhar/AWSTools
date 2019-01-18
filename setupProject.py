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

EFSScriptName = 'makeEFSProjectDir.sh'
EFSScript = './scripts/' + EFSScriptName
BaseEC2Call = 'aws ec2 '
BaseEFSCall = 'aws efs '

if __name__ == '__main__':
    if 'linux' not in str(sys.platform):
        raise RuntimeError('Unsupported OS. Only Linux is supported.')

    Args = Parser.parse_args()
    if len(sys.argv) == 1:
        Parser.print_help()
        exit()

    EC2Client = boto3.client('ec2')

    print('[ INFO ]: Creating temporary instance...')
    InstanceID = utils.createEC2(EC2Client, Args.key_name, utils.AMI_FREETIER, utils.INSTANCE_TYPE_FREETIER, MaxCount=1, DryRun=False)
    utils.printEC2Status(EC2Client)
    print(' [ INFO ]: Waiting 10 seconds for instance to start.')
    utils.waitForEC2(EC2Client, InstanceID, TargetState='running', TimeOut=1)

    try:
        print(utils.getAllEC2InfoByToken(EC2Client))
        print(utils.getEC2InfoByToken(EC2Client, InstanceID))
        exit()

        # # Mount EFS directory
        # print('[ INFO ]: SSHing into machine to setup EFS directories... This may take several seconds to a few minutes.')
        # # Copy scripts to instance
        # Command = ['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=1000', '-i', Args.key_path, EFSScript, 'ubuntu@'+InstanceIP+':~/']
        # Output = utils.runCommandList(Command)
        #
        # # Run script
        # Command = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=1000', '-i', Args.key_path, 'ubuntu@'+InstanceIP, 'bash ' + EFSScriptName + ' ' + Args.efs_name + ' ' + Args.project_name]
        # Output = utils.runCommandList(Command)
        # utils.printOutput(Output)
        # # Check if project directory exists. If yes, print details of created isntances, existing instances, subnets, etc.
        # # If not, create directory and proceed
        # # TODO
    except:
        print('[ ERR ]: Failed to create instance or SSH. Aborting.')
        utils.terminateEC2(EC2Client, [InstanceID], Yes=True, DryRun=False)

    # print('[ INFO ]: Instance', InstanceID, 'terminate started.')
    # Command = BaseEC2Call + 'terminate-instances --instance-ids ' + InstanceID
    # Output = utils.runCommand(Command)


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
