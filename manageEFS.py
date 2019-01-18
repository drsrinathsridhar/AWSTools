import sys, argparse, boto3, time, random
import utils

Parser = argparse.ArgumentParser(description='Script to manage EFS filesystems (describe, create, delete).')

# --------------------
# Required Arguments
# --------------------
ParseGroup = Parser.add_mutually_exclusive_group()
ParseGroup.add_argument('-v', '--describe', action='store_true', help='Describe all available EFS filesystems.')
ParseGroup.add_argument('-l', '--list-fs-id', action='store_true', help='List all filesystem IDs only.')
ParseGroup.add_argument('-c', '--create-efs', help='Create a new file system with a name tag.', metavar='EFS_NAME')
ParseGroup.add_argument('-d', '--delete-efs', help='Delete an existing file system by FileSystemId.', metavar='FS-ID', nargs='+')

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
        time.sleep(random.randint(2, 5)) # Sleep for a second

    utils.printEFSStatus(EFSClient)

    if Args.list_fs_id:
        AllEFS = utils.getAllEFSInfoByToken(EFSClient, 'FileSystemId')
        print('[ INFO ]: List of EFS filesystem IDs - ', end='')
        for FS in AllEFS:
            print(FS, end=' ')
        print('\n', end='')