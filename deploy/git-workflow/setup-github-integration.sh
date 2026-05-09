#!/bin/bash

# NexusAI Docs GitHub Actions Integration Setup Script
# Creates IAM role for deploying docs to S3 (totogi-callsense-doc) + CloudFront

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_color() { echo -e "${1}${2}${NC}"; }
print_header() { echo; print_color "$BLUE" "=== $1 ==="; echo; }

print_header "NexusAI Docs GitHub Actions Integration Setup"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

if [ ! -f "$PROJECT_ROOT/mkdocs.yml" ]; then
    print_color "$RED" "Error: Please run this script from the nexus-docs project (must contain mkdocs.yml)"
    exit 1
fi

cd "$SCRIPT_DIR"

AWS_PROFILE="${AWS_PROFILE:-default}"
AWS_REGION="${AWS_REGION:-us-east-1}"
DOCS_S3_BUCKET="${DOCS_S3_BUCKET:-totogi-callsense-doc}"

print_color "$YELLOW" "Using AWS Profile: $AWS_PROFILE"
print_color "$YELLOW" "Using AWS Region: $AWS_REGION"
print_color "$YELLOW" "Docs S3 bucket: $DOCS_S3_BUCKET"

if ! aws sts get-caller-identity --profile "$AWS_PROFILE" > /dev/null 2>&1; then
    print_color "$RED" "AWS credentials not valid. Configure profile or run aws configure."
    exit 1
fi
print_color "$GREEN" "✓ AWS credentials verified"

OIDC_PROVIDER_ARN=$(aws iam list-open-id-connect-providers --profile "$AWS_PROFILE" --query "OpenIDConnectProviderList[?contains(Arn, 'token.actions.githubusercontent.com')].Arn" --output text 2>/dev/null || true)
if [ -z "$OIDC_PROVIDER_ARN" ]; then
    print_color "$RED" "GitHub OIDC provider not found. Create it in IAM → Identity providers first."
    exit 1
fi
print_color "$GREEN" "✓ Found GitHub OIDC provider"

read -p "GitHub organization [trilogy-group]: " GITHUB_ORG
GITHUB_ORG=${GITHUB_ORG:-trilogy-group}
read -p "Repository name [nexus-docs]: " GITHUB_REPO
GITHUB_REPO=${GITHUB_REPO:-nexus-docs}

print_header "Deploy IAM Role for Docs"

STACK_NAME="github-actions-role-nexus-docs"
aws cloudformation deploy \
    --template-file ./github-role-only.yml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        GitHubOrganization="$GITHUB_ORG" \
        GitHubRepository="$GITHUB_REPO" \
        BranchName=main \
        DocsS3Bucket="$DOCS_S3_BUCKET" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" \
    --no-fail-on-empty-changeset

ROLE_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='GitHubActionsRoleArn'].OutputValue" --output text --region "$AWS_REGION" --profile "$AWS_PROFILE")
print_color "$GREEN" "✓ Role ARN: $ROLE_ARN"

print_header "GitHub Secrets Configuration"

print_color "$YELLOW" "Add these secrets at: https://github.com/$GITHUB_ORG/$GITHUB_REPO/settings/secrets/actions"
echo
echo "| Secret Name         | Value |"
echo "|---------------------|-------|"
echo "| AWS_ROLE_TO_ASSUME  | $ROLE_ARN |"
echo "| DOCS_S3_BUCKET     | $DOCS_S3_BUCKET |"
echo "| DOCS_CLOUDFRONT_ID | (distribution ID from deploy/setup-website.sh or AWS Console) |"
echo

cat > ./role-arns-secrets.md << EOF
# NexusAI Docs GitHub Actions

| Secret Name         | Value |
|---------------------|-------|
| AWS_ROLE_TO_ASSUME  | $ROLE_ARN |
| DOCS_S3_BUCKET     | $DOCS_S3_BUCKET |
| DOCS_CLOUDFRONT_ID | Set after running deploy/setup-website.sh |

Docs deploy on push to \`main\`; build runs \`mkdocs build\`, syncs \`site/\` to S3, invalidates CloudFront.
EOF

print_color "$GREEN" "✓ Saved to ./role-arns-secrets.md"
print_color "$GREEN" "NexusAI Docs GitHub Actions setup complete."
