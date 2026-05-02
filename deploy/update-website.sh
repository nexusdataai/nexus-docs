#!/usr/bin/env bash
# update-website.sh - Build NexusAI MkDocs site and publish to S3 + CloudFront.
#
# Reads DOCS_S3_BUCKET, DOCS_CLOUDFRONT_ID, AWS_PROFILE and AWS_REGION from
# ./.env.local (created by setup-website.sh). Runs:
#   1. mkdocs build (in the parent docs repo)
#   2. aws s3 sync site/ s3://$DOCS_S3_BUCKET --delete
#   3. CloudFront invalidation for /*
#
# Re-run any time docs change. Idempotent.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.local"
SITE_DIR="$DOCS_ROOT/site"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
log()  { echo -e "${GREEN}[update-website]${NC} $*"; }
warn() { echo -e "${YELLOW}[update-website]${NC} $*"; }
err()  { echo -e "${RED}[update-website]${NC} $*"; exit 1; }

# --- Load .env.local ---
[ -f "$ENV_FILE" ] || err "$ENV_FILE not found. Run setup-website.sh first."
# shellcheck disable=SC1090
set -a; source "$ENV_FILE"; set +a

[ -n "${DOCS_S3_BUCKET:-}" ]     || err "DOCS_S3_BUCKET missing in $ENV_FILE"
[ -n "${DOCS_CLOUDFRONT_ID:-}" ] || err "DOCS_CLOUDFRONT_ID missing in $ENV_FILE (run setup-website.sh)"
AWS_PROFILE="${AWS_PROFILE:-default}"
AWS_REGION="${AWS_REGION:-us-east-1}"
SKIP_BUILD="${SKIP_BUILD:-0}"
SKIP_INVALIDATION="${SKIP_INVALIDATION:-0}"

aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1 \
  || err "AWS profile '$AWS_PROFILE' not valid."

# --- Step 1: mkdocs build ---
build_site() {
  if [ "$SKIP_BUILD" = "1" ]; then
    warn "SKIP_BUILD=1 - skipping mkdocs build"
    [ -d "$SITE_DIR" ] || err "$SITE_DIR does not exist; cannot skip build."
    return
  fi
  log "Step 1: mkdocs build (in $DOCS_ROOT)"
  if command -v mkdocs >/dev/null 2>&1; then
    (cd "$DOCS_ROOT" && mkdocs build -q)
  elif python3 -c "import mkdocs" >/dev/null 2>&1; then
    (cd "$DOCS_ROOT" && python3 -m mkdocs build -q)
  else
    err "mkdocs not installed. pip install -r requirements.txt"
  fi
  [ -d "$SITE_DIR" ] || err "Build did not produce $SITE_DIR"
}

# --- Step 2: sync to S3 ---
sync_to_s3() {
  log "Step 2: Sync $SITE_DIR/ -> s3://$DOCS_S3_BUCKET (with --delete)"
  aws s3 sync "$SITE_DIR/" "s3://$DOCS_S3_BUCKET/" \
    --delete \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --exclude '*.DS_Store'
}

# --- Step 3: CloudFront invalidation ---
invalidate_cloudfront() {
  if [ "$SKIP_INVALIDATION" = "1" ]; then
    warn "SKIP_INVALIDATION=1 - skipping CloudFront invalidation"
    return
  fi
  log "Step 3: CloudFront invalidation /* on $DOCS_CLOUDFRONT_ID"
  local inv_id
  inv_id=$(aws cloudfront create-invalidation \
    --distribution-id "$DOCS_CLOUDFRONT_ID" \
    --paths '/*' \
    --profile "$AWS_PROFILE" \
    --query 'Invalidation.Id' --output text)
  log "Invalidation submitted: $inv_id"
  log "(Typical completion: 30-90 seconds. Check with: aws cloudfront get-invalidation --distribution-id $DOCS_CLOUDFRONT_ID --id $inv_id)"
}

summary() {
  echo
  echo -e "${BLUE}=== NexusAI Docs Update Complete ===${NC}"
  if [ -n "${DOCS_CLOUDFRONT_DOMAIN:-}" ]; then
    echo "Public URL: https://$DOCS_CLOUDFRONT_DOMAIN"
  fi
}

build_site
sync_to_s3
invalidate_cloudfront
summary
