# Totogi CallSense Platform

Welcome to the comprehensive documentation portal for the **Totogi CallSense Platform** - an enterprise-grade AI-powered call processing and analytics platform for Webex Contact Center.

---

## Executive Summary

Totogi provides **two primary enterprise applications** designed to transform telecommunications operations:

### 1. **Totogi CallSense Platform** - AI-Powered Call Analytics

An enterprise-grade AI-powered call processing and analytics platform that delivers:

- **100% automated QA coverage** of all calls (vs. 30% manual coverage)
- **Real-time AI insights** on sentiment, compliance, and performance
- **12.5-15% conversion rate improvement** from current 8-10% baseline
- **50% reduction** in manager time spent on manual QA
- **Multi-million dollar revenue impact** with measurable ROI of 25-55x

**Key Capabilities:**
- AI transcription and diarization
- Automated quality assurance and compliance monitoring
- Real-time sentiment analysis and coaching recommendations
- Product recommendation engine
- Automatic quote generation
- Salesforce and Office 365 integration

### 2. **Totogi Toolkit** - Self-Service Deployment Platform

An enterprise-grade self-service deployment toolkit that enables:

- **One-click AWS infrastructure deployment** via guided wizard
- **CloudFormation-based** infrastructure as code
- **License-controlled capability deployment**
- **Desktop (Electron), PWA, and web** deployment options
- **Complete infrastructure provisioning** (VPC, ECS, S3, DynamoDB, CloudFront, Cognito)

**Key Features:**
- Wizard-driven deployment flow
- AWS credential and permission validation
- Multi-capability architecture selection
- Post-deployment health verification
- Installation history and management

Together, these applications enable enterprises to rapidly deploy and operate AI-powered call analytics at scale.

---

## Overview

The Totogi CallSense Platform is a sophisticated platform that enables organizations to:

- **Process Webex CC Calls** - Fetch, transcribe, and analyze calls from Webex Contact Center
- **Manage Transformation Journeys** - Orchestrate multi-stage processing workflows
- **Provide AI Analytics** - Leverage OpenAI for intelligent call analysis and insights
- **Automate CRM Actions** - Create and manage Salesforce leads and opportunities based on call analysis
- **Enable Real-time Monitoring** - Comprehensive logging, reporting, and dashboards

---

For detailed architecture diagrams and technical design, see the [Platform Architecture](platform-architecture.md) page.

---

## Documentation Categories

### 📊 [Business Documentation](business/)
Executive summaries, business requirements, and business cases that define the strategic value and objectives of the platform.

**Key Documents:**
- Executive Summary
- Business Requirements
- Business Case Analysis

---

### 📋 [Functional Specifications](functional/)
Product requirements documents (PRD) and functional specifications that detail what the platform does and how it meets business needs.

**Key Documents:**
- Design Specifications
- Functional Requirements
- Task Definitions

---

### 🚀 [Features & Capabilities](features/)
Detailed documentation on platform capabilities, feature architecture, and telco AI capabilities.

**Key Documents:**
- Capability Architecture
- Telco AI FAQ
- AWS Well-Architected Framework Compliance

---

### 📅 [Project Scope](project-scope/)
Project scope definitions, release notes, and project metadata tracking the evolution of the platform.

**Key Documents:**
- Release Notes
- Project Metadata
- Scope Definitions

---

### 🏗️ [Technical Documentation](technical/)
In-depth technical documentation covering solution architecture, infrastructure requirements, integration guides, and system design.

**Key Documents:**
- Solution Architecture
- Infrastructure Requirements
- Webex Integration Guide
- Database Design
- Gateway Architecture

---

### ⚙️ [Operational Documentation](operational/)
Deployment guides, AWS configuration, troubleshooting, and operational procedures for running the platform.

**Key Documents:**
- Getting Started Guide
- Installation Instructions
- Deployment Wizard
- AWS Configuration
- Troubleshooting & FAQ
- Quick Reference

---

### 👨‍💻 [Developer Guide](developer/)
Development guides, API documentation, testing procedures, and setup instructions for developers working on the platform.

**Key Documents:**
- Backend Development Guide
- LocalStack Setup
- API Documentation
- MCP Tools
- Testing Guides

---

## Quick Links

| Category | Quick Access |
|----------|-------------|
| 🎯 **Get Started** | [Installation Guide](operational/index.md) → [Getting Started](operational/user-guide/01-getting-started.md) |
| 🏗️ **Architecture** | [Solution Architecture](technical/solution-architecture.md) → [Technical Docs](technical/) |
| 👨‍💻 **Developers** | [Backend README](developer/backend/README.md) → [Developer Guide](developer/) |
| 📊 **Business** | [Executive Summary](business/source/executive-summary.md) → [Business Docs](business/) |

---

## Repository Structure

The Totogi CallSense Platform consists of multiple repositories:

- **starhub-backend** - Backend services and API
- **starhub-ui** - React-based frontend application
- **starhub-deployer** - AWS deployment automation
- **starhub-docs** - This documentation site
- **project-notes** - Project metadata and notes

---

## Key Features

✅ **Call Processing** - Automated processing of Webex CC call recordings  
✅ **AI Transcription** - Speech-to-text powered by OpenAI  
✅ **AI Analysis** - GPT-powered call analysis and insights  
✅ **Salesforce CRM Integration** - Automated lead creation and opportunity management  
✅ **Journey Management** - Multi-stage processing workflows  
✅ **Real-time Analytics** - Performance metrics and comprehensive reporting  
✅ **WXCC Simulator** - Built-in simulator for testing  
✅ **MCP Integration** - Model Context Protocol tools  
✅ **License Management** - Enterprise licensing and feature gating  

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI
- **Frontend**: React, TypeScript
- **Cloud**: AWS (ECS, DynamoDB, S3, Lambda, Glue)
- **AI**: OpenAI GPT-4
- **Infrastructure**: Terraform, Docker
- **Development**: LocalStack for local testing

---

## Getting Help

- 📖 Browse the documentation categories above
- 🔍 Use the search function to find specific topics
- ❓ Check the [FAQ](operational/user-guide/07-faq.md)
- 🐛 See [Troubleshooting](operational/user-guide/06-troubleshooting.md)

---

**Version**: 0.0.1
