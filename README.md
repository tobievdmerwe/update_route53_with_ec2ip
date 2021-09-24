# Update Route53 rule with public IP of EC2

When EC2 machines restart the possibility exist that the public IP can also change for the EC2.
This makes it difficult to connect for example via RDP if the IP do not stay the same.

This Cloud Formation stack deploys a Lambda that gets triggered when an EC2 goes into a running state via a Cloud Watch event.
The Lambda will check if the EC2 is tagged and if it is then it will upsert a the Route53 hosted zone with an A record with the DNS name and the IP address of the EC2.
This allows the EC2 to be accessible by the DNS name.

## Requirements
1.  The AWS CLI is required to deploy the Lambda function using the deployment instructions.
2.  The AWS CLI should be configured with valid credentials to create the CloudFormation stack, lambda function, and related resources.  You must also have rights to upload new objects to the S3 bucket you specify in the deployment steps.  
3.  A valid wild card domain hosted in Route 53 ie. *.mydomain.com
   
## Setup
Tag EC2 machines with the AutoUpdateIP tag and assign a DNS name as a value ie. machine1.mydomain.com to the tag.
    
## Deploy 

1. Clone the update_route53_with_ec2ip github repository to your computer using the following command:

       git clone https://github.com/tobievdmerwe/update_route53_with_ec2ip
       
2. Configure the AWS CLI with credentials for your AWS account.  This walkthrough uses temporary credentials provided by AWS Single Sign On using the **Command line or programmatic access** option.  This sets the **AWS_ACCESS_KEY_ID**, **AWS_SECRET_ACCESS_KEY**, and **AWS_SESSION_TOKEN** AWS environment variables with the appropriate credentials for use with the AWS CLI.

3. Package the deployment

       aws cloudformation package \
        --template-file EC2Route53IPUpdate.yaml \
        --s3-bucket <bucket name> \      
        --s3-prefix AutoUpdateIP \
        --output-template-file EC2Route53IPUpdate-packaged.yaml 

4. Deploy the stack

       aws cloudformation deploy \
        --template-file EC2Route53IPUpdate-packaged.yaml \
        --stack-name AutoIPUPdate 
        --region <region where the EC2s are deployed ie eu-west-1> 
        --capabilities CAPABILITY_IAM 
        --parameter-overrides ParameterKey=Route53HostedZone,ParameterValue=<Route53 hosted zone id>