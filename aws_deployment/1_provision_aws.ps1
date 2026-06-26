$ErrorActionPreference = "Stop"

$REGION = "ap-south-1"
$SG_NAME = "exposys-production-sg"
$KEY_NAME = "exposys-aws-key"
$KEY_FILE = ".\$KEY_NAME.pem"

Write-Host "Creating Security Group: $SG_NAME..."
$VPC_ID = (aws ec2 describe-vpcs --region $REGION --query 'Vpcs[?isDefault==`true`].VpcId' --output text)
if (-not $VPC_ID -or $VPC_ID -eq "None") { 
    Write-Host "No default VPC found. Using the first available VPC..."
    $VPC_ID = (aws ec2 describe-vpcs --region $REGION --query 'Vpcs[0].VpcId' --output text)
}
if (-not $VPC_ID -or $VPC_ID -eq "None") { throw "No VPCs found in region $REGION!" }

$SG_ID = (aws ec2 describe-security-groups --region $REGION --filters "Name=group-name,Values=$SG_NAME" --query 'SecurityGroups[0].GroupId' --output text)
if (-not $SG_ID -or $SG_ID -eq "None") {
    $SG_ID = (aws ec2 create-security-group --group-name $SG_NAME --description "Exposys Web Server Security Group" --vpc-id $VPC_ID --region $REGION --query 'GroupId' --output text)
    Write-Host "Configuring Security Group Rules..."
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $REGION | Out-Null
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION | Out-Null
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $REGION | Out-Null
} else {
    Write-Host "Security Group already exists: $SG_ID"
}

Write-Host "Creating Key Pair: $KEY_NAME..."
aws ec2 delete-key-pair --key-name $KEY_NAME --region $REGION | Out-Null
if (Test-Path $KEY_FILE) { Remove-Item $KEY_FILE }
aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text --region $REGION > $KEY_FILE
if (Test-Path $KEY_FILE) {
    icacls.exe $KEY_FILE /reset | Out-Null
    icacls.exe $KEY_FILE /grant:r "$($env:USERNAME):(R)" | Out-Null
    icacls.exe $KEY_FILE /inheritance:r | Out-Null
}

Write-Host "Finding Latest Ubuntu 22.04 AMI in $REGION..."
$AMI_ID = (aws ec2 describe-images --region $REGION --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" "Name=state,Values=available" --query "sort_by(Images, &CreationDate)[-1].ImageId" --output text)

Write-Host "Launching EC2 Instance..."
$BDM_JSON = '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp3"}}]'
$BDM_JSON | Out-File ".\bdm.json" -Encoding ascii

$INSTANCE_ID = (aws ec2 run-instances `
    --region $REGION `
    --image-id $AMI_ID `
    --count 1 `
    --instance-type t3.micro `
    --key-name $KEY_NAME `
    --security-group-ids $SG_ID `
    --block-device-mappings file://bdm.json `
    --query 'Instances[0].InstanceId' `
    --output text)

Remove-Item ".\bdm.json"

if (-not $INSTANCE_ID -or $INSTANCE_ID -eq "None") { throw "Failed to launch instance." }

Write-Host "Waiting for instance $INSTANCE_ID to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

$PUBLIC_IP = (aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $REGION --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

Write-Host "`n================================================="
Write-Host "SUCCESS! EC2 Instance Launched."
Write-Host "Instance ID: $INSTANCE_ID"
Write-Host "Public IP:   $PUBLIC_IP"
Write-Host "SSH Key:     $KEY_FILE"
Write-Host "================================================="

$DEPLOY_SCRIPT = @"
Write-Host 'Zipping files... (excluding venv, .git, etc)'
if (Test-Path exposys.zip) { Remove-Item exposys.zip }
tar.exe -a -c -f exposys.zip --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=node_modules *

Write-Host 'Uploading files to EC2...'
scp -i $KEY_FILE -o StrictHostKeyChecking=no exposys.zip ubuntu@${PUBLIC_IP}:/home/ubuntu/

Write-Host 'Extracting and setting up on EC2...'
ssh -i $KEY_FILE -o StrictHostKeyChecking=no ubuntu@${PUBLIC_IP} `"
    sudo mkdir -p /var/www/exposys
    sudo chown -R ubuntu:ubuntu /var/www/exposys
    sudo apt-get update && sudo apt-get install -y unzip
    unzip -o /home/ubuntu/exposys.zip -d /var/www/exposys/
    sudo chmod +x /var/www/exposys/aws_deployment/2_server_setup.sh
    cd /var/www/exposys/
    ./aws_deployment/2_server_setup.sh
`"

Write-Host "`nDone! Your site is live at: http://${PUBLIC_IP}"
"@

$DEPLOY_SCRIPT | Out-File ".\deploy.ps1" -Encoding utf8
Write-Host "`n-> I have generated a deployment script: .\deploy.ps1"
Write-Host "-> To push your code to the server and start it, run: .\deploy.ps1"
