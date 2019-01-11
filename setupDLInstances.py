import os, sys, argparse, json, ipaddress
import utils

Parser = argparse.ArgumentParser(description='Setup deep learning instances with required software, scripts, repos, etc. And stop them to avoid charges.')

# --------------------
# Required Arguments
# --------------------
Parser.add_argument('--project-name', help='Provide a name for this deep learning project.', required=True)
Parser.add_argument('--key-name', help='Provide an SSH key name to be used for creating instances.', required=True)
Parser.add_argument('--vpc-id', help='Provide the ID of VPC to use. If not provided some default VPC is used.', required=True, default='None')
Parser.add_argument('--subnet-id', help='Provide the subnet ID of VPC to use. If not provided some default VPC is used.', required=True)
Parser.add_argument('--efs-name', help='Provide a name for an existing deep learning EFS where custom directories will be created.', required=True)
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
    # utils.printArgs(Args)

    BaseEC2Call = 'aws ec2 '
    BaseEFSCall = 'aws efs '

    Command = BaseEC2Call + 'run-instances --image-id ' + Args.image_id + ' --count 1 --instance-type ' + Args.instance_type + ' --key-name ' + Args.key_name + ' --security-groups ' + Args.security_group
    print(Command)