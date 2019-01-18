import sys, argparse, boto3, time, random
import utils

Parser = argparse.ArgumentParser(description='Script to manage EC2 instances (describe, create, start, stop, terminate).')

# --------------------
# Required Arguments
# --------------------
ParseGroup = Parser.add_mutually_exclusive_group()
ParseGroup.add_argument('-v', '--describe', action='store_true', help='Describe all available EC2 instances.')
ParseGroup.add_argument('-t', '--terminate-instance', help='Delete existing EC2 instances.', metavar='INSTANCE-IDs', nargs='+')
ParseGroup.add_argument('-c', '--create-instance', help='Create a new instance.', action='store_true')
ParseGroup.add_argument('-a', '--start-instance', help='Start (not create) existing EC2 instances.', metavar='INSTANCE-IDs', nargs='+')
ParseGroup.add_argument('-o', '--stop-instance', help='Stop (not terminate) existing EC2 instances.', metavar='INSTANCE-IDs', nargs='+')

Parser.add_argument('--dry-run', action='store_true')
Parser.add_argument('--show-terminated', action='store_true')

if __name__ == '__main__':
    if 'linux' not in str(sys.platform):
        raise RuntimeError('Unsupported OS. Only Linux is supported.')

    if len(sys.argv) == 1:
        Parser.print_help()
        exit()

    Args = Parser.parse_args()
    EC2Client = boto3.client('ec2')

    if Args.create_instance:
        print('[ WARN ]: Since creating instances is complicated, please use the createEC2.py script.')
        exit()
    elif Args.terminate_instance:
        utils.terminateEC2(EC2Client, Args.terminate_instance, DryRun=Args.dry_run)
    elif Args.start_instance:
        utils.startEC2(EC2Client, Args.start_instance, DryRun=Args.dry_run)
    elif Args.stop_instance:
        utils.stopEC2(EC2Client, Args.stop_instance, DryRun=Args.dry_run)

    time.sleep(random.randint(2, 5))  # Sleep for a few seconds
    utils.printEC2Status(EC2Client, showTerminated=Args.show_terminated)