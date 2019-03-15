import subprocess, json, boto3, uuid, sys, time, paramiko, pipes
from datetime import datetime
from distutils.util import strtobool

#################################################
# Utils
#################################################
def getCurrentEpochTime():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1e6)

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


def existsRemotePath(Username, Hostname, CheckPath, KeyPath=None):
    try:
        status = subprocess.call(
            ['ssh', '-y', '-i ', KeyPath, Username + '@'+ Hostname, 'test -e {}'.format(pipes.quote(CheckPath))])
        if status == 0:
            return True
        elif status == 1:
            return False
        else:
            print('[ WARN ]: Command likely failed.')
            return None
    except Exception as e:
        print('[ WARN ]: SSH failed - ' + Username + '@'+ Hostname)
        return None


#################################################
# Pre-defined EC2 Instance and AMIs
#################################################
AMI_FREETIER = 'ami-0653e888ec96eab9b'
INSTANCE_TYPE_FREETIER = 't2.micro'

#################################################
# EFS Tools
#################################################
def printEFSStatus(EFSClient):
    try:
        Response = EFSClient.describe_file_systems()
    except Exception as e:
        print('[ WARN ]: Unable to get EFS status.')
        print('[ ERR ]:', e)
        return

    # Pretty print details
    print('[ INFO ]: EFS file system details:', end='')
    RelevantKeys = ['OwnerId', 'CreationToken', 'FileSystemId', 'LifeCycleState', 'Name']
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

def getEFSInfoByToken(EFSClient, FileSystemId, Token='LifeCycleState'):
    try:
        Response = EFSClient.describe_file_systems()
    except Exception as e:
        print('[ WARN ]: Unable to get EFS status.')
        print('[ ERR ]:', e)
        return

    Output = None

    for FS in Response['FileSystems']:
        if FS['FileSystemId'] == FileSystemId:
            Output = FS[Token]

    return Output

def getAllEFSInfoByToken(EFSClient, Token='LifeCycleState'):
    try:
        Response = EFSClient.describe_file_systems()
    except Exception as e:
        print('[ WARN ]: Unable to get EFS status.')
        print('[ ERR ]:', e)
        return

    Output = []

    for FS in Response['FileSystems']:
        Output.append(FS[Token])

    return Output

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
        print('[ INFO ]: Created EFS', FSName, 'with name tag', Name)

        print('[ INFO ]: Waiting for EFS to become available...')
        FSState = getEFSStatusByToken(EFSClient, FSName)
        Ctr = 0
        isSetMountTarget = True
        while FSState != 'available':
            time.sleep(0.1)
            FSState = getEFSStatusByToken(EFSClient, FSName)
            Ctr = Ctr + 1
            if Ctr > 30:
                print('[ WARN ]: State change taking too long. Please setup mount target manually in EFS management console.')
                isSetMountTarget = False
                break

        if isSetMountTarget:
            # Create a default mount target in the current availability zone
            EC2 = boto3.resource('ec2')
            DefaultSubnet = list(EC2.subnets.all())[0]
            print('[ INFO ]: Setup mount target in', DefaultSubnet.id)
            MountResponse = EFSClient.create_mount_target(FileSystemId=FSName, SubnetId=DefaultSubnet.id)

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


