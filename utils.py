import subprocess, json, boto3, uuid, sys
from distutils.util import strtobool

def yesNoQuery(question):
    sys.stdout.write('[ INP ]: %s [y/n]\n' % question)
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write('[ INP ]: Please respond with \'y\' or \'n\'.\n')

def spCommandTokenize(CommandStr):
    return CommandStr.split()

def runCommand(Command, shell=False, isPrint=False):
    try:
        if shell == False:
            Output = subprocess.check_output(spCommandTokenize(Command))
        else:
            Output = subprocess.check_output(Command, shell=True)
    except Exception as error:
        print('[ ERR ]: ' + repr(error))
        exit()

    if isPrint:
        printOutput(Output)

    return Output

def runCommandList(CommandList, shell=False, isPrint=False):
    try:
        if shell == False:
            Output = subprocess.check_output(CommandList)
        else:
            Output = subprocess.check_output(CommandList, shell=True)
    except Exception as error:
        print('[ ERR ]: ' + repr(error))
        exit()

    if isPrint:
        printOutput(Output)

    return Output

def printArgs(Args):
    ArgsDict = vars(Args)
    for Arg in ArgsDict:
        ArgVal = ArgsDict[Arg]
        if ArgsDict[Arg] is None:
            ArgVal = 'None'
        print('{:<15}:   {:<50}'.format(Arg, ArgVal))

def printOutput(Output):
    print(Output.decode('unicode-escape'))

def getEC2InstPublicIP(InstanceID):
    Command = 'aws ec2 describe-instances --filters Name=instance-id,Values=' + InstanceID
    Command = Command + """ --query Reservations[*].Instances[*].{InstanceId:InstanceId,PublicDnsName:PublicDnsName,State:State.Name,PublicIpAddress:PublicIpAddress}"""
    Output = runCommand(Command)
    # printOutput(Output)
    JSON = json.loads(Output)

    return JSON[0][0]['PublicIpAddress']

def printEFSStatus(EFSClient):
    try:
        Response = EFSClient.describe_file_systems()
    except Exception as e:
        print('[ WARN ]: Unable to get EFS status.')
        print('[ ERR ]:', e)
        return

    # Pretty print details
    print('[ INFO ]: EFS file system details:', end='')
    RelevantKeys = ['OwnerId', 'CreationToken', 'FileSystemId', 'Name']
    FormatString = '  {:<25.25}  '
    TitleFormatString = '| {:<25.25}  '
    TitleString = ''.join(TitleFormatString.format(e) for e in RelevantKeys)
    HBar = '-' * (len(TitleString))
    print('\n' + HBar)
    print(TitleString, end='')
    print('\n' + HBar)

    for FS in Response['FileSystems']:
        for Key in FS:
            if Key in RelevantKeys:
                print(FormatString.format(str(FS[Key])), end='')
        print('\n', end='')
    print(HBar)

def createEFS(EFSClient, Name):
    try:
        CreateResponse = EFSClient.create_file_system(CreationToken='console-'+str(uuid.uuid4()), PerformanceMode='generalPurpose')
        FSName = CreateResponse['FileSystemId']
        CreateResponse = EFSClient.create_tags(FileSystemId=FSName,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': Name,
                },
            ],
        )
        print('[ INFO ]: Created EFS', FSName, 'with Name', Name)
    except Exception as e:
        print('[ WARN ]: Cannot create EFS. Exception', e)
        return

def deleteEFS(EFSClient, EFSID):
    isRemove = yesNoQuery('Are you sure you want to remove EFS ' + EFSID + '? All data will be lost.')
    if isRemove == False:
        print('[ INFO ]: Not deleting', EFSID)
        return

    try:
        if yesNoQuery('This action will delete all data in ' + EFSID + '. Proceed?') == False:
            print('[ INFO ]: Not deleting', EFSID)
            return
        CreateResponse = EFSClient.delete_file_system(FileSystemId=EFSID)
        print('[ INFO ]: Delete for EFS', EFSID, 'started. It might take a few seconds before it is deleted.')
    except Exception as e:
        print('[ WARN ]: Cannot delete EFS. Exception', e)
        return

