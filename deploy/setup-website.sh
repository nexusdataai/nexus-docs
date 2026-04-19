#!/usr/bin/env bash
# setup-website.sh – One-time setup for starhub-docs on S3 + CloudFront with Basic Auth
#
# Creates: S3 bucket, OAC, CloudFront distribution, Lambda@Edge (auth + URL rewriting),
#          S3 bucket policy. Idempotent – safe to re-run.
#
# Usage:
#   AWS_PROFILE=external-access ./setup-website.sh
#   BASIC_AUTH_USER=admin BASIC_AUTH_PASSWORD=secret AWS_PROFILE=external-access ./setup-website.sh

set -e

BUCKET="${DOCS_S3_BUCKET:-totogi-callsense-doc}"
AWS_PROFILE="${AWS_PROFILE:-default}"
AWS_REGION="${AWS_REGION:-us-east-1}"
LAMBDA_REGION="us-east-1"
LAMBDA_NAME="starhub-docs-basic-auth"
OAC_NAME="starhub-docs-oac"
BASIC_AUTH_USER="${BASIC_AUTH_USER:-admin}"
BASIC_AUTH_PASSWORD="${BASIC_AUTH_PASSWORD:-changeme}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
log() { echo -e "${GREEN}[setup-website]${NC} $*"; }
warn() { echo -e "${YELLOW}[setup-website]${NC} $*"; }
err() { echo -e "${RED}[setup-website]${NC} $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAMBDA_DIR="$SCRIPT_DIR/lambda-basic-auth"

# --- Step 1: S3 bucket ---
step1() {
  log "Step 1: Create S3 bucket ($BUCKET)"
  if aws s3api head-bucket --bucket "$BUCKET" --profile "$AWS_PROFILE" 2>/dev/null; then
    warn "Bucket $BUCKET already exists, skipping create."
  else
    aws s3api create-bucket --bucket "$BUCKET" --region "$AWS_REGION" --profile "$AWS_PROFILE"
  fi
  aws s3api put-public-access-block --bucket "$BUCKET" --profile "$AWS_PROFILE" \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
  log "Step 1 done."
}

# --- Step 2: Origin Access Control ---
# Returns OAC ID on stdout; all log messages go to stderr.
step2() {
  log "Step 2: Create Origin Access Control (OAC)" >&2
  local oac_id
  oac_id=$(aws cloudfront list-origin-access-controls --profile "$AWS_PROFILE" \
    --query "OriginAccessControlList.Items[?Name=='$OAC_NAME'].Id | [0]" --output text 2>/dev/null)
  if [ -z "$oac_id" ] || [ "$oac_id" = "null" ] || [ "$oac_id" = "None" ]; then
    oac_id=$(aws cloudfront create-origin-access-control --profile "$AWS_PROFILE" \
      --origin-access-control-config '{
        "Name": "'"$OAC_NAME"'",
        "SigningProtocol": "sigv4",
        "SigningBehavior": "always",
        "OriginAccessControlOriginType": "s3"
      }' --query 'OriginAccessControl.Id' --output text)
    log "Created OAC: $oac_id" >&2
  else
    log "OAC already exists: $oac_id" >&2
  fi
  if [ -z "$oac_id" ] || [ "$oac_id" = "null" ] || [ "$oac_id" = "None" ]; then
    err "Could not create or find OAC."
  fi
  echo "$oac_id"
}

# --- Step 3: CloudFront distribution ---
# No CustomErrorResponses – Lambda@Edge handles directory index rewriting.
step3() {
  local oac_id="$1"
  log "Step 3: Create CloudFront distribution"

  local origin_domain="${BUCKET}.s3.${AWS_REGION}.amazonaws.com"

  # Reuse existing distribution for this origin
  local existing_id
  existing_id=$(aws cloudfront list-distributions --profile "$AWS_PROFILE" \
    --query "DistributionList.Items[?Origins.Items[0].DomainName=='$origin_domain' && Enabled==\`true\`].Id | [0]" --output text 2>/dev/null)
  if [ -n "$existing_id" ] && [ "$existing_id" != "None" ] && [ "$existing_id" != "null" ]; then
    DIST_ID="$existing_id"
    DOMAIN=$(aws cloudfront get-distribution --id "$DIST_ID" --profile "$AWS_PROFILE" --query 'Distribution.DomainName' --output text)
    DIST_ARN="arn:aws:cloudfront::$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text):distribution/$DIST_ID"
    warn "Distribution $DIST_ID already exists ($DOMAIN), skipping create."
    log "Step 3 done."
    return
  fi

  local caller_ref="starhub-docs-$(date +%s)"
  local dist_config
  dist_config=$(cat <<DISTJSON
{
  "CallerReference": "$caller_ref",
  "Comment": "StarHub Docs",
  "DefaultRootObject": "index.html",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "S3Origin",
      "DomainName": "$origin_domain",
      "OriginAccessControlId": "$oac_id",
      "S3OriginConfig": { "OriginAccessIdentity": "" }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": { "Quantity": 2, "Items": ["GET", "HEAD"], "CachedMethods": { "Quantity": 2, "Items": ["GET", "HEAD"] } },
    "Compress": true,
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6"
  }
}
DISTJSON
  )

  local dist_out
  dist_out=$(aws cloudfront create-distribution --profile "$AWS_PROFILE" \
    --distribution-config "$dist_config" 2>&1) || err "Create distribution failed: $dist_out"
  DIST_ID=$(echo "$dist_out" | jq -r '.Distribution.Id')
  DIST_ARN=$(echo "$dist_out" | jq -r '.Distribution.ARN')
  if [ "$DIST_ARN" = "null" ] || [ -z "$DIST_ARN" ]; then
    DIST_ARN="arn:aws:cloudfront::$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text):distribution/$DIST_ID"
  fi
  DOMAIN=$(echo "$dist_out" | jq -r '.Distribution.DomainName')
  log "Distribution ID: $DIST_ID  Domain: $DOMAIN"
  log "Step 3 done."
}

