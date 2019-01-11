import subprocess, json

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
