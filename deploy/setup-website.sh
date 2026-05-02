#!/usr/bin/env bash
# setup-website.sh - One-time NexusAI documentation site setup.
#
# Provisions a public, unauthenticated docs site on S3 + CloudFront:
#   - Private S3 bucket (no public access; CloudFront-only via OAC)
#   - CloudFront distribution with OAC origin access
#   - CloudFront Function (viewer-request) that rewrites directory URLs
#     to /index.html so MkDocs use_directory_urls=true works
#   - Bucket policy restricting GetObject to this CloudFront distribution
#
# Configuration is read from ./.env.local (see .env.local.example).
# After setup, DOCS_CLOUDFRONT_ID and DOCS_CLOUDFRONT_DOMAIN are written
# back into .env.local for use by update-website.sh.
#
# Idempotent - safe to re-run.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.local"
CF_FUNCTION_FILE="$SCRIPT_DIR/cloudfront-function/url-rewrite.js"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
log()  { echo -e "${GREEN}[setup-website]${NC} $*"; }
warn() { echo -e "${YELLOW}[setup-website]${NC} $*"; }
err()  { echo -e "${RED}[setup-website]${NC} $*"; exit 1; }

# --- Load .env.local ---
if [ ! -f "$ENV_FILE" ]; then
  err "$ENV_FILE not found. Copy .env.local.example to .env.local and fill in DOCS_S3_BUCKET / AWS_PROFILE / AWS_REGION."
fi
# shellcheck disable=SC1090
set -a; source "$ENV_FILE"; set +a

[ -n "${DOCS_S3_BUCKET:-}" ] || err "DOCS_S3_BUCKET is not set in $ENV_FILE"
AWS_PROFILE="${AWS_PROFILE:-default}"
AWS_REGION="${AWS_REGION:-us-east-1}"
BUCKET="$DOCS_S3_BUCKET"
OAC_NAME="nexusai-docs-oac"
CF_FUNCTION_NAME="nexusai-docs-url-rewrite"

# --- env writeback helper ---
upsert_env() {
  local key="$1" value="$2"
  if grep -qE "^${key}=" "$ENV_FILE"; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|" "$ENV_FILE" && rm -f "${ENV_FILE}.bak"
  elif grep -qE "^# ${key}=" "$ENV_FILE"; then
    sed -i.bak "s|^# ${key}=.*|${key}=${value}|" "$ENV_FILE" && rm -f "${ENV_FILE}.bak"
  else
    printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
  fi
}

# --- Step 1: S3 bucket (private; CloudFront-only) ---
step1() {
  log "Step 1: Create S3 bucket ($BUCKET)"
  if aws s3api head-bucket --bucket "$BUCKET" --profile "$AWS_PROFILE" 2>/dev/null; then
    warn "Bucket $BUCKET already exists, skipping create."
  else
    if [ "$AWS_REGION" = "us-east-1" ]; then
      aws s3api create-bucket --bucket "$BUCKET" --region "$AWS_REGION" --profile "$AWS_PROFILE"
    else
      aws s3api create-bucket --bucket "$BUCKET" --region "$AWS_REGION" --profile "$AWS_PROFILE" \
        --create-bucket-configuration "LocationConstraint=$AWS_REGION"
    fi
  fi
  aws s3api put-public-access-block --bucket "$BUCKET" --profile "$AWS_PROFILE" \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
  log "Step 1 done."
}

# --- Step 2: Origin Access Control ---
step2() {
  log "Step 2: Create Origin Access Control (OAC)" >&2
  local oac_id
  oac_id=$(aws cloudfront list-origin-access-controls --profile "$AWS_PROFILE" \
    --query "OriginAccessControlList.Items[?Name=='$OAC_NAME'].Id | [0]" --output text 2>/dev/null)
  if [ -z "$oac_id" ] || [ "$oac_id" = "None" ] || [ "$oac_id" = "null" ]; then
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
  [ -n "$oac_id" ] && [ "$oac_id" != "None" ] || err "Could not create or find OAC."
  echo "$oac_id"
}

# --- Step 3: CloudFront Function (URL rewrite) ---
step3() {
  log "Step 3: Publish CloudFront Function ($CF_FUNCTION_NAME)" >&2
  [ -f "$CF_FUNCTION_FILE" ] || err "Missing CloudFront function source: $CF_FUNCTION_FILE"
  local fn_code etag fn_arn
  fn_code=$(base64 -w 0 "$CF_FUNCTION_FILE" 2>/dev/null || base64 "$CF_FUNCTION_FILE" | tr -d '\n')

  if aws cloudfront describe-function --name "$CF_FUNCTION_NAME" --profile "$AWS_PROFILE" >/dev/null 2>&1; then
    etag=$(aws cloudfront describe-function --name "$CF_FUNCTION_NAME" --profile "$AWS_PROFILE" \
      --query 'ETag' --output text)
    aws cloudfront update-function --name "$CF_FUNCTION_NAME" --profile "$AWS_PROFILE" \
      --function-config '{"Comment":"NexusAI docs URL rewrite","Runtime":"cloudfront-js-2.0"}' \
      --function-code "$fn_code" --if-match "$etag" >/dev/null
    log "Updated CloudFront Function." >&2
  else
    aws cloudfront create-function --name "$CF_FUNCTION_NAME" --profile "$AWS_PROFILE" \
      --function-config '{"Comment":"NexusAI docs URL rewrite","Runtime":"cloudfront-js-2.0"}' \
      --function-code "$fn_code" >/dev/null
    log "Created CloudFront Function." >&2
  fi

  etag=$(aws cloudfront describe-function --name "$CF_FUNCTION_NAME" --profile "$AWS_PROFILE" \
    --query 'ETag' --output text)
  fn_arn=$(aws cloudfront publish-function --name "$CF_FUNCTION_NAME" --if-match "$etag" \
    --profile "$AWS_PROFILE" --query 'FunctionSummary.FunctionMetadata.FunctionARN' --output text)
  log "Published CloudFront Function: $fn_arn" >&2
  echo "$fn_arn"
}

