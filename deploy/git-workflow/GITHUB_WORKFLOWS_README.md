# StarHub Docs GitHub Actions

GitHub Actions deploy the MkDocs documentation site to S3 (`totogi-callsense-doc`) and CloudFront. Access is protected by HTTP Basic Auth (Lambda@Edge).

## Workflow

- **File:** `.github/workflows/docs.yml`
- **Trigger:** Push to `main` (and PR for build-only).
- **Steps:** Checkout → Python + pip install → `mkdocs build` → Configure AWS (OIDC) → `aws s3 sync site/` → CloudFront invalidation.

## GitHub Secrets

Go to: `https://github.com/YOUR_ORG/starhub-docs/settings/secrets/actions`

| Secret               | Description |
|----------------------|-------------|
| `AWS_ROLE_TO_ASSUME` | IAM role ARN from `deploy/git-workflow/setup-github-integration.sh` |
| `DOCS_S3_BUCKET`     | S3 bucket name, e.g. `totogi-callsense-doc` |
| `DOCS_CLOUDFRONT_ID`| CloudFront distribution ID (from `deploy/setup-website.sh` or Console) |

## One-time AWS setup

1. **Infrastructure:** Run `deploy/setup-website.sh` to create S3 bucket, OAC, CloudFront, Lambda@Edge (Basic Auth), and bucket policy. It prints the distribution ID for `DOCS_CLOUDFRONT_ID`.
2. **IAM role for GitHub:** Run `deploy/git-workflow/setup-github-integration.sh` to create the OIDC role and get `AWS_ROLE_TO_ASSUME`.
3. Add the three secrets above in the repo.

## Local build

```bash
pip install -r requirements.txt
mkdocs build
# Output in site/
```

## Disable GitHub Pages

In repo **Settings → Pages**, set **Source** to **None** so the docs are only served from CloudFront (no public GitHub Pages URL).
