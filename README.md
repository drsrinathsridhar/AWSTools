# AWSTools
Some scripts and tools for running deep learning jobs on AWS.

## Requirements
- Linux
- Python 3+
- [Boto3][3]
- [AWS Command Line Interface][2]
- AWS account ID and key
- Enough credits to create GPU instances (these are expensive, beware!)

## Getting Started

### Initial Setup
1. Setup your AWS CLI tools by running ``aws configure``. See the [AWS CLI documentation][1] for details.
2. You must setup a shared EFS storage space for **data**---input datasets, output models and weights, and logs (including console outputs).
Run `manangeEFS.py --help` for instructions on how to create an EFS volume for your projects. Note that multiple projects can share a single EFS.

### Initial Project Setup

For each machine learning project, we create an exclusive directory in the shared EFS containing dedicated input/output data.
We also create a fixed number of GPU instances and stop them for later use.
These instances can be started or stopped later depending on the project.
 
All instances and data directories are logged under the project EFS directory.
All instances come with an EBS-backed root and can preserve any local data.

For each project, run the following commands **once** at the beginning.

``python startProject.py --help``

# Contact
Srinath Sridhar  
<http://srinathsridhar.com>  
<ssrinath@cs.stanford.edu>

[1]: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
[2]: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
[3]: https://github.com/boto/boto3