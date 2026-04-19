# Operational Documentation

This section contains deployment guides, AWS configuration, troubleshooting procedures, and operational documentation for running the Starhub Trilogy platform.

## Overview

The operational documentation provides:

- **Deployment Guides** - Step-by-step deployment instructions
- **Configuration** - AWS and application configuration
- **Operations** - Day-to-day operational procedures
- **Troubleshooting** - Common issues and solutions
- **FAQ** - Frequently asked questions

## Available Documents

### User Guide Overview
Comprehensive overview of the platform from an operational perspective.

📄 [View User Guide Overview](user-guide/README.md)

---

### Getting Started
Quick start guide to get the platform up and running.

📄 [View Getting Started Guide](user-guide/01-getting-started.md)

---

### Installation
Detailed installation instructions for all components.

📄 [View Installation Guide](user-guide/02-installation.md)

---

### Deployment Wizard
Guide to using the deployment wizard for AWS deployment.

📄 [View Deployment Wizard Guide](user-guide/03-deployment-wizard.md)

---

### AWS Configuration
AWS-specific configuration including IAM, VPC, and service setup.

📄 [View AWS Configuration Guide](user-guide/04-aws-configuration.md)

---

### Managing Deployments
Guide to managing, monitoring, and maintaining deployments.

📄 [View Deployment Management Guide](user-guide/05-managing-deployments.md)

---

### Troubleshooting
Common issues, error messages, and troubleshooting procedures.

📄 [View Troubleshooting Guide](user-guide/06-troubleshooting.md)

---

### FAQ
Frequently asked questions about deployment, configuration, and operations.

📄 [View FAQ](user-guide/07-faq.md)

---

### Build Guide
Guide to building and packaging the platform components.

📄 [View Build Guide](user-guide/BUILD_GUIDE.md)

---

### Quick Reference
Quick reference card for common operations and commands.

📄 [View Quick Reference](user-guide/QUICK_REFERENCE.md)

---

## Kubernetes Operator

### Kubernetes Operator Overview
Deploy and manage Totogi capabilities on EKS clusters using Kubernetes Operator pattern.

📄 [View Kubernetes Operator Documentation](kubernetes-operator/index.md)

---

### Quick Start
Get the operator running in minutes.

📄 [View Quick Start Guide](kubernetes-operator/quick-start.md)

---

### Custom Resource Reference
Complete reference for TotogiCapability CRD.

📄 [View CRD Reference](kubernetes-operator/custom-resource.md)

---

## Deployment Options

### Option 1: AWS ECS Deployment (Production)

Fully managed ECS Fargate deployment:

1. **Prerequisites**
   - AWS account with admin access
   - AWS CLI configured
   - Terraform installed

2. **Deployment Steps**
   - Configure AWS credentials
   - Set environment variables
   - Run deployment wizard
   - Verify deployment

3. **Configuration**
   - SSM Parameter Store
   - Secrets Manager
   - IAM roles and policies
   - VPC and networking

### Option 2: LocalStack Deployment (Development)

Local development environment:

1. **Prerequisites**
   - Docker installed
   - Python 3.11+
   - LocalStack running

2. **Setup Steps**
   - Start LocalStack
   - Configure environment
   - Initialize resources
   - Start gateway

3. **Benefits**
   - No AWS costs
   - Rapid iteration
   - Isolated testing
   - Full feature parity

## Operational Procedures

### Daily Operations

#### Monitoring
- Check CloudWatch dashboards
- Review error logs
- Monitor call processing metrics
- Track API usage

#### Maintenance
- Review journey execution status
- Clean up old data
- Update license keys
- Backup critical data

### Weekly Operations

#### Health Checks
- Verify all services running
- Check resource utilization
- Review cost optimization
- Update documentation

#### Performance Tuning
- Analyze slow queries
- Optimize DynamoDB indexes
- Review S3 lifecycle policies
- Tune ECS task sizing

### Monthly Operations

#### Updates
- Apply security patches
- Update dependencies
- Review and apply AWS updates
- Update documentation

#### Reporting
- Generate usage reports
- Create cost analysis reports
- Review SLA compliance
- Stakeholder updates

## Monitoring & Alerts

### CloudWatch Metrics
- ECS service health
- API response times
- DynamoDB throttling
- S3 operations
- Lambda execution

### CloudWatch Alarms
- Service down alerts
- High error rate alerts
- Resource utilization alerts
- Cost threshold alerts

### Logging
- Application logs to CloudWatch Logs
- Journey execution logs to S3
- API access logs
- Error and exception tracking

## Backup & Recovery

### Data Backup
- DynamoDB point-in-time recovery
- S3 versioning enabled
- Cross-region replication (optional)
- Regular backup verification

### Disaster Recovery
- Multi-AZ deployment
- Automated failover
- Recovery time objective (RTO): < 1 hour
- Recovery point objective (RPO): < 15 minutes

## Security Operations

### Access Management
- Regular IAM policy review
- Rotate API keys and secrets
- Review CloudTrail logs
- Audit user access

### Compliance
- Regular security audits
- Vulnerability scanning
- Patch management
- Documentation updates

## Cost Management

### Cost Optimization
- Right-size ECS tasks
- Optimize DynamoDB capacity
- Use S3 lifecycle policies
- Review unused resources

### Cost Monitoring
- CloudWatch cost alerts
- Monthly cost reports
- Resource tagging
- Budget tracking

## Common Commands

```bash
# Health check
curl http://localhost:8000/health

# Start gateway
./gateway.sh start

# View logs
./gateway.sh logs

# Run tests
./gateway.sh test

# Deploy to AWS
terraform apply

# Check ECS service
aws ecs describe-services --cluster call-processing-prod --services gateway-service
```

---

[← Back to Home](../index.md) | [← Previous: Technical Documentation](../technical/index.md) | [Next: Developer Guide →](../developer/index.md)
