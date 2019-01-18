import sys, argparse, boto3, time
import utils

Parser = argparse.ArgumentParser(description='Script to manage EFS filesystems (describe, create, delete).')

# --------------------
# Required Arguments
# --------------------
ParseGroup = Parser.add_mutually_exclusive_group()
ParseGroup.add_argument('-v', '--describe', action='store_true', help='Describe all available EFS filesystems.')

ReqGroup = Parser.add_mutually_exclusive_group()

ReqGroup.add_argument('-c', '--create-efs', help='Create a new file system with a name tag.', metavar='EFS_NAME')
ReqGroup.add_argument('-d', '--delete-efs', help='Delete an existing file system by FileSystemId.', metavar='FS-ID', nargs='+')

if __name__ == '__main__':
    if 'linux' not in str(sys.platform):
        raise RuntimeError('Unsupported OS. Only Linux is supported.')

    if len(sys.argv) == 1:
        Parser.print_help()
        exit()

    Args = Parser.parse_args()
    EFSClient = boto3.client('efs')

    if Args.create_efs:
        utils.createEFS(EFSClient, Args.create_efs)
    elif Args.delete_efs:
        for EFSID in Args.delete_efs:
            utils.deleteEFS(EFSClient, EFSID)
        time.sleep(1) # Sleep for a minute

    utils.printEFSStatus(EFSClient)