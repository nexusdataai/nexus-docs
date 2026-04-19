# StarHub Docs GitHub Actions

| Secret Name         | Value |
|---------------------|-------|
| AWS_ROLE_TO_ASSUME  | arn:aws:iam::764119721991:role/GitHubActions-starhub-docs-main |
| DOCS_S3_BUCKET     | totogi-callsense-doc |
| DOCS_CLOUDFRONT_ID | E15B2077ZA0NR4 |

Docs deploy on push to `main`; build runs `mkdocs build`, syncs `site/` to S3, invalidates CloudFront.
