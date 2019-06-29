import sys, argparse, boto3, time, random, os
import utils

Parser = argparse.ArgumentParser(description='Script to create EC2 instances.')

# --------------------
# Required Arguments
# --------------------
ParseGroup = Parser.add_argument_group()
ParseGroup.add_argument('-k', '--key-path', help='Path to the key. Key name is extracted from the filename.', type=str, required=True)
ParseGroup.add_argument('-a', '--ami-image-id', help='AMI ID.', default=utils.AMI_FREETIER, required=False)
ParseGroup.add_argument('-t', '--instance-type', help='The instance type.', default=utils.INSTANCE_TYPE_FREETIER, required=False)

Parser.add_argument('--dry-run', action='store_true')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        Parser.print_help()
        exit()

    Args = Parser.parse_args()
    EC2Client = boto3.client('ec2')

    KeyPath = Args.key_path
    KeyName = os.path.splitext(os.path.basename(KeyPath))[0]

    print('[ INFO ]: Using key name', KeyName, 'at', KeyPath)
    print('[ INFO ]: AMI', Args.ami_image_id)
    print('[ INFO ]: Instance type', Args.instance_type)

    utils.createEC2(EC2Client, KeyName, ImageId=Args.ami_image_id, InstanceType=Args.instance_type, DryRun=Args.dry_run)
    print('[ INFO ]: Waiting for a few seconds...' )
    time.sleep(random.randint(5, 10))  # Sleep for a few seconds
    utils.printEC2Status(EC2Client)