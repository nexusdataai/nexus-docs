# Starhub Trilogy Documentation

Centralized documentation site for the Starhub Trilogy project built with MkDocs Material.

## Overview

This repository hosts a comprehensive documentation portal that organizes all documentation across the Starhub Trilogy project into logical categories. The documentation site provides a single access point to all project documentation while keeping source documents in their original locations.

## Documentation Structure

The documentation is organized into 7 main categories:

1. **Business Documentation** - Executive summaries, business requirements, and business cases
2. **Functional Specifications** - Product requirements and functional specifications
3. **Features & Capabilities** - Capability architecture and feature documentation
4. **Project Scope** - Release notes and project metadata
5. **Technical Documentation** - Architecture, infrastructure, and integration guides
6. **Operational Documentation** - Deployment guides, configuration, and troubleshooting
7. **Developer Guide** - Development setup, API documentation, and testing guides

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Local Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Serve documentation locally
mkdocs serve

# Open browser to http://127.0.0.1:8000
```

### Building the Site

```bash
# Build static site
mkdocs build

# Output will be in site/ directory
```

## Deployment

The documentation site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch.

### GitHub Pages Setup

1. Enable GitHub Pages in repository settings
2. Set source to `gh-pages` branch
3. Push to main branch to trigger deployment

The workflow (`.github/workflows/docs.yml`) handles:
- Installing dependencies
- Building the documentation
- Deploying to gh-pages branch

## Project Structure

```
starhub-docs/
├── docs/                      # Documentation content
│   ├── index.md              # Landing page
│   ├── business/             # Business documentation
│   │   └── index.md
│   ├── functional/           # Functional specifications
│   │   └── index.md
│   ├── features/             # Features & capabilities
│   │   └── index.md
│   ├── project-scope/        # Project scope & releases
│   │   └── index.md
│   ├── technical/            # Technical documentation
│   │   └── index.md
│   ├── operational/          # Operational guides
│   │   └── index.md
│   └── developer/            # Developer documentation
│       └── index.md
├── .github/
│   └── workflows/
│       └── docs.yml          # GitHub Actions workflow
├── mkdocs.yml                # MkDocs configuration
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Configuration

The site configuration is in `mkdocs.yml`:

- **Theme**: Material for MkDocs with dark/light mode
- **Features**: Navigation tabs, search, code highlighting, mermaid diagrams
- **Plugins**: Search, git-revision-date-localized

## Contributing

1. Create a feature branch
2. Make your changes to documentation
3. Test locally with `mkdocs serve`
4. Commit and push changes
5. Create pull request

## Links to Source Repositories

The Starhub Trilogy consists of multiple repositories:

- **starhub-backend** - Backend services and API
- **starhub-ui** - React-based frontend application
- **starhub-deployer** - AWS deployment automation
- **starhub-docs** - This documentation site
- **project-notes** - Project metadata and notes

## Features

✅ Single access point for all documentation  
✅ Modern Material Design theme  
✅ Dark/light mode toggle  
✅ Full-text search functionality  
✅ Mobile responsive design  
✅ Mermaid diagram support  
✅ Automatic deployment to GitHub Pages  
✅ Git revision dates on pages  

## Accessing the Documentation

- **Local**: http://127.0.0.1:8000 (when running `mkdocs serve`)
- **Production**: https://yourusername.github.io/starhub-docs/ (replace with actual URL)

## Support

For issues or questions:
- Check the [FAQ](docs/operational/index.md)
- Review existing documentation
- Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Status**: Active
