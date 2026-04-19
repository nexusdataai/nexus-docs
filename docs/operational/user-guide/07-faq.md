# Frequently Asked Questions

## General Questions

### What is the Totogi Capability Installer?

The Totogi Capability Installer is a desktop application that enables you to deploy Totogi's telco business capabilities directly into your own AWS environment. It provides a guided wizard experience for deploying, updating, and managing capabilities.

### What capabilities can I deploy?

Currently available capabilities include:
- **Call Processing** - Voice call processing with AI routing
- **Billing Engine** - Real-time billing and charging
- **Customer Portal** - Self-service customer management

More capabilities are added regularly. Check the installer for the latest list.

### Which cloud providers are supported?

Currently, **AWS** is fully supported. Support for Azure, GCP, Kubernetes, and on-premise deployments is coming soon.

### Do I need an AWS account?

Yes, you need an AWS account with appropriate IAM permissions to deploy capabilities. The capabilities are deployed into your own AWS account, giving you full control over your infrastructure.

---

## Installation Questions

### What are the system requirements?

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: 4GB RAM minimum
- **Disk Space**: 500MB for application
- **Network**: Internet connection for AWS API access

### Is the installer safe to run?

Yes, the installer is digitally signed and verified. If you see security warnings, they are standard for new applications. You can safely proceed with installation.

### Can I run the portable version?

Yes, on Windows you can use the portable version which doesn't require installation. Simply download and run the executable.

### How do I update the installer?

The application checks for updates automatically. When an update is available, you'll be prompted to download and install it.

---

## AWS & Security Questions

### What AWS permissions are required?

The deployment requires permissions for:
- CloudFormation (stack management)
- IAM (role creation)
- VPC (networking)
- ECS (container services)
- S3 (storage)
- CloudFront (CDN)
- Route53 (DNS)
- ACM (certificates)
- And more...

See the [AWS Configuration Guide](./04-aws-configuration.md) for the complete IAM policy.

### Are my AWS credentials stored?

No, your credentials are used only for the current session and are not stored on disk. For ADFS authentication, session tokens are used which expire automatically.

### Can I deploy to a different AWS account?

Yes, using IAM Role ARN authentication, you can deploy to any AWS account where you have a role with appropriate permissions. This is the recommended approach for cross-account deployments.

### Is the deployment secure?

Yes, the deployment follows AWS security best practices:
- All data encrypted at rest and in transit
- Private subnets for backend services
- WAF protection for web applications
- IAM roles with least privilege
- Secrets stored in AWS Secrets Manager

---

## Deployment Questions

### How long does deployment take?

A typical deployment takes 15-30 minutes, depending on:
- Capability complexity
- AWS region
- Network conditions
- Whether it's a new deployment or update

### Can I deploy to multiple environments?

Yes, you can deploy the same capability to multiple environments (dev, staging, prod). Each environment is completely isolated with its own resources.

### What happens if deployment fails?

If deployment fails:
1. The installer shows the error message
2. You can view detailed logs
3. CloudFormation automatically rolls back partial changes
4. You can retry or use Clean Deploy strategy

### Can I cancel a deployment in progress?

Yes, click the "Cancel Deployment" button. CloudFormation will roll back any changes made so far.

### What is Clean Deploy vs Update?

- **Update**: Modifies existing resources in place, preserving data
- **Clean Deploy**: Deletes everything and creates fresh resources (data loss!)

Use Update for normal updates. Use Clean Deploy only when stacks are in a failed state.

---

## Cost Questions

### How much does deployment cost?

Costs vary by environment and usage. Typical monthly costs:

| Environment | Estimated Cost |
|-------------|----------------|
| Development | $40-100/month |
| Staging | $100-200/month |
| Production | $300-1000+/month |

### What AWS services incur costs?

Main cost drivers:
- ECS Fargate (compute)
- NAT Gateway (networking)
- CloudFront (CDN)
- ALB (load balancing)
- S3 (storage)
- DynamoDB (database)

### How can I reduce costs?

For development environments:
- Use FARGATE_SPOT for ECS
- Disable NAT Gateway
- Set auto-scaling minimum to 0
- Use on-demand DynamoDB billing

### Are there any Totogi licensing costs?

Contact your Totogi representative for licensing information. The installer itself is provided as part of your Totogi subscription.

---

## Management Questions

### How do I update a deployed capability?

1. Open the installer
2. Go to Capability Selection
3. Find your capability in "Installed" section
4. Click "Update"
5. Follow the wizard

### How do I delete a deployment?

1. Open the installer
2. Go to Capability Selection
3. Find your capability in "Installed" section
4. Click "Delete"
5. Confirm deletion
6. Follow the wizard

**Warning**: Deletion removes all resources and data!

### Can I access the deployed resources directly?

Yes, all resources are created in your AWS account. You can:
- View in AWS Console
- Access via AWS CLI
- Manage with Infrastructure as Code

### How do I monitor my deployment?

Use AWS CloudWatch for:
- Metrics and dashboards
- Log analysis
- Alarms and notifications

The installer also shows deployment status and health checks.

---

## Troubleshooting Questions

### Why can't I connect to AWS?

Common causes:
1. **Network issues** - Check internet connection
2. **Firewall** - Allow outbound HTTPS to AWS
3. **Proxy** - Configure proxy settings
4. **Credentials** - Verify credentials are correct

### Why is my deployment failing?

Check:
1. **IAM permissions** - Ensure all required permissions
2. **Service limits** - Check AWS quotas
3. **Resource conflicts** - Existing resources with same names
4. **Network** - VPC and subnet availability

### Why can't I access my application after deployment?

Common causes:
1. **DNS propagation** - Wait up to 48 hours
2. **Certificate validation** - Check ACM status
3. **Security groups** - Verify port access
4. **Health checks** - Check ECS task health

### Where can I find logs?

- **Installer logs**: Download from deployment screen
- **CloudFormation**: AWS Console → CloudFormation → Events
- **Application**: CloudWatch → Log groups

---

## Support Questions

### How do I get help?

1. Check this documentation
2. Review [Troubleshooting Guide](./06-troubleshooting.md)
3. Contact support at support@totogi.com

### What information should I provide to support?

- Deployment ID
- Error messages
- Deployment logs
- Screenshots
- AWS region and account (if comfortable sharing)

### Is there a community forum?

Contact your Totogi representative for information about community resources and forums.

---

## Feature Requests

### How do I request new features?

Contact your Totogi representative or email feedback@totogi.com with:
- Feature description
- Use case
- Priority level

### When will Azure/GCP support be available?

Multi-cloud support is on our roadmap. Contact your Totogi representative for timeline information.

### Can I customize the deployment?

The installer uses standard CloudFormation templates. For custom requirements, contact your Totogi representative to discuss options.