# --- Step 4: S3 bucket policy ---
step4() {
  local dist_arn="$1"
  log "Step 4: Attach S3 bucket policy (CloudFront only)"
  local bucket_arn="arn:aws:s3:::${BUCKET}"
  local policy='{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": { "Service": "cloudfront.amazonaws.com" },
      "Action": "s3:GetObject",
      "Resource": "'"$bucket_arn"'/*",
      "Condition": { "StringEquals": { "AWS:SourceArn": "'"$dist_arn"'" } }
    }]
  }'
  aws s3api put-bucket-policy --bucket "$BUCKET" --profile "$AWS_PROFILE" --policy "$policy"
  log "Step 4 done."
}

# --- Step 5: Lambda@Edge ---
# Lambda@Edge does NOT support env vars. Auth credentials are baked into index.js.
# The Lambda also rewrites directory URLs (e.g. /business/ → /business/index.html).
step5() {
  log "Step 5: Lambda@Edge (auth + URL rewriting)"
  local account_id
  account_id=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)

  # --- 5a: IAM role (Lambda@Edge needs both lambda + edgelambda principals) ---
  local role_arn
  role_arn=$(aws iam get-role --role-name "lambda_basic_execution" --profile "$AWS_PROFILE" \
    --query 'Role.Arn' --output text 2>/dev/null) || true
  if [ -z "$role_arn" ] || [ "$role_arn" = "None" ]; then
    warn "Creating Lambda execution role..."
    aws iam create-role --role-name "lambda_basic_execution" --profile "$AWS_PROFILE" \
      --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
          "Effect": "Allow",
          "Principal": { "Service": ["lambda.amazonaws.com", "edgelambda.amazonaws.com"] },
          "Action": "sts:AssumeRole"
        }]
      }' >/dev/null 2>&1 || true
    aws iam attach-role-policy --role-name "lambda_basic_execution" --profile "$AWS_PROFILE" \
      --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" 2>/dev/null || true
    warn "Waiting for IAM role propagation (15s)..."
    sleep 15
    role_arn=$(aws iam get-role --role-name "lambda_basic_execution" --profile "$AWS_PROFILE" \
      --query 'Role.Arn' --output text)
  fi

  # --- 5b: Bake credentials into Lambda source ---
  local src_file="$LAMBDA_DIR/index.js"
  local tmp_src="/tmp/lambda-edge-src.js"
  sed "s|const user = '.*';|const user = '$BASIC_AUTH_USER';|; s|const pass = '.*';|const pass = '$BASIC_AUTH_PASSWORD';|" \
    "$src_file" > "$tmp_src"

  local zip_path="/tmp/lambda-basic-auth.zip"
  (cd /tmp && zip -q -j "$zip_path" "$tmp_src" && cd - >/dev/null)
  # zip stores as lambda-edge-src.js; Lambda needs index.js
  (cd /tmp && mkdir -p _lambda_pkg && cp "$tmp_src" _lambda_pkg/index.js && cd _lambda_pkg && zip -q -r "$zip_path" . && cd .. && rm -rf _lambda_pkg)
  rm -f "$tmp_src"

  # --- 5c: Create or update Lambda ---
  local func_arn

  if aws lambda get-function --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" >/dev/null 2>&1; then
    log "Updating existing Lambda $LAMBDA_NAME..."
    aws lambda wait function-updated-v2 --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" 2>/dev/null \
      || aws lambda wait function-updated --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" 2>/dev/null \
      || sleep 10
    aws lambda update-function-code --function-name "$LAMBDA_NAME" \
      --zip-file "fileb://$zip_path" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" >/dev/null
    aws lambda wait function-updated-v2 --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" 2>/dev/null \
      || aws lambda wait function-updated --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" 2>/dev/null \
      || sleep 10
    func_arn=$(aws lambda get-function --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" \
      --region "$LAMBDA_REGION" --query 'Configuration.FunctionArn' --output text)
  else
    log "Creating Lambda $LAMBDA_NAME..."
    func_arn=$(aws lambda create-function --function-name "$LAMBDA_NAME" --runtime nodejs18.x \
      --role "$role_arn" --handler index.handler --zip-file "fileb://$zip_path" \
      --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" --query 'FunctionArn' --output text)
  fi
  rm -f "$zip_path"

  # --- 5d: Wait for active, then publish ---
  log "Waiting for Lambda to become Active..."
  aws lambda wait function-active-v2 --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" 2>/dev/null \
    || aws lambda wait function-active --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" --region "$LAMBDA_REGION" 2>/dev/null \
    || sleep 10

  log "Publishing Lambda version..."
  local version_arn
  version_arn=$(aws lambda publish-version --function-name "$LAMBDA_NAME" --profile "$AWS_PROFILE" \
    --region "$LAMBDA_REGION" --query 'FunctionArn' --output text)

  # --- 5e: Attach to CloudFront ---
  log "Attaching Lambda@Edge to CloudFront..."
  local config_file="/tmp/cf-config-$$.json"
  local full_cfg etag
  full_cfg=$(aws cloudfront get-distribution-config --id "$DIST_ID" --profile "$AWS_PROFILE")
  etag=$(echo "$full_cfg" | jq -r '.ETag')
  echo "$full_cfg" | jq --arg arn "$version_arn" '
    .DistributionConfig
    | .DefaultCacheBehavior.LambdaFunctionAssociations = {
        "Quantity": 1,
        "Items": [{"EventType": "viewer-request", "LambdaFunctionARN": $arn}]
      }
    | .CustomErrorResponses = {"Quantity": 0}
  ' > "$config_file"
  aws cloudfront update-distribution --id "$DIST_ID" --distribution-config "file://$config_file" \
    --if-match "$etag" --profile "$AWS_PROFILE" >/dev/null
  rm -f "$config_file"
  log "Step 5 done. Auth: user=$BASIC_AUTH_USER"
}

# --- Step 6 & 7: Instructions ---
step6_7() {
  echo
  echo -e "${BLUE}=== Setup Complete ===${NC}"
  echo
  echo "DOCS_S3_BUCKET=$BUCKET"
  echo "DOCS_CLOUDFRONT_ID=$DIST_ID"
  echo "Docs URL: https://$DOMAIN"
  echo "Auth: user=$BASIC_AUTH_USER"
  echo
  echo -e "${YELLOW}GitHub Actions secrets needed:${NC}"
  echo "  DOCS_S3_BUCKET      = $BUCKET"
  echo "  DOCS_CLOUDFRONT_ID  = $DIST_ID"
  echo
  echo -e "${YELLOW}Next steps:${NC}"
  echo "  1. Set the above secrets in GitHub repo settings"
  echo "  2. Push to main to trigger the docs.yml workflow"
  echo "  3. Disable GitHub Pages if previously enabled"
}

# --- Main ---
main() {
  if ! aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1; then
    err "AWS profile '$AWS_PROFILE' not valid. Set AWS_PROFILE or run aws configure."
  fi
  if ! command -v jq &>/dev/null; then
    err "jq is required. Install with: apt-get install jq / brew install jq"
  fi

  step1
  OAC_ID=$(step2)
  step3 "$OAC_ID"
  step4 "$DIST_ARN"
  step5
  step6_7
}

main "$@"