#################################################
# EC2 Tools
#################################################
def printEC2Status(EC2Client, showTerminated=False):
    try:
        Response = EC2Client.describe_instances()
    except Exception as e:
        print('[ WARN ]: Unable to get EC2 status.')
        print('[ ERR ]:', e)
        return

    # Pretty print details
    print('[ INFO ]: EC2 instance details', end='')
    if showTerminated == False:
        print(' (not showing terminated instances):', end='')
    else:
        print(':', end='')

    RelevantKeys = ['InstanceId', 'InstanceType', 'State', 'NetworkInterfaces']
    InstancesData = []
    FormatString = '  {:<25.25}  '
    TitleFormatString = '| {:<25.25}  '
    TitleString = ''.join(TitleFormatString.format(e) for e in RelevantKeys)
    HBar = '-' * (len(TitleString))
    print('\n' + HBar)
    print(TitleString, end='')
    print('\n' + HBar)

    for RES in Response['Reservations']:
        for INS in RES['Instances']:
            InstData = []
            for Key in INS:
                if Key == 'NetworkInterfaces':
                    if len(INS[Key]) > 0:
                        if 'Association' in INS[Key][0]:
                            InstData.append(str(INS[Key][0]['Association']['PublicIp']))
                        else:
                            InstData.append('Initializing...')
                    else:
                        InstData.append('NA')
                elif Key == 'State':
                    InstData.append(str(INS[Key]['Name']))
                elif Key in RelevantKeys:
                    InstData.append(str(INS[Key]))
            InstancesData.append(InstData)

    InstancesData.sort(key=lambda x: x[2])
    for Dat in InstancesData:
        if Dat[2] == 'terminated' and showTerminated == False:
            continue
        for Val in Dat:
            print(FormatString.format(Val), end='')
        print('\n', end='')
    print(HBar)


def createEC2(EC2Client, KeyName, ImageId=AMI_FREETIER, InstanceType=INSTANCE_TYPE_FREETIER, MaxCount=1, DryRun=True):
    try:
        CreateResponse = EC2Client.run_instances(ImageId=ImageId, InstanceType=InstanceType, KeyName=KeyName, MinCount=1, MaxCount=MaxCount, DryRun=DryRun)
        Insts = CreateResponse['Instances']
        if len(Insts) > 0:
            print('[ INFO ]: Created instance', Insts[0]['InstanceId'], 'of type', Insts[0]['InstanceType'])
            return Insts[0]['InstanceId']
    except Exception as e:
        print('[ WARN ]: Cannot create EC2 instance. Exception', e)

def startEC2(EC2Client, InstanceIds, DryRun=True):
    try:
        CreateResponse = EC2Client.start_instances(InstanceIds=InstanceIds, DryRun=DryRun)
        print('[ INFO ]: Starting instances -', InstanceIds)
    except Exception as e:
        print('[ WARN ]: Cannot start EC2 instances', InstanceIds, '. Exception', e)
        return

def stopEC2(EC2Client, InstanceIds, DryRun=True):
    try:
        CreateResponse = EC2Client.stop_instances(InstanceIds=InstanceIds, DryRun=DryRun)
        print('[ INFO ]: Stopping instances -', InstanceIds)
    except Exception as e:
        print('[ WARN ]: Cannot stop EC2 instances', InstanceIds, '. Exception', e)
        return

def terminateEC2(EC2Client, InstanceIds, Yes=False, DryRun=True):
    if Yes == False:
        isRemove = yesNoQuery('Are you sure you want to terminate these instances - ' + str(InstanceIds) + '? All data will be lost.')
        if isRemove == False:
            print('[ INFO ]: Not deleting any instances from', InstanceIds)
            return

    try:
        if Yes == False:
            if yesNoQuery('This action will delete all instances - ' + str(InstanceIds) + '. Proceed?') == False:
                print('[ INFO ]: Not deleting any instances from', InstanceIds)
                return

        CreateResponse = EC2Client.terminate_instances(InstanceIds=InstanceIds, DryRun=DryRun)
        print('[ INFO ]: Started terminate on instances -', InstanceIds)
    except Exception as e:
        print('[ WARN ]: Cannot terminate EC2 instances', InstanceIds, '. Exception', e)
        return

# def getEC2InstPublicIP(InstanceID):
#     Command = 'aws ec2 describe-instances --filters Name=instance-id,Values=' + InstanceID
#     Command = Command + """ --query Reservations[*].Instances[*].{InstanceId:InstanceId,PublicDnsName:PublicDnsName,State:State.Name,PublicIpAddress:PublicIpAddress}"""
#     Output = runCommand(Command)
#     # printOutput(Output)
#     JSON = json.loads(Output)
#
#     return JSON[0][0]['PublicIpAddress']