# --- Step 4: CloudFront distribution ---
step4() {
  local oac_id="$1" fn_arn="$2"
  log "Step 4: Create CloudFront distribution"

  local origin_domain="${BUCKET}.s3.${AWS_REGION}.amazonaws.com"
  local existing_id
  existing_id=$(aws cloudfront list-distributions --profile "$AWS_PROFILE" \
    --query "DistributionList.Items[?Origins.Items[0].DomainName=='$origin_domain'].Id | [0]" \
    --output text 2>/dev/null)

  if [ -n "$existing_id" ] && [ "$existing_id" != "None" ] && [ "$existing_id" != "null" ]; then
    DIST_ID="$existing_id"
    DOMAIN=$(aws cloudfront get-distribution --id "$DIST_ID" --profile "$AWS_PROFILE" \
      --query 'Distribution.DomainName' --output text)
    DIST_ARN="arn:aws:cloudfront::$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text):distribution/$DIST_ID"
    warn "Distribution $DIST_ID already exists ($DOMAIN), updating function association."
    attach_function_to_distribution "$fn_arn"
    log "Step 4 done."
    return
  fi

  local caller_ref="nexusai-docs-$(date +%s)"
  local dist_config
  dist_config=$(cat <<DISTJSON
{
  "CallerReference": "$caller_ref",
  "Comment": "NexusAI Docs",
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
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "FunctionAssociations": {
      "Quantity": 1,
      "Items": [{ "EventType": "viewer-request", "FunctionARN": "$fn_arn" }]
    }
  }
}
DISTJSON
  )

  local dist_out
  dist_out=$(aws cloudfront create-distribution --profile "$AWS_PROFILE" \
    --distribution-config "$dist_config" 2>&1) || err "Create distribution failed: $dist_out"
  DIST_ID=$(echo "$dist_out" | jq -r '.Distribution.Id')
  DIST_ARN=$(echo "$dist_out" | jq -r '.Distribution.ARN')
  DOMAIN=$(echo "$dist_out" | jq -r '.Distribution.DomainName')
  log "Distribution ID: $DIST_ID  Domain: $DOMAIN"
  log "Step 4 done."
}

attach_function_to_distribution() {
  local fn_arn="$1"
  local config_file="/tmp/cf-config-$$.json"
  local full_cfg etag
  full_cfg=$(aws cloudfront get-distribution-config --id "$DIST_ID" --profile "$AWS_PROFILE")
  etag=$(echo "$full_cfg" | jq -r '.ETag')
  echo "$full_cfg" | jq --arg arn "$fn_arn" '
    .DistributionConfig
    | .DefaultCacheBehavior.FunctionAssociations = {
        "Quantity": 1,
        "Items": [{"EventType": "viewer-request", "FunctionARN": $arn}]
      }
    | .DefaultCacheBehavior.LambdaFunctionAssociations = { "Quantity": 0 }
    | .CustomErrorResponses = {"Quantity": 0}
  ' > "$config_file"
  aws cloudfront update-distribution --id "$DIST_ID" --distribution-config "file://$config_file" \
    --if-match "$etag" --profile "$AWS_PROFILE" >/dev/null
  rm -f "$config_file"
}

# --- Step 5: S3 bucket policy (CloudFront-only access) ---
step5() {
  local dist_arn="$1"
  log "Step 5: Attach S3 bucket policy (CloudFront only)"
  local bucket_arn="arn:aws:s3:::${BUCKET}"
  local policy='{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "AllowCloudFrontServicePrincipalReadOnly",
      "Effect": "Allow",
      "Principal": { "Service": "cloudfront.amazonaws.com" },
      "Action": "s3:GetObject",
      "Resource": "'"$bucket_arn"'/*",
      "Condition": { "StringEquals": { "AWS:SourceArn": "'"$dist_arn"'" } }
    }]
  }'
  aws s3api put-bucket-policy --bucket "$BUCKET" --profile "$AWS_PROFILE" --policy "$policy"
  log "Step 5 done."
}

# --- Step 6: Persist outputs to .env.local ---
step6() {
  log "Step 6: Write outputs back to $ENV_FILE"
  upsert_env "DOCS_CLOUDFRONT_ID" "$DIST_ID"
  upsert_env "DOCS_CLOUDFRONT_DOMAIN" "$DOMAIN"
  log "Step 6 done."
}

summary() {
  echo
  echo -e "${BLUE}=== NexusAI Docs Setup Complete ===${NC}"
  echo
  echo "DOCS_S3_BUCKET         = $BUCKET"
  echo "DOCS_CLOUDFRONT_ID     = $DIST_ID"
  echo "DOCS_CLOUDFRONT_DOMAIN = $DOMAIN"
  echo
  echo "Public URL: https://$DOMAIN"
  echo
  echo -e "${YELLOW}Next steps:${NC}"
  echo "  1. CloudFront takes ~5-15 minutes to fully deploy on first creation."
  echo "  2. Run ./update-website.sh to build MkDocs and publish content."
}

main() {
  aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1 \
    || err "AWS profile '$AWS_PROFILE' not valid. Set AWS_PROFILE in .env.local or run aws configure."
  command -v jq >/dev/null 2>&1 || err "jq is required. Install with: apt-get install jq / brew install jq"

  step1
  OAC_ID=$(step2)
  FN_ARN=$(step3)
  step4 "$OAC_ID" "$FN_ARN"
  step5 "$DIST_ARN"
  step6
  summary
}

main "$@"
