import os, sys, subprocess, argparse, json, ipaddress

Parser = argparse.ArgumentParser(description='Initial AWS setup for a deep learning project.')

# --------------------
# Required Arguments
# --------------------
Parser.add_argument('--project-name', help='Provide a name for this deep learning project.', required=True)
Parser.add_argument('--key-name', help='Provide an SSH key name to be used for creating instances.', required=True)
# --------------------
# Optional Arguments
# --------------------
Parser.add_argument('--count', help='How many instance counts to create. Default is 1.', required=False, default=1, type=int)
Parser.add_argument('--security-group', help='Provide an optional security-group. If not provided, ''default'' will be used.', required=False, default='default')
Parser.add_argument('--image-id', help='Provide an AMI image ID. Default is ''ami-0c9ae74667b049f59''.', required=False, default='ami-0c9ae74667b049f59')
Parser.add_argument('--instance-type', help='Provide an instance type. Default is ''p3.2xlarge''.', required=False, default='p3.2xlarge')
Parser.add_argument('--vpc-id', help='Provide the ID of VPC to use. If not provided some default VPC is used.', required=False, default='None')

def spCommandTokenize(CommandStr):
    return CommandStr.split()

def runCommand(Command):
    try:
        Output = subprocess.check_output(spCommandTokenize(Command))
        # print(Output)
    except Exception as error:
        print('[ ERR ]: ' + repr(error))
        exit()

    return Output

if __name__ == '__main__':
    if 'linux' not in str(sys.platform):
        raise RuntimeError('Unsupported OS. Only Linux is supported.')

    Args = Parser.parse_args()
    ArgsDict = vars(Args)
    for Arg in ArgsDict:
        ArgVal = ArgsDict[Arg]
        if ArgsDict[Arg] is None:
            ArgVal = 'None'
        print('{:<15}:   {:<50}'.format(Arg, ArgVal))

    BaseEC2Call = 'aws ec2 '

    # Let's get VPC details
    Output = runCommand(BaseEC2Call + 'describe-vpcs')

    VPCJSON = json.loads(Output)
    if Args.vpc_id == 'None':
        VPCID = VPCJSON['Vpcs'][0]['VpcId'] # First VPC
        VPCCIDR = VPCJSON['Vpcs'][0]['CidrBlock']
    else:
        # Make sure requested VPC exists
        if Args.vpc_id not in str(Output):
            raise RuntimeError('[ ERR ]: VPC ' + Args.vpc_id + ' not found.')

        VPCID = Args.vpc_id
        for VPC in VPCJSON['Vpcs']:
            if VPC['VpcId'] == VPCID:
                VPCCIDR = VPC['CidrBlock']
                break
    print('[ INFO ]: Using VPC', VPCID, 'CIDR', VPCCIDR)

    # Calculate maximum possible IP addresses in VPC
    VPCCIDR_ip = ipaddress.IPv4Network(VPCCIDR)
    VPC_IPRange = []
    for Addr in VPCCIDR_ip:
        VPC_IPRange.append(Addr)
    VPCMaxAddr = len(VPC_IPRange)

    # Let's get subnet details
    Output = runCommand(BaseEC2Call + 'describe-subnets')

    AllSubnets = VPCCIDR_ip.subnets(prefixlen_diff=4)
    UsedSubnetsJSON = json.loads(Output)
    UsedSubnets = []
    for SN in UsedSubnetsJSON['Subnets']:
        UsedSubnets.append(SN['CidrBlock'])
    ValidSubnets = []
    for SN in AllSubnets:
        if str(SN) not in UsedSubnets:
            ValidSubnets.append(SN)
        # else:
        #     print('[ INFO ]: Excluding pre-existing subnet', str(SN))

    if len(ValidSubnets) <= 0:
        raise RuntimeError('Ran out of subnets, please check your AWS VPC console.')

    # First create a subnet to use for this project in the VPC
    print('[ INFO ]: Using subnet', ValidSubnets[0])
    Command = BaseEC2Call + 'create-subnet --vpc-id ' + VPCID + ' --cidr-block ' + str(ValidSubnets[0])

    Output = runCommand(Command)

    Command = BaseEC2Call + 'run-instances --image-id ' + Args.image_id + ' --count 1 --instance-type ' + Args.instance_type + ' --key-name ' + Args.key_name + ' --security-groups ' + Args.security_group
    print(Command)
