import os, sys, subprocess, argparse

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

    # First create a subnet to use for this project
    'aws ec2 create-subnet  --cidr-block 10.0.1.0/24'

    subprocess.call(['aws', 'ec2', 'create-subnet', '--vpc-id vpc-a01106c2'])

    # 'aws ec2 run-instances --image-id ami-0c9ae74667b049f59 --count 1 --instance-type p3.2xlarge --key-name ssrinath_aws --security-groups default'
    subprocess.call(['watch', '-n', '1', 'nvidia-smi'])