def getAllEC2InfoByToken(EC2Client, Token='PublicIp', onlyRunning=True):
    try:
        Response = EC2Client.describe_instances()
    except Exception as e:
        print('[ WARN ]: Unable to get EC2 status.')
        print('[ ERR ]:', e)
        return

    Output = []
    # RelevantKeys = ['InstanceId', 'InstanceType', 'State', 'NetworkInterfaces']

    for RES in Response['Reservations']:
        for INS in RES['Instances']:
            if onlyRunning and INS['State']['Name'] != 'running':
                continue

            for Key in INS:
                if Token == 'PublicIp' and Key == 'NetworkInterfaces':
                    if len(INS[Key]) > 0:
                        if 'Association' in INS[Key][0]:
                            Output.append(INS[Key][0]['Association']['PublicIp'])
                        else:
                            Output.append('Initializing...')
                    else:
                        Output.append('NA')
                elif Token == 'State' and Key == 'State':
                    Output.append(INS[Key]['Name'])
                elif Key == Token:
                    Output.append(INS[Key])

    return Output

def getEC2InfoByToken(EC2Client, InstanceId, Token='PublicIp'):
    try:
        Response = EC2Client.describe_instances()
    except Exception as e:
        print('[ WARN ]: Unable to get EC2 status.')
        print('[ ERR ]:', e)
        return

    Output = None
    # RelevantKeys = ['InstanceId', 'InstanceType', 'State', 'NetworkInterfaces']

    for RES in Response['Reservations']:
        for INS in RES['Instances']:
            if INS['InstanceId'] != InstanceId:
                continue

            for Key in INS:
                if Token == 'PublicIp' and Key == 'NetworkInterfaces':
                    if len(INS[Key]) > 0:
                        if 'Association' in INS[Key][0]:
                            Output = INS[Key][0]['Association']['PublicIp']
                        else:
                            Output = 'Initializing...'
                    else:
                        Output = 'NA'
                elif Token == 'State' and Key == 'State':
                    Output = INS[Key]['Name']
                elif Key == Token:
                    Output = INS[Key]

    return Output

def waitForEC2(SSMClient, InstanceId, TargetState='running', TimeOut=100):
    InstState = getEC2InfoByToken(SSMClient, InstanceId, Token='State')
    Tic = getCurrentEpochTime()
    while InstState != TargetState:
        time.sleep(0.1)
        InstState = getEC2InfoByToken(SSMClient, InstanceId, Token='State')
        Toc = getCurrentEpochTime()
        if (Toc-Tic)*1e-6 > TimeOut:
            print('[ WARN ]: Target state', TargetState, 'not reached by instance', InstanceId)
            return

def runCommandEC2(KeyPath, Commands, InstancePublicIp, Username='ubuntu', Verbose=0):
    Key = paramiko.RSAKey.from_private_key_file(KeyPath)
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print('[ INFO ]: SSH ', Username + '@'+ InstancePublicIp)
        SSHClient.connect(hostname=InstancePublicIp, username=Username, pkey=Key)

        # Execute a command(cmd) after connecting/ssh to an instance
        for cmd in Commands:
            print('[ INFO ]: Running command:', cmd)
            _, stdout, stderr = SSHClient.exec_command(cmd)
            if Verbose > 0:
                print(stdout.read().decode(), flush=True)
                print(stderr.read().decode(), flush=True)

        SSHClient.close()
    except Exception as e:
        print(e)

def runShellScriptEC2(KeyPath, BashScriptPath, InstancePublicIp, Username='ubuntu'):
    print('[ TODO ]: Not implemented.')
    return
    Key = paramiko.RSAKey.from_private_key_file(KeyPath)
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    with open(BashScriptPath, 'r') as File:
        ScriptContents = File.read() #.replace('\n', '')
    # '/usr/bin/python -c "%s"' % command

    try:
        print('[ INFO ]: SSH ', Username + '@'+ InstancePublicIp)
        SSHClient.connect(hostname=InstancePublicIp, username=Username, pkey=Key)

        # Execute a command(cmd) after connecting/ssh to an instance
        stdin, stdout, stderr = SSHClient.exec_command(ScriptContents)
        print(stdout.read())

        SSHClient.close()
    except Exception as e:
        print(e)
